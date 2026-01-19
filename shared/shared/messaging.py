"""
Redis messaging dla komunikacji między serwisami
"""
import json
import redis
from typing import Callable, Any, Optional
from datetime import datetime
import structlog

logger = structlog.get_logger()


class RedisClient:
    """
    Wrapper na Redis do zarządzania kolejkami zadań
    """
    
    def __init__(
        self,
        host: str = "redis",
        port: int = 6379,
        db: int = 0,
        decode_responses: bool = True
    ):
        """
        Args:
            host: Redis host
            port: Redis port
            db: Database number
            decode_responses: Czy dekodować odpowiedzi jako string
        """
        self.client = redis.Redis(
            host=host,
            port=port,
            db=db,
            decode_responses=decode_responses,
            socket_connect_timeout=5,
            retry_on_timeout=True,
            health_check_interval=30,
        )
        logger.info("redis_connected", host=host, port=port, db=db)
    
    def ping(self) -> bool:
        """Sprawdź czy Redis odpowiada"""
        try:
            return self.client.ping()
        except redis.ConnectionError:
            logger.error("redis_connection_failed")
            return False
    
    def publish_task(
        self,
        queue_name: str,
        payload: dict,
        priority: int = 0
    ) -> bool:
        """
        Wyślij zadanie do kolejki
        
        Args:
            queue_name: Nazwa kolejki (np. 'queue:refinery')
            payload: Dane zadania (dict)
            priority: Priorytet (wyższy = ważniejsze)
        
        Returns:
            True jeśli sukces
        """
        try:
            # Dodaj metadata
            task = {
                **payload,
                "metadata": {
                    "enqueued_at": datetime.utcnow().isoformat(),
                    "priority": priority,
                }
            }
            
            # LPUSH dodaje na początek listy (FIFO z RPOP)
            self.client.lpush(queue_name, json.dumps(task))
            
            logger.info(
                "task_published",
                queue=queue_name,
                task_id=payload.get("id"),
                priority=priority
            )
            return True
            
        except Exception as e:
            logger.error(
                "task_publish_failed",
                queue=queue_name,
                error=str(e)
            )
            return False
    
    def listen_to_queue(
        self,
        queue_name: str,
        callback: Callable[[dict], None],
        timeout: int = 0
    ) -> None:
        """
        Nasłuchuj na kolejce i wywołuj callback dla każdego zadania
        
        Args:
            queue_name: Nazwa kolejki
            callback: Funkcja przetwarzająca zadanie callback(task_data)
            timeout: Timeout w sekundach (0 = blokujące czekanie)
        
        Przykład:
            def process_task(task):
                print(f"Processing: {task}")
            
            client.listen_to_queue("queue:refinery", process_task)
        """
        logger.info("queue_listener_started", queue=queue_name)
        
        while True:
            try:
                # BRPOP - blokujące pobranie z końca listy
                result = self.client.brpop(queue_name, timeout=timeout or 0)
                
                if result:
                    _, task_json = result
                    task = json.loads(task_json)
                    
                    logger.info(
                        "task_received",
                        queue=queue_name,
                        task_id=task.get("id")
                    )
                    
                    # Wywołaj callback
                    callback(task)
                    
            except json.JSONDecodeError as e:
                logger.error("task_json_decode_error", error=str(e))
            except KeyboardInterrupt:
                logger.info("queue_listener_stopped", queue=queue_name)
                break
            except Exception as e:
                logger.error(
                    "queue_listener_error",
                    queue=queue_name,
                    error=str(e)
                )
    
    def get_queue_length(self, queue_name: str) -> int:
        """Ile zadań w kolejce"""
        return self.client.llen(queue_name)
    
    def clear_queue(self, queue_name: str) -> bool:
        """Wyczyść wszystkie zadania z kolejki"""
        try:
            self.client.delete(queue_name)
            logger.warning("queue_cleared", queue=queue_name)
            return True
        except Exception as e:
            logger.error("queue_clear_failed", queue=queue_name, error=str(e))
            return False


class TaskQueue:
    """
    Wysokopoziomowy wrapper - uproszczone API dla standardowych operacji
    """
    
    # Standardowe nazwy kolejek
    COLLECTOR_QUEUE = "queue:collector"
    REFINERY_QUEUE = "queue:refinery"
    FINANCE_QUEUE = "queue:finance"
    
    def __init__(self, redis_client: Optional[RedisClient] = None):
        self.redis = redis_client or RedisClient()
    
    def send_to_refinery(self, task: dict) -> bool:
        """Wyślij zadanie do przetworzenia przez AI"""
        return self.redis.publish_task(self.REFINERY_QUEUE, task)
    
    def send_to_finance(self, task: dict) -> bool:
        """Wyślij paragon do weryfikacji"""
        return self.redis.publish_task(self.FINANCE_QUEUE, task)
    
    def get_stats(self) -> dict:
        """Statystyki wszystkich kolejek"""
        return {
            "collector": self.redis.get_queue_length(self.COLLECTOR_QUEUE),
            "refinery": self.redis.get_queue_length(self.REFINERY_QUEUE),
            "finance": self.redis.get_queue_length(self.FINANCE_QUEUE),
        }
