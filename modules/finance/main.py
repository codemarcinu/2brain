"""
Finance Service Main Entry Point
"""
import time
import sys
import json
import redis
from pathlib import Path

# Add shared to path if running locally (not needed in docker if installed)
sys.path.append(str(Path(__file__).parent.parent.parent))

from shared.logging import setup_logging, get_logger
from shared.config import get_settings
from services.receipt_processor import ReceiptProcessor
import psycopg2
from psycopg2.extras import Json

setup_logging(
    level="INFO",
    service_name="finance"
)
logger = get_logger(__name__)
settings = get_settings()

def main():
    """Main loop"""
    logger.info("finance_service_starting")
    
    # Initialize Redis
    try:
        r = redis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            db=settings.redis_db,
            decode_responses=True
        )
        r.ping()
    except Exception as e:
        logger.error("redis_connection_failed", error=str(e))
        return

    processor = ReceiptProcessor()
    
    # Initialize Postgres Connection
    try:
        db_conn = psycopg2.connect(
            host=settings.postgres_host,
            user=settings.postgres_user,
            password=settings.postgres_password,
            database=settings.postgres_db,
            port=settings.postgres_port
        )
        db_conn.autocommit = True
        logger.info("postgres_connected", host=settings.postgres_host)
    except Exception as e:
        logger.error("postgres_connection_failed", error=str(e))
        return

    logger.info("finance_service_ready", queue="queue:finance")
    
    while True:
        try:
            # Blocking pop
            task = r.blpop("queue:finance", timeout=1)
            
            if not task:
                continue
                
            queue_name, task_json = task
            logger.info("task_received", queue=queue_name)
            
            try:
                task_data = json.loads(task_json)
                file_path_str = task_data.get("file_path")
                if not file_path_str:
                    logger.error("missing_file_path", task=task_data)
                    continue
                
                file_path = Path(file_path_str)
                
                if not file_path.exists():
                    logger.error("file_not_found", path=str(file_path))
                    continue
                    
                # Process
                result = processor.process_image(file_path)
                
                # Handling Result (Save to Database)
                try:
                    cur = db_conn.cursor()
                    cur.execute("""
                        INSERT INTO expenses (
                            shop_name, total_amount, purchase_date, items, 
                            verified, ocr_raw_text, image_path, source_file
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        result.get("shop_name", "Unknown"),
                        result.get("total_amount", 0.0),
                        result.get("date") or result.get("purchase_date"),
                        Json(result.get("items", [])),
                        False, # Verified
                        result.get("ocr_raw_text") or result.get("raw_text", ""),
                        str(file_path),
                        file_path.name
                    ))
                    cur.close()
                    logger.info("task_saved_to_db", file=file_path.name)
                except Exception as e:
                    logger.error("db_insert_failed", error=str(e))
                    # Fallback to file archive
                    output_file = Path("./data/receipts_archive") / f"{file_path.stem}.json"
                    output_file.parent.mkdir(parents=True, exist_ok=True)
                    with open(output_file, 'w', encoding='utf-8') as f:
                        json.dump(result, f, indent=2, ensure_ascii=False)
                    logger.info("task_saved_to_fallback_file", output=str(output_file))
                
            except json.JSONDecodeError:
                logger.error("invalid_task_format", task=task_json)
            except Exception as e:
                logger.error("processing_error", error=str(e))
                
        except KeyboardInterrupt:
            logger.info("finance_service_shutting_down")
            break
        except Exception as e:
            logger.error("loop_error", error=str(e))
            if "closed" in str(e).lower():
                # Try to reconnect
                try:
                    db_conn = psycopg2.connect(
                        host=settings.postgres_host,
                        user=settings.postgres_user,
                        password=settings.postgres_password,
                        database=settings.postgres_db,
                        port=settings.postgres_port
                    )
                    db_conn.autocommit = True
                    logger.info("postgres_reconnected")
                except:
                    pass
            time.sleep(1)
    
    if db_conn:
        db_conn.close()

if __name__ == "__main__":
    main()
