"""
Configuration for Finance Service
"""
from pathlib import Path
from shared.config import get_settings as get_base_settings

class FinanceConfig:
    """Finance specific configuration"""
    
    def __init__(self):
        self.base = get_base_settings()
        
        # Paths
        self.inbox_path = Path(self.base.inbox_path)
        self.receipts_archive_path = Path("./data/receipts_archive") # In container
        
        # Redis
        self.input_queue = "queue:finance"
        
        # OCR
        self.ocr_lang = "pol+eng"
        
        # LLM
        self.llm_model = "deepseek-r1:14b" # Fallback model
        
        # Cache
        self.product_cache_path = Path("./data/product_cache.json")
        
        # Create dirs
        self.receipts_archive_path.mkdir(parents=True, exist_ok=True)

        # AI Provider
        self.receipt_ai_provider = "ollama"
        self.ollama_receipt_model = "deepseek-r1:14b"
        
        # Taxonomy & Cache
        self.taxonomy_path = Path(__file__).parent / "config" / "product_taxonomy.json"
        
        # Ensure config dir exists
        self.taxonomy_path.parent.mkdir(parents=True, exist_ok=True)

config = FinanceConfig()
