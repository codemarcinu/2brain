import hashlib
from datetime import datetime
from typing import List, Dict, Optional
from modules.pantry.database.repositories.product_repo import ProductRepository
from modules.pantry.adapters.obsidian.view_generator import MarkdownGenerator
from shared.logging import get_logger

logger = get_logger(__name__)

class PantryService:
    def __init__(self, repo: Optional[ProductRepository] = None, 
                 generator: Optional[MarkdownGenerator] = None):
        self.repo = repo or ProductRepository()
        self.generator = generator or MarkdownGenerator()

    def process_receipt(self, receipt_data: Dict) -> bool:
        """Processes receipt data and updates stock & views."""
        shop_name = receipt_data.get('shop_name', 'Nieznany')
        date_str = receipt_data.get('date') or receipt_data.get('purchase_date')
        items = receipt_data.get('items', [])
        total_sum = float(receipt_data.get('total_amount', 0.0))
        
        # Generation unique hash for deduplication
        transaction_date = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else datetime.now().date()
        receipt_fingerprint = f"{transaction_date}|{shop_name}|{total_sum:.2f}"
        receipt_hash = hashlib.sha256(receipt_fingerprint.encode()).hexdigest()

        # Check for duplicates
        if not self.repo.get_unprocessed_receipt_hashes([receipt_hash]):
            logger.info("pantry_receipt_duplicate_skipped", hash=receipt_hash)
            return False

        try:
            self.repo.save_transaction(
                shop_name=shop_name,
                transaction_date=transaction_date,
                total_sum=total_sum,
                receipt_hash=receipt_hash,
                source_file=receipt_data.get('source_file', 'unknown'),
                items_data=items
            )
            # Update views
            self.refresh_views()
            return True
        except Exception as e:
            logger.error("pantry_process_receipt_failed", error=str(e))
            return False

    def consume_product(self, name: str, qty: float) -> bool:
        """Records product consumption and updates views."""
        product = self.repo.get_product_by_name(name)
        if not product:
            logger.warning("consumption_attempt_failed_product_not_found", name=name)
            return False
        
        success = self.repo.add_consumption(product.id, qty, product.jednostka_miary)
        if success:
            logger.info("product_consumed", name=name, qty=qty)
            self.refresh_views()
        return success

    def refresh_views(self) -> None:
        """Updates all Obsidian Markdown files."""
        pantry_data = self.repo.get_pantry_state()
        self.generator.regenerate_pantry_view(pantry_data)
        self.generator.generate_shopping_list(pantry_data)
        logger.info("pantry_views_refreshed")

    def get_shopping_list(self) -> List[Dict]:
        """Returns items below minimum stock."""
        pantry_data = self.repo.get_pantry_state()
        return [p for p in pantry_data if p['stan'] < p['minimum_ilosc']]
