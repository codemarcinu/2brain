"""
Testy dla modułu messaging
"""
import pytest
from shared.messaging import RedisClient, TaskQueue
from shared.types import ArticleTask


@pytest.fixture
def redis_client():
    """Fixture z klientem Redis (wymaga działającego Redis)"""
    client = RedisClient(host="localhost")
    yield client
    # Cleanup
    client.clear_queue("test_queue")


def test_redis_connection(redis_client):
    """Test połączenia z Redis"""
    assert redis_client.ping() is True


def test_publish_task(redis_client):
    """Test publikacji zadania"""
    task = {"id": "test_001", "type": "test", "data": "hello"}
    result = redis_client.publish_task("test_queue", task)
    assert result is True
    assert redis_client.get_queue_length("test_queue") == 1


def test_listen_to_queue(redis_client):
    """Test nasłuchiwania na kolejce"""
    received_tasks = []
    
    def callback(task):
        received_tasks.append(task)
    
    # Wyślij zadanie
    task = {"id": "test_002", "data": "test"}
    redis_client.publish_task("test_queue", task)
    
    # Nasłuchuj (timeout aby nie czekać w nieskończoność)
    result = redis_client.client.brpop("test_queue", timeout=1)
    assert result is not None


def test_task_queue_wrapper(redis_client):
    """Test wysokopoziomowego API"""
    queue = TaskQueue(redis_client=redis_client)
    
    task = ArticleTask(
        id="art_001",
        url="https://example.com",
        content="Test content"
    )
    
    result = queue.send_to_refinery(task.model_dump(mode='json'))
    assert result is True
