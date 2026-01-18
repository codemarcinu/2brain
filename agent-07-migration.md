# Agent 7: Migration & Testing

## 🎭 Rola
**QA Engineer / DevOps**

## 🎯 Cel
Bezpieczna migracja ze starego systemu, testy integracyjne i monitoring produkcji

## 📖 Kontekst

Stary monolit nadal działa i ma cenne dane. Ten agent:
1. **Migruje** historyczne notatki do nowego Vault
2. **Testuje** cały pipeline end-to-end
3. **Monitoruje** system w produkcji
4. **Dokumentuje** proces przejścia

### Kluczowa zasada:
**Nie niszczyć starego systemu** - zachować jako backup przez 2-4 tygodnie.

## ✅ Zadania

### 1. Struktura Projektu

```
scripts/
├── migration/
│   ├── migrate_notes.py          # Migracja notatek
│   ├── migrate_receipts.py       # Migracja paragonów (jeśli były)
│   └── validate_migration.py     # Walidacja po migracji
├── testing/
│   ├── test_full_pipeline.py     # Test E2E
│   ├── test_performance.py       # Testy wydajności
│   └── test_data/                # Przykładowe dane testowe
├── monitoring/
│   ├── health_check.py           # Status wszystkich serwisów
│   ├── queue_monitor.py          # Monitoring Redis queues
│   └── dashboard.py              # Streamlit dashboard
├── backup/
│   ├── backup_postgres.sh        # Backup bazy danych
│   └── backup_vault.sh           # Backup Obsidian Vault
└── docs/
    ├── MIGRATION_GUIDE.md        # Instrukcja migracji
    ├── ROLLBACK_PLAN.md          # Plan wycofania zmian
    └── TROUBLESHOOTING.md        # Najczęstsze problemy
```

### 2. scripts/migration/migrate_notes.py

