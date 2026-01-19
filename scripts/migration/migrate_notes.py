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
        if 'templates' in [p.lower() for p in file_path.parts]:
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
