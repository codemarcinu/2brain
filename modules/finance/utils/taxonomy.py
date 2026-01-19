import json
from pathlib import Path
from typing import Tuple, Dict, Optional, Any
from rapidfuzz import process, fuzz
from config import config
from shared.logging import get_logger

logger = get_logger("TaxonomyGuard")

class TaxonomyGuard:
    ALLOWED_UNITS = {"szt", "kg", "g", "l", "ml", "opakowanie"}
    UNIT_MAPPING = {"szt.": "szt", "kg.": "kg", "gram": "g", "litr": "l"}

    def __init__(self, json_path: Optional[str] = None):
        self.json_path = Path(json_path) if json_path else config.taxonomy_path
        self.data = self._load_data()
        self.ocr_map = {}
        self.canonical_products = set()
        self._build_indexes()
        # Lazily loaded brain to avoid circular imports if possible, or just init here if adapter is ready
        # For now, we will pass the brain or adapter when calling methods involving LLM if needed, 
        # or instantiate a lightweight adapter.

    def _load_data(self) -> Dict:
        if not self.json_path.exists():
            return {"mappings": [], "categories": {}}
        try:
            with open(self.json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load taxonomy: {e}")
            return {"mappings": [], "categories": {}}

    def _build_indexes(self):
        self.categories = set(self.data.get("categories", {}).keys())
        for m in self.data.get("mappings", []):
            ocr_key = m['ocr'].strip().upper()
            self.ocr_map[ocr_key] = {
                "name": m['name'], "cat": m['cat'],
                "unit": self.normalize_unit(m.get('unit', 'szt'))
            }
            self.canonical_products.add(m['name'])
        self.ocr_patterns = list(self.ocr_map.keys())

    def normalize_unit(self, unit: str) -> str:
        u = unit.lower().strip().replace(" ", "")
        return self.UNIT_MAPPING.get(u, u if u in self.ALLOWED_UNITS else "szt")

    def normalize_product(self, ocr_name: str, shop: str = "Sklep") -> Tuple[str, str, str]:
        ocr_clean = ocr_name.strip().upper()
        
        # 1. Exact match
        if ocr_clean in self.ocr_map:
            meta = self.ocr_map[ocr_clean]
            return meta['name'], meta['cat'], self.normalize_unit(meta['unit'])
        
        # 2. Fuzzy match
        if self.ocr_patterns:
            match = process.extractOne(ocr_clean, self.ocr_patterns, scorer=fuzz.token_sort_ratio)
            if match and match[1] >= 92:
                meta = self.ocr_map[match[0]]
                return meta['name'], meta['cat'], self.normalize_unit(meta['unit'])
            
        # 3. Fallback (if no AI available here yet, return capitalized)
        # The calling pipeline usually handles the AI fallback if this returns generic results
        # But if we want to integrate AI normalization here we can.
        # For now, let's return a "best effort" which acts as a signal to the pipeline 
        # that it might need AI if confidence is low, but this method signature doesn't return confidence.
        
        # In the referenced design, `_llm_normalize_with_context` was here. 
        # We will skip direct LLM call here to keep TaxonomyGuard synchronous and fast, 
        # and let the AsyncPipeline decide when to call LLM for full receipt or line items.
        # However, if we process a single line that missed cache/fuzzy, we might want AI.
        
        return ocr_name.title(), "INNE", "szt"

