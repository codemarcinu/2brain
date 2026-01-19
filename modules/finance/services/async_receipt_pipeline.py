"""
Async Receipt Processing Pipeline
Orchestrates caching, fuzzy matching, and AI fallback for fast receipt processing.
"""
import asyncio
import re
import json
import time
from typing import List, Dict, Optional, Any, Tuple
from concurrent.futures import ThreadPoolExecutor
from rapidfuzz import process, fuzz

from shared.logging import get_logger
from config import config
from utils.receipt_cache import ReceiptCache, ProductMatch
from utils.taxonomy import TaxonomyGuard
from adapters.llm_adapter import LLMAdapter
from utils.receipt_agents import detect_shop, get_agent

logger = get_logger("AsyncReceiptPipeline")

class AsyncReceiptPipeline:
    def __init__(self):
        self.cache = ReceiptCache()
        self.brain = LLMAdapter()
        self.taxonomy = TaxonomyGuard()
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.processing_times: List[float] = []
        logger.info("async_pipeline_initialized")

    async def process_receipt_async(
        self,
        ocr_text: str,
        shop: Optional[str] = None
    ) -> Dict[str, Any]:
        """Main async entry point for receipt processing."""
        start_time = time.time()

        if not ocr_text or not ocr_text.strip():
            logger.error("empty_ocr_text")
            return {"error": "OCR text is empty"}

        # Stage 0: Shop detection & preprocessing
        if shop is None:
            shop = detect_shop(ocr_text)

        agent = get_agent(shop)
        cleaned_ocr = agent.preprocess(ocr_text)
        lines = [l.strip() for l in cleaned_ocr.split('\n') if l.strip()]

        logger.info("processing_lines", count=len(lines), shop=shop)

        # Stage 1: Cache lookup (Tier 1)
        cached_items = []
        cache_misses = []

        for line in lines:
            cached = self.cache.lookup(line, shop)
            if cached:
                cached_items.append((line, cached))
            else:
                cache_misses.append(line)

        cache_hit_rate = len(cached_items) / len(lines) if lines else 0
        logger.debug("cache_stats", hit_rate=cache_hit_rate, misses=len(cache_misses))
        
        # Stage 2: Parallel fuzzy matching for cache misses (Tier 2)
        fuzzy_matches = []
        if cache_misses:
            fuzzy_matches = await self._fuzzy_match_batch(cache_misses)

        # Stage 3: Combine cached + fuzzy results
        all_items = []

        # Add cached items
        for line, match in cached_items:
            all_items.append(self._match_to_item(line, match))

        # Add fuzzy matched items
        for line, match_tuple in zip(cache_misses, fuzzy_matches):
            if match_tuple and match_tuple[1] >= 70:  # Accept 70%+ similarity
                # match_tuple is (matched_string, score, index)
                matched_ocr_key = match_tuple[0]
                meta = self.taxonomy.ocr_map.get(matched_ocr_key)
                
                if meta:
                    category = meta['cat'].upper() if meta['cat'] else 'INNE'
                    product_match = ProductMatch(
                        name=meta['name'],
                        category=category,
                        unit=meta['unit'],
                        confidence=match_tuple[1] / 100.0,
                        source="fuzzy"
                    )
                    all_items.append(self._match_to_item(line, product_match))
                    # Update cache so next time it's faster
                    self.cache.update(line, product_match, shop)

        # Stage 4: AI processing (only if needed)
        needs_ai = self._needs_ai_processing(all_items, len(lines), cache_hit_rate)
        used_ai = False

        if needs_ai:
            logger.info("invoking_ai_fallback", reason="low_coverage_or_hits")
            used_ai = True
            try:
                ai_result = await self._ai_process_async(ocr_text, shop, timeout=120.0)
                if ai_result and 'items' in ai_result:
                    # If AI returns items, we prefer them or merge them?
                    # Strategy: If AI was called, it likely sees the whole context better.
                    # We can replace the items list with AI result, OR only fill gaps.
                    # The user's code replaced `all_items = ai_result['items']`.
                    # Let's follow that but also learn from it.
                    all_items = ai_result['items']
                    self._update_cache_from_ai(ai_result['items'], shop)
            except asyncio.TimeoutError:
                logger.warning("ai_timeout_fallback_fuzzy")
            except Exception as e:
                logger.error("ai_processing_failed", error=str(e))

        # Stage 5: Extract metadata
        receipt_date = self._extract_date(ocr_text, shop)
        total_amount = sum(float(item.get('suma', 0)) for item in all_items)

        if len(cached_items) + len(cache_misses) > 0:
            self.cache.save()

        elapsed = time.time() - start_time
        self.processing_times.append(elapsed)
        
        logger.info("pipeline_completed", elapsed=elapsed, items=len(all_items), ai=used_ai)

        return {
            'items': all_items,
            'date': receipt_date,
            'total_amount': total_amount,
            'shop': shop,
            'stats': {
                'processing_time': elapsed,
                'cache_hit_rate': cache_hit_rate,
                'used_ai': used_ai,
                'items_count': len(all_items)
            }
        }

    async def _fuzzy_match_batch(self, lines: List[str]) -> List[Optional[Tuple]]:
        """Parallel fuzzy matching using ThreadPoolExecutor."""
        if not lines or not self.taxonomy.ocr_patterns:
            return [None] * len(lines)
            
        # Small optimization: for small batches, just run sync
        if len(lines) < 15:
            return [self._fuzzy_match_single(line) for line in lines]

        loop = asyncio.get_event_loop()
        tasks = [
            loop.run_in_executor(self.executor, self._fuzzy_match_single, line)
            for line in lines
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return [r if not isinstance(r, Exception) else None for r in results]

    def _fuzzy_match_single(self, line: str) -> Optional[Tuple]:
        try:
            # partial_ratio because OCR line might have extra garbage like prices
            return process.extractOne(
                line.upper(),
                self.taxonomy.ocr_patterns,
                scorer=fuzz.partial_ratio
            )
        except Exception:
            return None

    async def _ai_process_async(self, ocr_text: str, shop: str, timeout: float = 120.0) -> Optional[Dict]:
        """Async AI processing with timeout."""
        system_prompt = self._build_system_prompt(shop)
        user_prompt = self._build_user_prompt(ocr_text, shop)

        try:
            response = await asyncio.wait_for(
                self.brain.generate_content_async(
                    user_prompt,
                    system_prompt,
                    "json"
                ),
                timeout=timeout
            )

            if response:
                cleaned = self._clean_json_response(response)
                try:
                    return json.loads(cleaned)
                except json.JSONDecodeError:
                    # Try to find JSON block
                    match = re.search(r'\{.*\}', cleaned, re.DOTALL)
                    if match:
                        return json.loads(match.group(0))
        except Exception as e:
            logger.error("ai_parsing_error", error=str(e))
        return None

    def _clean_json_response(self, text: str) -> str:
        text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
        # Look for markdown json block
        match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
        if match:
            return match.group(1)
        # Or just array/object
        return text.strip()

    def _build_system_prompt(self, shop: str) -> str:
        return f"""# System Role
You are an expert data analyst specializing in structured data extraction from Polish receipts.
Extract transaction details and line items from the receipt OCR text into a strict JSON format.
Output Schema:
{{
  "shop": "{shop}",
  "date": "YYYY-MM-DD",
  "total_amount": 0.00,
  "items": [
    {{ "nazwa": "string", "kategoria": "enum", "jednostka": "string", "ilosc": 1.0, "cena_jedn": 0.00, "suma": 0.00 }}
  ]
}}
Kategorie: SPOŻYWCZE, CHEMIA, DOM, ALKOHOL, INNE.
"""

    def _build_user_prompt(self, ocr_text: str, shop: str) -> str:
        return f"""Shop: {shop}\nOCR Content:\n```text\n{ocr_text[:12000]}\n```"""

    def _match_to_item(self, line: str, match: ProductMatch) -> Dict:
        # Extract price/qty logic (simplified regex)
        # 12,99 or 12.99
        price_pattern = r'(\d+[.,]\d{2})'
        prices = re.findall(price_pattern, line)
        
        # Heuristic: the last price on line is usually the 'total' for that item
        price = 0.0
        if prices:
            try:
                price = float(prices[-1].replace(',', '.'))
            except ValueError:
                pass
                
        return {
            'nazwa': match.name,
            'kategoria': match.category,
            'jednostka': match.unit,
            'ilosc': 1.0,
            'cena_jedn': price,
            'suma': price
        }

    def _needs_ai_processing(self, items: List[Dict], total_lines: int, cache_hit_rate: float) -> bool:
        if not items and total_lines > 0: return True
        # If we have items but very low coverage compared to line count
        coverage = len(items) / total_lines if total_lines > 0 else 0
        # If coverage is low OR cache hit rate was low (meaning we relied on fuzzy matching heavily or missed a lot)
        # Actually user logic was: coverage < 0.3 or cache_hit_rate < 0.3
        return coverage < 0.3 or cache_hit_rate < 0.3

    def _extract_date(self, text: str, shop: Optional[str] = None) -> Optional[str]:
        if not shop: shop = detect_shop(text)
        agent = get_agent(shop)
        dates = agent.detect_dates(text)
        return dates[0] if dates else None

    def _update_cache_from_ai(self, items: List[Dict], shop: str):
        for item in items:
            raw_name = item.get('nazwa', '')
            if not raw_name: continue
            
            # Normalize via taxonomy (even if AI provides it, we want canonical keys)
            # Actually AI provides "nazwa", we want to map Raw OCR -> Canonical.
            # But here "items" from AI usually implies `nazwa` IS the canonical name or close to it.
            # To update cache properly we need the Raw Line -> Canonical mapping.
            # But the AI result structure loses the "Raw Line" mapping - it just gives structured items.
            # The User's Logic: `self.cache.update(raw_name.upper(), match, shop)`
            # This implies `raw_name` IS the lookup key. 
            # If AI extracted "Mleko", and we save "Mleko" -> "Mleko", that's fine.
            # But real cache power comes from "MLEKO 2% SWIEZE" -> "Mleko".
            # WITHOUT raw line mapping, AI feedback loop is weaker.
            # But we'll follow user implementation: save what AI outputted.
            
            normalized_name, category, unit = self.taxonomy.normalize_product(raw_name, shop)
            match = ProductMatch(
                name=normalized_name, 
                category=category.upper(), 
                unit=unit, 
                confidence=1.0, 
                source="ai"
            )
            # We use raw_name as key. Next time if OCR matches this raw_name, we hit cache.
            self.cache.update(raw_name.upper(), match, shop)
