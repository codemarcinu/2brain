"""
End-to-End test całego pipeline'u
"""
import pytest
import time
from pathlib import Path
from shared.messaging import RedisClient
from shared.types import YoutubeTask, ArticleTask
from shared.config import get_settings
import dotenv
import os

dotenv.load_dotenv() # Load environment variables from .env
get_settings.cache_clear() # Clear the cache for settings


settings = get_settings()
settings.redis_host = "localhost" # Force Redis host to localhost


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
        unique_token = f"test_{int(time.time())}"
        test_link = f"https://www.youtube.com/watch?v=jNQXAC9IVRw&test={unique_token}" # Me at the zoo
        test_file = inbox_path / f"test_youtube_{unique_token}.txt"
        
        youtube_folder = vault_path / "YouTube"
        youtube_folder.mkdir(parents=True, exist_ok=True)
        initial_count = len(list(youtube_folder.glob("*.md")))

        with open(test_file, 'w') as f:
            f.write(test_link)
    
        # Give the collector a moment to detect the new file
        time.sleep(30) # Increased from 5 to 30 seconds
    
        # 2. Poczekaj na Collector (max 120s)
        start_time = time.time()
        task_found = False
    
        while time.time() - start_time < 120: # Increased from 60 to 120 seconds
            queue_len = redis.get_queue_length("queue:refinery")
            
            # Check if note was created (fast path: count increased)
            if len(list(youtube_folder.glob("*.md"))) > initial_count:
                task_found = True
                break

            if queue_len > 0:
                task_found = True
                break
            time.sleep(2)        
        assert task_found, "Task not found in Redis queue (or processed too fast)"
        
        # 3. Poczekaj na Refinery (max 120s)
        start_time = time.time()
        note_created = False
        
        while time.time() - start_time < 120:
            # Check if note was created (search for count increase)
            if len(list(youtube_folder.glob("*.md"))) > initial_count:
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
        unique_token = f"test_{int(time.time())}"
        test_link = f"https://en.wikipedia.org/wiki/Artificial_intelligence?test={unique_token}"
        test_file = inbox_path / f"test_article_{unique_token}.txt"
        
        articles_folder = vault_path / "Articles"
        articles_folder.mkdir(parents=True, exist_ok=True)
        initial_count = len(list(articles_folder.glob("*.md")))

        with open(test_file, 'w') as f:
            f.write(test_link)
        
        # Wait for Collector
        start_time = time.time()
        while time.time() - start_time < 120: # Increased from 60 to 120 seconds
            if redis.get_queue_length("queue:refinery") > 0:
                break
            # Or if file already created
            if len(list(articles_folder.glob("*.md"))) > initial_count:
                break
            time.sleep(2)
        
        # Wait for Refinery
        start_time = time.time()
        while time.time() - start_time < 120:
            if len(list(articles_folder.glob("*.md"))) > initial_count:
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
