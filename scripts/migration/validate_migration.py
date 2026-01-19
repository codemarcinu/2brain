"""
Walidacja migracji - sprawdzenie integralnosci danych po migracji
"""
import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple
from shared.logging import setup_logging, get_logger

setup_logging(level="INFO", format="console", service_name="migration-validate")
logger = get_logger(__name__)


class MigrationValidator:
    """Walidator migracji"""

    def __init__(
        self,
        old_vault: Path,
        new_vault: Path,
        report_dir: Path
    ):
        self.old_vault = old_vault
        self.new_vault = new_vault
        self.report_dir = report_dir
        self.report_dir.mkdir(parents=True, exist_ok=True)

        self.validation_report = {
            'started_at': datetime.now().isoformat(),
            'checks': [],
            'issues': []
        }

    def calculate_file_hash(self, file_path: Path) -> str:
        """Calculate MD5 hash of file"""
        hasher = hashlib.md5()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hasher.update(chunk)
        return hasher.hexdigest()

    def check_file_count(self) -> Tuple[bool, Dict]:
        """Check if file counts match"""
        old_files = list(self.old_vault.rglob('*.md'))
        new_files = list(self.new_vault.rglob('*.md'))

        # Filter out hidden and config files
        old_files = [f for f in old_files
                    if not f.name.startswith('.')
                    and '.obsidian' not in str(f)]
        new_files = [f for f in new_files
                    if not f.name.startswith('.')
                    and '.obsidian' not in str(f)]

        result = {
            'check': 'file_count',
            'old_count': len(old_files),
            'new_count': len(new_files),
            'passed': len(new_files) >= len(old_files)
        }

        if not result['passed']:
            self.validation_report['issues'].append({
                'type': 'missing_files',
                'expected': len(old_files),
                'actual': len(new_files),
                'difference': len(old_files) - len(new_files)
            })

        return result['passed'], result

    def check_file_integrity(self) -> Tuple[bool, Dict]:
        """Check if migrated files have same content"""
        mismatches = []
        checked = 0

        for old_file in self.old_vault.rglob('*.md'):
            if old_file.name.startswith('.') or '.obsidian' in str(old_file):
                continue

            rel_path = old_file.relative_to(self.old_vault)
            new_file = self.new_vault / rel_path

            if new_file.exists():
                checked += 1
                old_hash = self.calculate_file_hash(old_file)
                new_hash = self.calculate_file_hash(new_file)

                if old_hash != new_hash:
                    mismatches.append({
                        'file': str(rel_path),
                        'old_hash': old_hash,
                        'new_hash': new_hash
                    })

        result = {
            'check': 'file_integrity',
            'files_checked': checked,
            'mismatches': len(mismatches),
            'passed': len(mismatches) == 0
        }

        if mismatches:
            self.validation_report['issues'].append({
                'type': 'content_mismatch',
                'files': mismatches
            })

        return result['passed'], result

    def check_folder_structure(self) -> Tuple[bool, Dict]:
        """Check if folder structure is preserved"""
        old_folders = set()
        new_folders = set()

        for old_file in self.old_vault.rglob('*.md'):
            if '.obsidian' not in str(old_file):
                rel_path = old_file.relative_to(self.old_vault).parent
                if str(rel_path) != '.':
                    old_folders.add(str(rel_path))

        for new_file in self.new_vault.rglob('*.md'):
            if '.obsidian' not in str(new_file):
                rel_path = new_file.relative_to(self.new_vault).parent
                if str(rel_path) != '.':
                    new_folders.add(str(rel_path))

        missing_folders = old_folders - new_folders

        result = {
            'check': 'folder_structure',
            'old_folders': len(old_folders),
            'new_folders': len(new_folders),
            'missing': list(missing_folders),
            'passed': len(missing_folders) == 0
        }

        if missing_folders:
            self.validation_report['issues'].append({
                'type': 'missing_folders',
                'folders': list(missing_folders)
            })

        return result['passed'], result

    def check_links_integrity(self) -> Tuple[bool, Dict]:
        """Check if internal links are valid"""
        broken_links = []

        for md_file in self.new_vault.rglob('*.md'):
            if '.obsidian' in str(md_file):
                continue

            content = md_file.read_text(encoding='utf-8', errors='ignore')

            # Find wiki-style links [[link]]
            import re
            links = re.findall(r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]', content)

            for link in links:
                # Check if linked file exists
                link_path = self.new_vault / f"{link}.md"
                # Also check with same parent folder
                link_path_relative = md_file.parent / f"{link}.md"

                if not link_path.exists() and not link_path_relative.exists():
                    # Try to find anywhere in vault
                    found = list(self.new_vault.rglob(f"{link}.md"))
                    if not found:
                        broken_links.append({
                            'source': str(md_file.relative_to(self.new_vault)),
                            'broken_link': link
                        })

        result = {
            'check': 'links_integrity',
            'broken_links_count': len(broken_links),
            'passed': len(broken_links) == 0
        }

        if broken_links:
            self.validation_report['issues'].append({
                'type': 'broken_links',
                'links': broken_links[:20]  # Limit to first 20
            })

        return result['passed'], result

    def run_all_checks(self) -> Dict:
        """Run all validation checks"""
        logger.info("validation_started",
                   old_vault=str(self.old_vault),
                   new_vault=str(self.new_vault))

        checks = [
            ('file_count', self.check_file_count),
            ('file_integrity', self.check_file_integrity),
            ('folder_structure', self.check_folder_structure),
            ('links_integrity', self.check_links_integrity),
        ]

        all_passed = True

        for check_name, check_func in checks:
            logger.info(f"running_check", check=check_name)
            passed, result = check_func()
            self.validation_report['checks'].append(result)

            if passed:
                logger.info(f"check_passed", check=check_name)
            else:
                logger.warning(f"check_failed", check=check_name)
                all_passed = False

        # Summary
        self.validation_report['completed_at'] = datetime.now().isoformat()
        self.validation_report['summary'] = {
            'total_checks': len(checks),
            'passed': sum(1 for c in self.validation_report['checks'] if c['passed']),
            'failed': sum(1 for c in self.validation_report['checks'] if not c['passed']),
            'all_passed': all_passed
        }

        # Save report
        report_path = self.report_dir / f"validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w') as f:
            json.dump(self.validation_report, f, indent=2)

        logger.info("validation_completed",
                   all_passed=all_passed,
                   report=str(report_path))

        return self.validation_report

    def print_report(self):
        """Print human-readable report"""
        print("\n" + "="*60)
        print("MIGRATION VALIDATION REPORT")
        print("="*60)

        for check in self.validation_report['checks']:
            status = "PASS" if check['passed'] else "FAIL"
            print(f"\n{check['check']}: {status}")
            for key, value in check.items():
                if key not in ['check', 'passed']:
                    print(f"  {key}: {value}")

        print("\n" + "-"*60)
        summary = self.validation_report['summary']
        print(f"Total: {summary['passed']}/{summary['total_checks']} checks passed")

        if self.validation_report['issues']:
            print(f"\nIssues found: {len(self.validation_report['issues'])}")
            for issue in self.validation_report['issues'][:5]:
                print(f"  - {issue['type']}")

        print("="*60)

        if summary['all_passed']:
            print("Migration validated successfully!")
        else:
            print("Migration validation FAILED - review issues above")

        print("="*60 + "\n")


def main():
    """Main entry point"""
    import sys

    if len(sys.argv) != 3:
        print("Usage: python validate_migration.py <old_vault_path> <new_vault_path>")
        sys.exit(1)

    old_vault = Path(sys.argv[1])
    new_vault = Path(sys.argv[2])
    report_dir = Path('./backups/migration')

    if not old_vault.exists():
        print(f"Error: Old vault not found: {old_vault}")
        sys.exit(1)

    if not new_vault.exists():
        print(f"Error: New vault not found: {new_vault}")
        sys.exit(1)

    validator = MigrationValidator(old_vault, new_vault, report_dir)
    validator.run_all_checks()
    validator.print_report()

    if not validator.validation_report['summary']['all_passed']:
        sys.exit(1)


if __name__ == "__main__":
    main()
