"""
Health check dla wszystkich serwisów
"""
import requests
import redis
import psycopg2
from pathlib import Path
from typing import Dict
from shared.config import get_settings
from shared.logging import setup_logging, get_logger

setup_logging(level="INFO", format="console", service_name="health-check")
logger = get_logger(__name__)
settings = get_settings()


class HealthChecker:
    """Sprawdzanie stanu wszystkich serwisów"""
    
    def __init__(self):
        self.results = {}
    
    def check_redis(self) -> bool:
        """Check Redis"""
        try:
            r = redis.Redis(host=settings.redis_host, port=settings.redis_port)
            r.ping()
            logger.info("redis_healthy")
            return True
        except Exception as e:
            logger.error("redis_unhealthy", error=str(e))
            return False
    
    def check_postgres(self) -> bool:
        """Check PostgreSQL"""
        try:
            conn = psycopg2.connect(
                host=settings.postgres_host,
                port=settings.postgres_port,
                user=settings.postgres_user,
                password=settings.postgres_password,
                database=settings.postgres_db
            )
            conn.close()
            logger.info("postgres_healthy")
            return True
        except Exception as e:
            logger.error("postgres_unhealthy", error=str(e))
            return False
    
    def check_ollama(self) -> bool:
        """Check Ollama"""
        try:
            response = requests.get(f"{settings.ollama_host}/api/tags", timeout=5)
            response.raise_for_status()
            logger.info("ollama_healthy")
            return True
        except Exception as e:
            logger.error("ollama_unhealthy", error=str(e))
            return False
    
    def check_qdrant(self) -> bool:
        """Check Qdrant"""
        try:
            response = requests.get("http://qdrant:6333/", timeout=5)
            response.raise_for_status()
            logger.info("qdrant_healthy")
            return True
        except Exception as e:
            logger.error("qdrant_unhealthy", error=str(e))
            return False
    
    def check_open_webui(self) -> bool:
        """Check Open Web UI"""
        try:
            response = requests.get("http://open-webui:8080/health", timeout=5)
            response.raise_for_status()
            logger.info("open_webui_healthy")
            return True
        except Exception as e:
            logger.error("open_webui_unhealthy", error=str(e))
            return False
    
    def check_vault(self) -> bool:
        """Check Obsidian Vault accessibility"""
        vault_path = Path(settings.obsidian_vault_path)
        if vault_path.exists() and vault_path.is_dir():
            logger.info("vault_accessible")
            return True
        else:
            logger.error("vault_not_accessible", path=str(vault_path))
            return False
    
    def run_all_checks(self) -> Dict[str, bool]:
        """Run all health checks"""
        logger.info("health_check_started")
        
        self.results = {
            'redis': self.check_redis(),
            'postgres': self.check_postgres(),
            'ollama': self.check_ollama(),
            'qdrant': self.check_qdrant(),
            'open_webui': self.check_open_webui(),
            'vault': self.check_vault(),
        }
        
        # Overall status
        all_healthy = all(self.results.values())
        
        if all_healthy:
            logger.info("all_services_healthy")
        else:
            unhealthy = [k for k, v in self.results.items() if not v]
            logger.warning("some_services_unhealthy", services=unhealthy)
        
        return self.results
    
    def print_report(self):
        """Print human-readable report"""
        print("\n" + "="*60)
        print("HEALTH CHECK REPORT")
        print("="*60)
        
        for service, healthy in self.results.items():
            status = "✅ HEALTHY" if healthy else "❌ UNHEALTHY"
            print(f"{service:.<20} {status}")
        
        print("="*60)
        
        all_healthy = all(self.results.values())
        if all_healthy:
            print("🎉 All systems operational!")
        else:
            print("⚠️  Some systems require attention")
        print("="*60 + "\n")


def main():
    checker = HealthChecker()
    checker.run_all_checks()
    checker.print_report()
    
    # Exit code
    if all(checker.results.values()):
        exit(0)
    else:
        exit(1)


if __name__ == "__main__":
    main()
