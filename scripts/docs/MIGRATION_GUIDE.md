# Migration Guide - From Old System to v2

## Overview

This guide helps you safely migrate from the old monolithic system to the new microservices architecture (Obsidian Brain v2).

## Pre-Migration Checklist

- [ ] **Backup**: Completely backup your old Vault and Receipt folder.
- [ ] **Export**: Ensure all data from the old system is accessible on the filesystem.
- [ ] **Review**: Read through the new architecture documentation if you haven't already.
- [ ] **Time**: Allocate 1-2 hours for the migration and validation process.
- [ ] **Users**: Inform any other users about potential downtime (if applicable).

## Migration Steps

### Step 1: Prepare New System

1.  **Clone the new repository:**
    ```bash
    cd ~/projects
    git clone <new-repo-url> obsidian-brain-v2
    cd obsidian-brain-v2
    ```

2.  **Configure environment:**
    ```bash
    cp .env.example .env
    # Edit .env and set paths:
    # OBSIDIAN_VAULT_PATH=/path/to/new/vault
    # INBOX_PATH=/path/to/new/inbox
    # ... other variables
    ```

3.  **Start infrastructure:**
    ```bash
    docker compose up -d redis postgres ollama qdrant
    docker compose logs -f
    ```
    Ensure all services start correctly.

### Step 2: Migrate Notes

This script copies markdown files from your old vault to the new one, preserving folder structure but ignoring configuration files.

```bash
# Syntax: python scripts/migration/migrate_notes.py <OLD_VAULT> <NEW_VAULT>
python scripts/migration/migrate_notes.py \
    /path/to/old/vault \
    /path/to/new/vault
```

**What it does:**
*   Creates a backup of the *new* vault before starting (in `backups/migration`).
*   Copies `.md` files.
*   Skips hidden files and `.obsidian` config.
*   Generates a JSON report in `backups/migration`.

### Step 3: Migrate Receipts (Optional)

If you have a collection of receipts (images/PDFs), migrate them to the new Inbox for processing by the Finance agent.

```bash
# Syntax: python scripts/migration/migrate_receipts.py <OLD_RECEIPTS_DIR> <NEW_INBOX_DIR>
python scripts/migration/migrate_receipts.py \
    /path/to/old/receipts \
    /path/to/new/inbox/receipts
```

**What it does:**
*   Copies image files (`.jpg`, `.png`, `.pdf`, etc.).
*   Renames files with a timestamp prefix to avoid collisions.
*   Generates a JSON report.

### Step 4: Validate Migration

After running the migration scripts, verify the integrity of the data.

```bash
# Syntax: python scripts/migration/validate_migration.py <OLD_VAULT> <NEW_VAULT>
python scripts/migration/validate_migration.py \
    /path/to/old/vault \
    /path/to/new/vault
```

**Checks performed:**
*   **File Count**: Ensures the number of files matches (accounting for filtered files).
*   **Integrity**: Compares MD5 hashes of migrated files to ensure content is identical.
*   **Folder Structure**: Verifies the directory tree is preserved.
*   **Links**: Checks for broken internal Wikilinks `[[...]]` in the new vault.

### Step 5: Start Services

Once data is migrated, start the application logic services.

```bash
docker compose up -d collector refinery finance pipelines open-webui
```

### Step 6: Post-Migration Validation

1.  **System Health Check:**
    ```bash
    python scripts/monitoring/health_check.py
    ```
    All checks should pass.

2.  **Manual Tests:**
    *   Drop a text file with a link into the `INBOX_PATH` and verify it gets processed into the Vault.
    *   Open the Open Web UI (`http://localhost:3000`) and verify RAG functionality.
    *   Check that old notes are visible and searchable.

## Rollback Plan

If critical issues are found:

1.  **Stop new services:**
    ```bash
    docker compose down
    ```
2.  **Restore Backup:**
    *   Restore the new vault from the backup created in `backups/migration`.
    *   Or simply delete the contents of the new vault if it was empty before.
3.  **Resume Old System:**
    *   Continue using the old system until the issue is resolved.

## Troubleshooting

*   **Permission Errors:** Ensure the user running the script has read access to the old vault and write access to the new vault and `backups/` directory.
*   **Missing Files:** Check `validate_migration.py` output. Hidden files and `.obsidian` folder are intentionally skipped.
*   **Service Failures:** Check logs with `docker compose logs -f <service_name>`.
