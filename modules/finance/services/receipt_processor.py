"""
Receipt Processor
Handles OCR, caching, and LLM extraction for receipts.
"""
import json
import logging
from pathlib import Path
from typing import Dict, Optional, List
import pytesseract
from PIL import Image
from thefuzz import process as fuzz_process
from shared.logging import get_logger
from config import config

logger = get_logger(__name__)

class ReceiptProcessor:
    """Core logic for receipt processing"""

    def __init__(self):
        self.cache = self._load_cache()

    def _load_cache(self) -> Dict[str, str]:
        """Load product category cache from disk"""
        if config.product_cache_path.exists():
            try:
                with open(config.product_cache_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error("cache_load_failed", error=str(e))
                return {}
        return {}

    def _save_cache(self):
        """Save cache to disk"""
        try:
            with open(config.product_cache_path, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error("cache_save_failed", error=str(e))

    def process_image(self, image_path: Path) -> Dict:
        """
        Full pipeline: Image -> OCR -> Data Extraction
        """
        logger.info("receipt_processing_started", file=image_path.name)
        
        # 1. OCR
        text = self._perform_ocr(image_path)
        if not text:
            return {"error": "OCR failed (empty text)"}
            
        logger.debug("ocr_completed", text_length=len(text))
        
        # 2. Extract Data (Rule-based + Cache + LLM)
        data = self._extract_data(text)
        
        return data

    def _perform_ocr(self, image_path: Path) -> str:
        """Run Tesseract OCR on image"""
        try:
            image = Image.open(image_path)
            # Basic preprocessing could be added here (contrast, greyscale)
            text = pytesseract.image_to_string(image, lang=config.ocr_lang)
            return text.strip()
        except Exception as e:
            logger.error("ocr_failed", error=str(e))
            return ""

    def _extract_data(self, text: str) -> Dict:
        """
        Extract structured data from text using LLM.
        """
        from openai import OpenAI
        
        # Configure client for Ollama
        client = OpenAI(
            base_url=f"{config.base.ollama_host}/v1",
            api_key="ollama"  # required but unused
        )
        
        prompt = f"""
        Extract receipt data from the following OCR text into JSON format.
        Return ONLY the JSON object, no markdown, no thinking.
        
        Required fields:
        - merchant (string): Name of the store
        - date (string): YYYY-MM-DD
        - total (number): Total amount
        - currency (string): e.g. "PLN"
        - items (list of objects): {{ "name": "product name", "price": number, "category": "category_name" }}
        
        For "category", try to guess one of: Grocery, Transport, Eating Out, Bills, Entertainment, Other.
        Use "Other" if unsure.
        
        OCR Text:
        {text}
        """
        
        try:
            response = client.chat.completions.create(
                model=config.llm_model,
                messages=[
                    {"role": "system", "content": "You are a receipt data extraction assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )
            
            content = response.choices[0].message.content
            # Clean up potential markdown code blocks
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
                
            data = json.loads(content.strip())
            return data
            
        except Exception as e:
            logger.error("llm_extraction_failed", error=str(e))
            # Return raw text fallback
            return {
                "raw_text": text,
                "merchant": "Unknown",
                "date": None,
                "total": 0.0,
                "items": [],
                "error": str(e)
            }

    def _lookup_category(self, product_name: str) -> Optional[str]:
        """Fuzzy match product name in cache"""
        # Exact match
        if product_name in self.cache:
            return self.cache[product_name]
            
        # Fuzzy match
        keys = list(self.cache.keys())
        if not keys:
            return None
            
        match, score = fuzz_process.extractOne(product_name, keys)
        if score > 85: # High confidence threshold
            return self.cache[match]
            
        return None
