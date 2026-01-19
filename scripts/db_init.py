"""
Database Initialization Script
Sets up the schema for the Obsidian Brain v2 finance module on the external database.
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from shared.config import get_settings
from shared.logging import setup_logging, get_logger
import psycopg2
from psycopg2 import sql

setup_logging(level="INFO", service_name="db_init")
logger = get_logger(__name__)

def init_db():
    settings = get_settings()
    
    logger.info("connecting_to_db", host=settings.postgres_host, db=settings.postgres_db)
    
    try:
        # Use host='localhost' if running from windows while ports are forwarded, 
        # but we are in WSL, so psql01.mikr.us should be direct.
        conn = psycopg2.connect(
            host=settings.postgres_host,
            user=settings.postgres_user,
            password=settings.postgres_password,
            database=settings.postgres_db,
            port=settings.postgres_port
        )
        conn.autocommit = True
        cur = conn.cursor()
        
        # 1. Create expenses table
        logger.info("creating_table_expenses")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id SERIAL PRIMARY KEY,
                shop_name VARCHAR(255),
                total_amount DECIMAL(10, 2),
                purchase_date TIMESTAMP,
                items JSONB,
                verified BOOLEAN DEFAULT FALSE,
                ocr_raw_text TEXT,
                image_path TEXT,
                source_file TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # 2. Add indexes
        cur.execute("CREATE INDEX IF NOT EXISTS idx_expenses_verified ON expenses(verified);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_expenses_purchase_date ON expenses(purchase_date);")
        
        logger.info("db_init_completed_successfully")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        logger.error("db_init_failed", error=str(e))
        sys.exit(1)

if __name__ == "__main__":
    init_db()
