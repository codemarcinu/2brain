import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List
from dataclasses import dataclass, asdict
from collections import OrderedDict
from pydantic import BaseModel
from shared.logging import get_logger
from config import config

logger = get_logger("ReceiptCache")

@dataclass
class ProductMatch:
    name: str
    category: str
    unit: str
    confidence: float
    source: str = "exact"

    def to_item(self) -> Dict:
        return {
            'nazwa': self.name, 
            'kategoria': self.category,
            'jednostka': self.unit, 
            'ilosc': 1.0, 
            'cena_jedn': 0.0, 
            'rabat': 0.0, 
            'suma': 0.0
        }

class ReceiptCache:
    def __init__(self, cache_file: Optional[Path] = None):
        self.cache_file = cache_file or config.product_cache_path
        self.exact_match: Dict[str, ProductMatch] = {}
        self._lru_cache: OrderedDict[str, ProductMatch] = OrderedDict()
        self._lru_max_size = 500
        self.shop_patterns: Dict[str, List[str]] = {}
        self._load_cache()

    def lookup(self, line: str, shop: str) -> Optional[ProductMatch]:
        line_clean = line.strip().upper()
        if len(line_clean) < 3: return None

        # Tier 1: Exact match
        if line_clean in self.exact_match:
            match = self.exact_match[line_clean]
            match.source = "exact"
            return match

        # Tier 2: LRU fuzzy cache
        cache_key = f"{shop}:{line_clean[:30]}"
        if cache_key in self._lru_cache:
            self._lru_cache.move_to_end(cache_key)
            match = self._lru_cache[cache_key]
            match.source = "lru"
            return match

        # Tier 3: Shop patterns
        if shop in self.shop_patterns:
            for pattern in self.shop_patterns[shop]:
                if pattern in line_clean and pattern in self.exact_match:
                    match = self.exact_match[pattern]
                    match.source = "pattern"
                    return match
        return None

    def update(self, line: str, match: ProductMatch, shop: str):
        line_clean = line.strip().upper()
        if len(line_clean) < 3 or not match.name: return

        self.exact_match[line_clean] = match
        
        cache_key = f"{shop}:{line_clean[:30]}"
        if cache_key in self._lru_cache: 
            self._lru_cache.move_to_end(cache_key)
        else:
            if len(self._lru_cache) >= self._lru_max_size: 
                self._lru_cache.popitem(last=False)
            self._lru_cache[cache_key] = match

        if shop not in self.shop_patterns: 
            self.shop_patterns[shop] = []
        if line_clean not in self.shop_patterns[shop]:
            self.shop_patterns[shop].append(line_clean)

    def save(self):
        try:
            self.cache_file.parent.mkdir(parents=True, exist_ok=True)
            data = {
                'exact': {k: asdict(v) for k, v in self.exact_match.items()},
                'shop_patterns': self.shop_patterns
            }
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Cache save failed: {e}")

    def _load_cache(self):
        if not self.cache_file.exists(): return
        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for line, match_data in data.get('exact', {}).items():
                self.exact_match[line] = ProductMatch(**match_data)
                
            self.shop_patterns = data.get('shop_patterns', {})
        except Exception as e: 
            logger.warning(f"Cache load issue (starting fresh): {e}")

