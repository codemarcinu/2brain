"""
Testy wydajnosci systemu
"""
import pytest
import time
import statistics
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from shared.messaging import RedisClient
from shared.config import get_settings

settings = get_settings()


class TestRedisPerformance:
    """Testy wydajnosci Redis"""

    @pytest.fixture
    def redis(self):
        return RedisClient(
            host=settings.redis_host,
            port=settings.redis_port
        )

    def test_redis_throughput(self, redis):
        """Test przepustowosci Redis - ile wiadomosci/s"""
        test_queue = "perf_test_queue"
        num_messages = 1000

        # Publish messages
        start_time = time.time()
        for i in range(num_messages):
            redis.publish_task(test_queue, {"id": f"perf_{i}", "data": "x" * 100})
        publish_time = time.time() - start_time

        publish_rate = num_messages / publish_time
        print(f"\nPublish rate: {publish_rate:.0f} msg/s")

        # Verify all messages arrived
        queue_len = redis.get_queue_length(test_queue)
        assert queue_len == num_messages, f"Expected {num_messages}, got {queue_len}"

        # Cleanup
        redis.clear_queue(test_queue)

        # Assert minimum performance (at least 100 msg/s)
        assert publish_rate > 100, f"Publish rate too slow: {publish_rate:.0f} msg/s"

    def test_redis_latency(self, redis):
        """Test opoznienia Redis"""
        test_queue = "perf_latency_queue"
        num_samples = 100
        latencies = []

        for i in range(num_samples):
            start = time.perf_counter()
            redis.publish_task(test_queue, {"id": f"lat_{i}"})
            latencies.append((time.perf_counter() - start) * 1000)  # ms

        avg_latency = statistics.mean(latencies)
        p95_latency = sorted(latencies)[int(num_samples * 0.95)]
        p99_latency = sorted(latencies)[int(num_samples * 0.99)]

        print(f"\nLatency - avg: {avg_latency:.2f}ms, p95: {p95_latency:.2f}ms, p99: {p99_latency:.2f}ms")

        # Cleanup
        redis.clear_queue(test_queue)

        # Assert reasonable latency (under 50ms avg)
        assert avg_latency < 50, f"Average latency too high: {avg_latency:.2f}ms"

    def test_concurrent_publish(self, redis):
        """Test rownoleglego publikowania"""
        test_queue = "perf_concurrent_queue"
        num_threads = 10
        messages_per_thread = 100

        def publish_batch(thread_id):
            for i in range(messages_per_thread):
                redis.publish_task(test_queue, {"thread": thread_id, "msg": i})
            return messages_per_thread

        start_time = time.time()

        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(publish_batch, i) for i in range(num_threads)]
            total = sum(f.result() for f in as_completed(futures))

        elapsed = time.time() - start_time
        rate = total / elapsed

        print(f"\nConcurrent publish: {total} messages in {elapsed:.2f}s = {rate:.0f} msg/s")

        # Verify
        queue_len = redis.get_queue_length(test_queue)
        assert queue_len == num_threads * messages_per_thread

        # Cleanup
        redis.clear_queue(test_queue)


class TestFileSystemPerformance:
    """Testy wydajnosci systemu plikow"""

    @pytest.fixture
    def vault_path(self):
        return Path(settings.obsidian_vault_path)

    @pytest.fixture
    def inbox_path(self):
        return Path(settings.inbox_path)

    def test_file_write_speed(self, vault_path):
        """Test szybkosci zapisu plikow"""
        test_dir = vault_path / "_perf_test"
        test_dir.mkdir(parents=True, exist_ok=True)

        num_files = 100
        content = "# Test Note\n\n" + "Lorem ipsum " * 100

        start_time = time.time()
        for i in range(num_files):
            (test_dir / f"test_{i}.md").write_text(content)
        write_time = time.time() - start_time

        write_rate = num_files / write_time
        print(f"\nFile write rate: {write_rate:.0f} files/s")

        # Cleanup
        for f in test_dir.glob("*.md"):
            f.unlink()
        test_dir.rmdir()

        # Assert minimum performance
        assert write_rate > 10, f"Write rate too slow: {write_rate:.0f} files/s"

    def test_file_read_speed(self, vault_path):
        """Test szybkosci odczytu plikow"""
        # Find existing markdown files
        md_files = list(vault_path.rglob("*.md"))[:100]

        if not md_files:
            pytest.skip("No markdown files in vault to test")

        start_time = time.time()
        total_bytes = 0
        for f in md_files:
            content = f.read_text(errors='ignore')
            total_bytes += len(content)
        read_time = time.time() - start_time

        read_rate = len(md_files) / read_time if read_time > 0 else 0
        mb_rate = (total_bytes / 1024 / 1024) / read_time if read_time > 0 else 0

        print(f"\nFile read rate: {read_rate:.0f} files/s, {mb_rate:.2f} MB/s")

        assert read_rate > 10, f"Read rate too slow: {read_rate:.0f} files/s"

    def test_directory_scan_speed(self, vault_path):
        """Test szybkosci skanowania katalogu"""
        start_time = time.time()
        all_files = list(vault_path.rglob("*"))
        scan_time = time.time() - start_time

        scan_rate = len(all_files) / scan_time if scan_time > 0 else 0
        print(f"\nDirectory scan: {len(all_files)} files in {scan_time:.2f}s = {scan_rate:.0f} files/s")

        # Should be able to scan at least 100 files/s
        if len(all_files) > 10:
            assert scan_rate > 100, f"Scan rate too slow: {scan_rate:.0f} files/s"


class TestDatabasePerformance:
    """Testy wydajnosci bazy danych"""

    @pytest.fixture
    def db_connection(self):
        """PostgreSQL connection"""
        try:
            import psycopg2
            conn = psycopg2.connect(
                host=settings.postgres_host,
                port=settings.postgres_port,
                user=settings.postgres_user,
                password=settings.postgres_password,
                database=settings.postgres_db
            )
            yield conn
            conn.close()
        except Exception as e:
            pytest.skip(f"Cannot connect to PostgreSQL: {e}")

    def test_db_connection_speed(self, db_connection):
        """Test szybkosci laczenia z baza"""
        import psycopg2

        num_connections = 10
        times = []

        for _ in range(num_connections):
            start = time.perf_counter()
            conn = psycopg2.connect(
                host=settings.postgres_host,
                port=settings.postgres_port,
                user=settings.postgres_user,
                password=settings.postgres_password,
                database=settings.postgres_db
            )
            times.append((time.perf_counter() - start) * 1000)
            conn.close()

        avg_time = statistics.mean(times)
        print(f"\nDB connection time: avg {avg_time:.2f}ms")

        assert avg_time < 100, f"Connection too slow: {avg_time:.2f}ms"

    def test_db_query_speed(self, db_connection):
        """Test szybkosci prostego zapytania"""
        cursor = db_connection.cursor()
        num_queries = 100
        times = []

        for _ in range(num_queries):
            start = time.perf_counter()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            times.append((time.perf_counter() - start) * 1000)

        avg_time = statistics.mean(times)
        qps = 1000 / avg_time  # queries per second

        print(f"\nDB query speed: {qps:.0f} queries/s (avg {avg_time:.2f}ms)")

        assert qps > 100, f"Query speed too slow: {qps:.0f} q/s"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
