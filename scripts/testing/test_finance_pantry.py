import pytest
import time
import os
import shutil
from pathlib import Path
from shared.messaging import RedisClient
from shared.config import get_settings
import psycopg2
from psycopg2.extras import RealDictCursor

settings = get_settings()
# Force localhost for Redis when running from host/WSL
settings.redis_host = "localhost"

class TestFinancePantryE2E:
    
    @pytest.fixture
    def redis(self):
        return RedisClient(host=settings.redis_host)
        
    @pytest.fixture
    def inbox_path(self):
        return Path(settings.inbox_path)
        
    @pytest.fixture
    def vault_path(self):
        return Path(settings.obsidian_vault_path)
        
    @pytest.fixture
    def db_conn(self):
        conn = psycopg2.connect(
            host=settings.postgres_host,
            user=settings.postgres_user,
            password=settings.postgres_password,
            database=settings.postgres_db,
            port=settings.postgres_port
        )
        yield conn
        conn.close()

    def test_finance_pipeline(self, redis, inbox_path, db_conn):
        """
        Test: Image -> Inbox -> Collector -> Finance Queue -> DB
        """
        sample_receipt = Path("scripts/testing/test_data/test_receipt.png")
        if not sample_receipt.exists():
            pytest.skip("Sample receipt image missing")
            
        # 1. Copy image to Inbox
        unique_name = f"test_receipt_{int(time.time())}.png"
        dest_path = inbox_path / unique_name
        shutil.copy(sample_receipt, dest_path)
        
        # 2. Wait for processing (max 120s)
        # We check the database for the unique_name
        start_time = time.time()
        found = False
        
        while time.time() - start_time < 120:
            cur = db_conn.cursor(cursor_factory=RealDictCursor)
            cur.execute("SELECT * FROM expenses WHERE source_file = %s", (unique_name,))
            row = cur.fetchone()
            cur.close()
            
            if row:
                found = True
                print(f"\nFound expense in DB: {row['shop_name']} - {row['total_amount']}")
                assert row['total_amount'] > 0
                break
            time.sleep(5)
            
        assert found, "Finance record not found in DB after 120s"

    def test_pantry_flow(self, vault_path):
        """
        Test: Pantry Service -> DB -> Obsidian View
        """
        from modules.pantry.core.services.pantry_service import PantryService
        from modules.pantry.database.repositories.product_repo import ProductRepository
        
        service = PantryService()
        
        # 1. Setup a test product
        repo = ProductRepository()
        test_product_name = f"Test_Milk_{int(time.time())}"
        
        # We need to manually insert or use service if available
        # PantryService doesn't have 'add_product' but it has 'process_receipt'
        
        receipt_data = {
            "shop_name": "TestStore",
            "date": "2023-10-26",
            "total_amount": 42.50,
            "items": [
                {"nazwa": test_product_name, "ilosc": 2.0, "cena": 3.50, "jednostka": "szt"}
            ],
            "source_file": "test_script"
        }
        
        success = service.process_receipt(receipt_data)
        assert success, "Failed to process test receipt in Pantry"
        
        # 2. Consume product
        success = service.consume_product(test_product_name, 1.0)
        assert success, "Failed to consume product"
        
        # 3. Verify Obsidian View
        pantry_file = vault_path / "Spiżarnia.md"
        assert pantry_file.exists(), "Pantry view file missing"
        
        content = pantry_file.read_text(encoding='utf-8')
        assert test_product_name in content, "Test product not found in Spiżarnia.md"
        assert "1.0" in content, "Stock level not updated in view"
