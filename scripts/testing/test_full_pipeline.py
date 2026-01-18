"""
End-to-End test całego pipeline'u
"""
import pytest
import time
from pathlib import Path
from shared.messaging import RedisClient
from shared.types import YoutubeTask, ArticleTask
from shared.config import get_settings

settings = get_settings()


class TestFullPipeline:
    """Testy E2E całego systemu"""
    
    @pytest.fixture
    def redis(self):
        """Redis client"""
        return RedisClient(host=settings.redis_host)
    
    @pytest.fixture
    def inbox_path(self):
        """Inbox folder"""
        return Path(settings.inbox_path)
    
    @pytest.fixture
    def vault_path(self):
        """Vault folder"""
        return Path(settings.obsidian_vault_path)
    
    def test_youtube_pipeline(self, redis, inbox_path, vault_path):
        """
        Test: Link YouTube → Collector → Redis → Refinery → Vault
        """
        # 1. Wrzuć link do Inbox
        test_link = "https://www.youtube.com/watch?v=F3QfS2U_P5c" # Grand tour of the International Space Station with Drew and Luca | Single take
        test_file = inbox_path / "test_youtube.txt"
        
        with open(test_file, 'w') as f:
            f.write(test_link)
        
        # Give the collector a moment to detect the new file
        time.sleep(5)
        
        # 2. Poczekaj na Collector (max 60s)
        start_time = time.time()
        task_found = False
        
        while time.time() - start_time < 60:
            queue_len = redis.get_queue_length("queue:refinery")
            if queue_len > 0:
                task_found = True
                break
            time.sleep(2)
        
        assert task_found, "Task not found in Redis queue after 60s"
        
        # 3. Poczekaj na Refinery (max 120s)
        start_time = time.time()
        note_created = False
        
        while time.time() - start_time < 120:
            # Check if note was created (search for today's date in filename)
            youtube_folder = vault_path / "YouTube"
            if youtube_folder.exists():
                notes = list(youtube_folder.glob("*.md"))
                if notes:
                    note_created = True
                    break
            time.sleep(5)
        
        assert note_created, "Note not created in Vault after 120s"
        
        # Cleanup
        test_file.unlink(missing_ok=True)
    
    def test_article_pipeline(self, redis, inbox_path, vault_path):
        """
        Test: Link WWW → Collector → Redis → Refinery → Vault
        """
        test_link = "https://en.wikipedia.org/wiki/Artificial_intelligence"
        test_file = inbox_path / "test_article.txt"
        
        with open(test_file, 'w') as f:
            f.write(test_link)
        
        # Wait for Collector
        start_time = time.time()
        while time.time() - start_time < 60:
            if redis.get_queue_length("queue:refinery") > 0:
                break
            time.sleep(2)
        
        # Wait for Refinery
        start_time = time.time()
        while time.time() - start_time < 120:
            articles_folder = vault_path / "Articles"
            if articles_folder.exists():
                notes = list(articles_folder.glob("*.md"))
                if notes:
                    # Success
                    test_file.unlink(missing_ok=True)
                    return
            time.sleep(5)
        
        pytest.fail("Article note not created in time")
    
    def test_redis_queues(self, redis):
        """Test podstawowej komunikacji Redis"""
        test_queue = "test_queue"
        
        # Publish
        success = redis.publish_task(test_queue, {"id": "test_001", "data": "hello"})
        assert success, "Failed to publish task"
        
        # Check queue length
        length = redis.get_queue_length(test_queue)
        assert length == 1, f"Expected queue length 1, got {length}"
        
        # Cleanup
        redis.clear_queue(test_queue)
