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