```python
"""
Migracja notatek ze starego Vault do nowego
"""
import shutil
from pathlib import Path
from datetime import datetime
import json
from typing import Dict, List
from shared.logging import setup_logging, get_logger

setup_logging(level="INFO", format="console", service_name="migration")
logger = get_logger(__name__)


class NoteMigrator:
    """Migrator dla notatek Obsidian"""
    
    def __init__(
        self,
        old_vault: Path,
        new_vault: Path,
        backup_dir: Path
    ):
        self.old_vault = old_vault
        self.new_vault = new_vault
        self.backup_dir = backup_dir
        
        # Create backup dir
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Migration report
        self.report = {
            'started_at': datetime.now().isoformat(),
            'migrated': [],
            'skipped': [],
            'errors': []
        }
    
    def backup_new_vault(self):
        """Backup nowego Vault przed migracją"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = self.backup_dir / f"vault_backup_{timestamp}"
        
        logger.info("creating_backup", path=str(backup_path))
        
        shutil.copytree(
            self.new_vault,
            backup_path,
            ignore=shutil.ignore_patterns('.*', '.obsidian')
        )
        
        logger.info("backup_created", path=str(backup_path))
        return backup_path
    
    def should_migrate_file(self, file_path: Path) -> bool:
        """Sprawdź czy plik powinien być migrowany"""
        # Skip hidden files
        if file_path.name.startswith('.'):
            return False
        
        # Skip Obsidian config
        if '.obsidian' in file_path.parts:
            return False
        
        # Skip templates
        if 'templates' in file_path.parts.lower():
            return False
        
        # Only markdown files
        if file_path.suffix != '.md':
            return False
        
        return True
    
    def migrate_file(self, old_file: Path) -> bool:
        """
        Migruj pojedynczy plik
        
        Returns:
            True jeśli sukces
        """
        try:
            # Relative path
            rel_path = old_file.relative_to(self.old_vault)
            new_file = self.new_vault / rel_path
            
            # Check if already exists
            if new_file.exists():
                logger.warning("file_exists_skipping", file=str(rel_path))
                self.report['skipped'].append({
                    'file': str(rel_path),
                    'reason': 'already_exists'
                })
                return False
            
            # Create parent dirs
            new_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy file
            shutil.copy2(old_file, new_file)
            
            logger.info("file_migrated", file=str(rel_path))
            self.report['migrated'].append({
                'file': str(rel_path),
                'size': old_file.stat().st_size,
                'mtime': old_file.stat().st_mtime
            })
            
            return True
            
        except Exception as e:
            logger.error("file_migration_failed", file=str(old_file), error=str(e))
            self.report['errors'].append({
                'file': str(old_file.relative_to(self.old_vault)),
                'error': str(e)
            })
            return False
    
    def run(self):
        """Uruchom pełną migrację"""
        logger.info(
            "migration_started",
            old_vault=str(self.old_vault),
            new_vault=str(self.new_vault)
        )
        
        # 1. Backup
        backup_path = self.backup_new_vault()
        
        # 2. Find all files to migrate
        all_files = list(self.old_vault.rglob('*.md'))
        files_to_migrate = [f for f in all_files if self.should_migrate_file(f)]
        
        logger.info("files_found", total=len(all_files), to_migrate=len(files_to_migrate))
        
        # 3. Migrate
        for file in files_to_migrate:
            self.migrate_file(file)
        
        # 4. Save report
        self.report['completed_at'] = datetime.now().isoformat()
        self.report['summary'] = {
            'total_files': len(files_to_migrate),
            'migrated': len(self.report['migrated']),
            'skipped': len(self.report['skipped']),
            'errors': len(self.report['errors'])
        }
        
        report_path = self.backup_dir / f"migration_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w') as f:
            json.dump(self.report, f, indent=2)
        
        logger.info(
            "migration_completed",
            migrated=self.report['summary']['migrated'],
            errors=self.report['summary']['errors'],
            report=str(report_path)
        )
        
        return self.report


def main():
    """Main entry point"""
    import sys
    
    if len(sys.argv) != 3:
        print("Usage: python migrate_notes.py <old_vault_path> <new_vault_path>")
        sys.exit(1)
    
    old_vault = Path(sys.argv[1])
    new_vault = Path(sys.argv[2])
    backup_dir = Path('./backups/migration')
    
    if not old_vault.exists():
        logger.error("old_vault_not_found", path=str(old_vault))
        sys.exit(1)
    
    if not new_vault.exists():
        logger.error("new_vault_not_found", path=str(new_vault))
        sys.exit(1)
    
    migrator = NoteMigrator(old_vault, new_vault, backup_dir)
    report = migrator.run()
    
    # Print summary
    print("\n" + "="*60)
    print("MIGRATION SUMMARY")
    print("="*60)
    print(f"Migrated: {report['summary']['migrated']}")
    print(f"Skipped:  {report['summary']['skipped']}")
    print(f"Errors:   {report['summary']['errors']}")
    print("="*60)
    
    if report['summary']['errors'] > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
```

### 3. scripts/testing/test_full_pipeline.py

```python
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
        return RedisClient()
    
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
        test_link = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        test_file = inbox_path / "test_youtube.txt"
        
        with open(test_file, 'w') as f:
            f.write(test_link)
        
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
```

### 4. scripts/monitoring/health_check.py

```python
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
```

### 5. scripts/monitoring/dashboard.py (Streamlit)

