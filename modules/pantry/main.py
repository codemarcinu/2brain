import sys
import json
from pathlib import Path

# Add shared to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from modules.pantry.core.services.pantry_service import PantryService
from shared.logging import setup_logging, get_logger

setup_logging(level="INFO", service_name="pantry")
logger = get_logger(__name__)

def help():
    print("""
Pantry Service CLI (Agent 09)
Usage:
  python main.py consume <name> <qty>   - Record consumption
  python main.py refresh               - Force refresh Obsidian views
  python main.py add-receipt <file>    - Import a receipt JSON
  python main.py status                - Print current pantry state
    """)

def main():
    service = PantryService()
    
    if len(sys.argv) < 2:
        help()
        return

    cmd = sys.argv[1].lower()

    if cmd == "consume" and len(sys.argv) == 4:
        name = sys.argv[2]
        qty = float(sys.argv[3])
        if service.consume_product(name, qty):
            print(f"✅ Consumed {qty} of {name}")
        else:
            print(f"❌ Failed to consume {name}")

    elif cmd == "refresh":
        service.refresh_views()
        print("✅ Views refreshed")

    elif cmd == "add-receipt" and len(sys.argv) == 3:
        receipt_path = Path(sys.argv[2])
        if not receipt_path.exists():
            print(f"❌ File not found: {receipt_path}")
            return
        
        with open(receipt_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if service.process_receipt(data):
                print("✅ Receipt processed")
            else:
                print("❌ Failed to process receipt (possible duplicate)")

    elif cmd == "status":
        state = service.repo.get_pantry_state()
        print("\n--- Current Pantry State ---")
        for item in state:
            status = "✅" if item['stan'] >= item['minimum_ilosc'] else "⚠️"
            if item['stan'] <= 0: status = "❌"
            print(f"{status} {item['nazwa']:<20} | Stock: {item['stan']:>6.1f} {item['jednostka_miary']:<4} | Min: {item['minimum_ilosc']:>4.1f}")

    else:
        help()

if __name__ == "__main__":
    main()
