"""
Migracja paragonow ze starego systemu do nowego Inbox
"""
import shutil
from pathlib import Path
from datetime import datetime
import json
from shared.logging import setup_logging, get_logger

setup_logging(level="INFO", format="console", service_name="migration-receipts")
logger = get_logger(__name__)


class ReceiptMigrator:
    """Migrator dla paragonow/rachunkow"""

    SUPPORTED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.pdf', '.webp'}

    def __init__(
        self,
        old_receipts_dir: Path,
        new_inbox_dir: Path,
        backup_dir: Path
    ):
        self.old_receipts_dir = old_receipts_dir
        self.new_inbox_dir = new_inbox_dir
        self.backup_dir = backup_dir

        # Ensure directories exist
        self.new_inbox_dir.mkdir(parents=True, exist_ok=True)
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        # Migration report
        self.report = {
            'started_at': datetime.now().isoformat(),
            'migrated': [],
            'skipped': [],
            'errors': []
        }

    def should_migrate_file(self, file_path: Path) -> bool:
        """Check if file should be migrated"""
        # Skip hidden files
        if file_path.name.startswith('.'):
            return False

        # Only supported image/pdf formats
        if file_path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
            return False

        return True

    def migrate_file(self, old_file: Path) -> bool:
        """Migrate single receipt file"""
        try:
            # Create unique filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            new_name = f"{timestamp}_{old_file.name}"
            new_file = self.new_inbox_dir / new_name

            # Check if already exists
            if new_file.exists():
                logger.warning("file_exists_skipping", file=old_file.name)
                self.report['skipped'].append({
                    'file': old_file.name,
                    'reason': 'already_exists'
                })
                return False

            # Copy file
            shutil.copy2(old_file, new_file)

            logger.info("receipt_migrated",
                       original=old_file.name,
                       new=new_name)

            self.report['migrated'].append({
                'original_file': old_file.name,
                'new_file': new_name,
                'size': old_file.stat().st_size
            })

            return True

        except Exception as e:
            logger.error("receipt_migration_failed",
                        file=old_file.name,
                        error=str(e))
            self.report['errors'].append({
                'file': old_file.name,
                'error': str(e)
            })
            return False

    def run(self):
        """Run full migration"""
        logger.info(
            "receipt_migration_started",
            source=str(self.old_receipts_dir),
            destination=str(self.new_inbox_dir)
        )

        # Find all receipt files
        all_files = []
        for ext in self.SUPPORTED_EXTENSIONS:
            all_files.extend(self.old_receipts_dir.rglob(f'*{ext}'))
            all_files.extend(self.old_receipts_dir.rglob(f'*{ext.upper()}'))

        files_to_migrate = [f for f in all_files if self.should_migrate_file(f)]

        logger.info("receipts_found",
                   total=len(all_files),
                   to_migrate=len(files_to_migrate))

        # Migrate each file
        for file in files_to_migrate:
            self.migrate_file(file)

        # Save report
        self.report['completed_at'] = datetime.now().isoformat()
        self.report['summary'] = {
            'total_files': len(files_to_migrate),
            'migrated': len(self.report['migrated']),
            'skipped': len(self.report['skipped']),
            'errors': len(self.report['errors'])
        }

        report_path = self.backup_dir / f"receipt_migration_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w') as f:
            json.dump(self.report, f, indent=2)

        logger.info(
            "receipt_migration_completed",
            migrated=self.report['summary']['migrated'],
            errors=self.report['summary']['errors'],
            report=str(report_path)
        )

        return self.report


def main():
    """Main entry point"""
    import sys

    if len(sys.argv) != 3:
        print("Usage: python migrate_receipts.py <old_receipts_path> <new_inbox_path>")
        sys.exit(1)

    old_receipts_dir = Path(sys.argv[1])
    new_inbox_dir = Path(sys.argv[2])
    backup_dir = Path('./backups/migration')

    if not old_receipts_dir.exists():
        logger.error("old_receipts_not_found", path=str(old_receipts_dir))
        sys.exit(1)

    migrator = ReceiptMigrator(old_receipts_dir, new_inbox_dir, backup_dir)
    report = migrator.run()

    # Print summary
    print("\n" + "="*60)
    print("RECEIPT MIGRATION SUMMARY")
    print("="*60)
    print(f"Migrated: {report['summary']['migrated']}")
    print(f"Skipped:  {report['summary']['skipped']}")
    print(f"Errors:   {report['summary']['errors']}")
    print("="*60)

    if report['summary']['errors'] > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