```python
"""
Monitoring Dashboard - Streamlit
"""
import streamlit as st
import redis
import psycopg2
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
from shared.config import get_settings

st.set_page_config(page_title="Obsidian Brain - Monitor", page_icon="📊", layout="wide")

settings = get_settings()


# Redis client
@st.cache_resource
def get_redis():
    return redis.Redis(host=settings.redis_host, port=settings.redis_port, decode_responses=True)


# Postgres connection
@st.cache_resource
def get_db():
    return psycopg2.connect(
        host=settings.postgres_host,
        user=settings.postgres_user,
        password=settings.postgres_password,
        database=settings.postgres_db
    )


st.title("📊 Obsidian Brain - System Monitor")

# Refresh button
if st.button("🔄 Refresh"):
    st.cache_resource.clear()
    st.rerun()

# Tabs
tab1, tab2, tab3 = st.tabs(["📈 Overview", "📋 Queues", "💰 Expenses"])


# === TAB 1: Overview ===
with tab1:
    st.header("System Status")
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Redis status
    with col1:
        try:
            r = get_redis()
            r.ping()
            st.metric("Redis", "✅ Healthy", delta="Online")
        except:
            st.metric("Redis", "❌ Down", delta="Offline")
    
    # Postgres status
    with col2:
        try:
            db = get_db()
            st.metric("PostgreSQL", "✅ Healthy", delta="Online")
        except:
            st.metric("PostgreSQL", "❌ Down", delta="Offline")
    
    # Queue stats
    with col3:
        try:
            r = get_redis()
            total_tasks = (
                r.llen("queue:collector") +
                r.llen("queue:refinery") +
                r.llen("queue:finance")
            )
            st.metric("Pending Tasks", total_tasks)
        except:
            st.metric("Pending Tasks", "N/A")
    
    # Expenses today
    with col4:
        try:
            db = get_db()
            cursor = db.cursor()
            cursor.execute("""
                SELECT COUNT(*) FROM expenses 
                WHERE created_at >= CURRENT_DATE
            """)
            count = cursor.fetchone()[0]
            st.metric("Expenses Today", count)
        except:
            st.metric("Expenses Today", "N/A")


# === TAB 2: Queues ===
with tab2:
    st.header("Redis Queues")
    
    try:
        r = get_redis()
        
        queues = {
            "queue:collector": r.llen("queue:collector"),
            "queue:refinery": r.llen("queue:refinery"),
            "queue:finance": r.llen("queue:finance"),
        }
        
        # Bar chart
        df = pd.DataFrame([
            {"Queue": k.split(':')[1].title(), "Tasks": v}
            for k, v in queues.items()
        ])
        
        fig = px.bar(df, x="Queue", y="Tasks", title="Queue Depths")
        st.plotly_chart(fig, use_container_width=True)
        
        # Table
        st.dataframe(df, use_container_width=True, hide_index=True)
        
    except Exception as e:
        st.error(f"Failed to load queues: {e}")


# === TAB 3: Expenses ===
with tab3:
    st.header("Expenses Analytics")
    
    try:
        db = get_db()
        
        # Last 30 days
        query = """
        SELECT 
            DATE(purchase_date) as date,
            category,
            SUM(total_amount) as total
        FROM expenses
        WHERE purchase_date >= CURRENT_DATE - INTERVAL '30 days'
        GROUP BY DATE(purchase_date), category
        ORDER BY date DESC
        """
        
        df = pd.read_sql(query, db)
        
        if not df.empty:
            # Line chart
            fig = px.line(df, x='date', y='total', color='category', title="Expenses Last 30 Days")
            st.plotly_chart(fig, use_container_width=True)
            
            # Summary by category
            summary = df.groupby('category')['total'].sum().reset_index()
            summary.columns = ['Category', 'Total (PLN)']
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("By Category")
                st.dataframe(summary, use_container_width=True, hide_index=True)
            
            with col2:
                st.subheader("Distribution")
                fig_pie = px.pie(summary, names='Category', values='Total (PLN)')
                st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No expenses in last 30 days")
            
    except Exception as e:
        st.error(f"Failed to load expenses: {e}")
```

### 6. docs/MIGRATION_GUIDE.md

```markdown
# Migration Guide - From Old System to v2

## Overview

This guide helps you safely migrate from the old monolithic system to the new microservices architecture.

## Pre-Migration Checklist

- [ ] Backup old Vault completely
- [ ] Export all important data from old system
- [ ] Review new architecture documentation
- [ ] Allocate 2-4 hours for migration
- [ ] Inform users about potential downtime

## Migration Steps

### Step 1: Prepare New System

```bash
# 1. Clone/create new project
cd ~/projects
git clone <new-repo> obsidian-brain-v2
cd obsidian-brain-v2

# 2. Configure environment
cp .env.example .env
nano .env  # Set OBSIDIAN_VAULT_PATH, etc.

# 3. Start infrastructure
docker compose up -d redis postgres ollama qdrant
docker compose logs -f
```

### Step 2: Migrate Notes

```bash
# Backup old vault first!
cp -r /path/to/old/vault /backup/old-vault-$(date +%Y%m%d)

# Run migration
python scripts/migration/migrate_notes.py \
    /path/to/old/vault \
    /path/to/new/vault

# Review migration report
cat backups/migration/migration_report_*.json
```

### Step 3: Migrate Receipts (if applicable)

```bash
# If you had receipts in old system
python scripts/migration/migrate_receipts.py \
    /path/to/old/receipts \
    /path/to/new/inbox/receipts
```

### Step 4: Start Services

```bash
# Start all microservices
docker compose up -d

