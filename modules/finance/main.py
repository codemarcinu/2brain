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
from config import config
from services.receipt_processor import ReceiptProcessor

setup_logging(
    level=config.base.log_level,
    service_name="finance"
)
logger = get_logger(__name__)

def main():
    """Main loop"""
    logger.info("finance_service_starting")
    
    # Initialize Redis
    try:
        r = redis.Redis(
            host=config.base.redis_host,
            port=config.base.redis_port,
            db=config.base.redis_db,
            decode_responses=True
        )
        r.ping()
    except Exception as e:
        logger.error("redis_connection_failed", error=str(e))
        return

    processor = ReceiptProcessor()
    
    logger.info("finance_service_ready", queue=config.input_queue)
    
    while True:
        try:
            # Blocking pop
            # Expected msg: {"id": "...", "file_path": "..."}
            task = r.blpop(config.input_queue, timeout=1)
            
            if not task:
                continue
                
            queue_name, task_json = task
            logger.info("task_received", queue=queue_name)
            
            try:
                task_data = json.loads(task_json)
                file_path = Path(task_data.get("file_path"))
                
                if not file_path.exists():
                    logger.error("file_not_found", path=str(file_path))
                    continue
                    
                # Process
                result = processor.process_image(file_path)
                
                # Handling Result (Save to Archive)
                # In real app: Save to DB, Create Obsidian Note
                output_file = config.receipts_archive_path / f"{file_path.stem}.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
                    
                logger.info("task_completed", output=str(output_file))
                
            except json.JSONDecodeError:
                logger.error("invalid_task_format", task=task_json)
            except Exception as e:
                logger.error("processing_error", error=str(e))
                
        except KeyboardInterrupt:
            logger.info("finance_service_shutting_down")
            break
        except Exception as e:
            logger.error("loop_error", error=str(e))
            time.sleep(1)

if __name__ == "__main__":
    main()