# Watch logs
docker compose logs -f collector refinery
```

### Step 5: Validate

```bash
# Run health check
python scripts/monitoring/health_check.py

# Run tests
pytest scripts/testing/

# Manual validation:
# 1. Drop test link to Inbox
# 2. Check if note appears in Vault (within 2 min)
# 3. Test Finance UI (upload receipt)
# 4. Test Chat interface
```

### Step 6: Parallel Run (1-2 weeks)

Keep BOTH systems running:
- Old system: Read-only, for reference
- New system: Active, accepting new data

Monitor closely for issues.

### Step 7: Decommission Old System

After 2 weeks of stable operation:

```bash
# Final backup
./scripts/backup/backup_all.sh

# Stop old system
cd /path/to/old/system
./stop.sh  # or equivalent

# Archive old code
tar -czf old-system-archive-$(date +%Y%m%d).tar.gz /path/to/old/system
mv old-system-archive-*.tar.gz ~/archives/
```

## Rollback Plan

If critical issues occur:

```bash
# 1. Stop new system
cd obsidian-brain-v2
docker compose down

# 2. Restore old Vault
rm -rf /path/to/new/vault
cp -r /backup/old-vault-YYYYMMDD /path/to/vault

# 3. Restart old system
cd /path/to/old/system
./run_brain.sh  # or equivalent
```

## Common Migration Issues

### Issue: Notes not appearing
**Solution:** Check Refinery logs for LLM errors

### Issue: OCR fails on receipts
**Solution:** Verify tesseract installation in container

### Issue: Chat not finding notes
**Solution:** Re-run vault indexing

See TROUBLESHOOTING.md for more details.
```

### 7. docs/ROLLBACK_PLAN.md

```markdown
# Rollback Plan

## When to Rollback

Rollback if:
- Data loss occurs
- Critical features broken for >4 hours
- Performance degradation >50%
- Security vulnerability discovered

## Rollback Procedure

### Phase 1: Stop New System (5 minutes)

```bash
cd obsidian-brain-v2
docker compose down
```

### Phase 2: Restore Data (15 minutes)

```bash
# Restore Vault
rm -rf $OBSIDIAN_VAULT_PATH
cp -r /backup/vault-YYYYMMDD $OBSIDIAN_VAULT_PATH

# Restore database (if needed)
docker exec brain-postgres psql -U brain -d obsidian_brain < /backup/postgres-YYYYMMDD.sql
```

### Phase 3: Restart Old System (10 minutes)

```bash
cd /path/to/old/system
./run_brain.sh
```

### Phase 4: Validate (10 minutes)

- [ ] Old system starts successfully
- [ ] Vault accessible
- [ ] No data corruption
- [ ] All features working

### Phase 5: Communication

Notify users:
- What happened
- Why rollback was necessary
- Expected timeline for fix
- Workarounds if any

## Post-Rollback Actions

1. **Investigate root cause**
2. **Fix issues in staging**
3. **Re-test thoroughly**
4. **Plan new migration date**

## Prevention

- Always backup before changes
- Test in staging first
- Have monitoring alerts
- Keep old system for 2 weeks minimum
```

## 🎯 Kryteria Sukcesu

```bash
# 1. Migracja działa
python scripts/migration/migrate_notes.py /old/vault /new/vault
# Expected: Migration report with 0 errors

# 2. Testy przechodzą
pytest scripts/testing/ -v
# Expected: All tests pass

# 3. Health check OK
python scripts/monitoring/health_check.py
# Expected: All services healthy

# 4. Dashboard działa
streamlit run scripts/monitoring/dashboard.py
# Open http://localhost:8501
```

### Checklist końcowy:
- [ ] Notatki zmigrowane bez błędów
- [ ] Testy E2E przechodzą
- [ ] Health check pokazuje wszystko OK
- [ ] Dashboard monitoringu działa
- [ ] Dokumentacja kompletna (Migration Guide, Rollback Plan)
- [ ] Backup scripts działają

## 📦 Pliki Wyjściowe

Kompletny folder `scripts/` z narzędziami do migracji, testów i monitoringu.

## 🔗 Zależności

**Wymaga:**
- ✅ Wszystkie poprzednie agenty (1-6) działające

---

**Status:** 🟢 Gotowy
**Czas:** ~90 minut
**To ostatni agent - system kompletny! 🎉**
