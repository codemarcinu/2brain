import sys
from datetime import datetime
from pathlib import Path

# Add shared to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent.parent))

from shared.config import get_settings
from shared.logging import get_logger

logger = get_logger(__name__)

class MarkdownGenerator:
    def __init__(self):
        self.settings = get_settings()
        self.vault_path = Path(self.settings.obsidian_vault_path)

    def regenerate_pantry_view(self, pantry_data: list) -> None:
        """Generates pantry dashboard in Markdown."""
        
        CAT_EMOJIS = {
            "NABIAŁ": "🥛", "MIĘSO_WĘDLINY": "🥩", "WARZYWA_OWOCE": "🍎", 
            "PIECZYWO": "🍞", "NAPOJE": "🧃", "CHEMIA_HIGIENA": "🧼", 
            "MROŻONKI": "🧊", "SYPKIE": "🌾", "INNE": "📦"
        }

        # Stats
        in_stock = sum(1 for i in pantry_data if i['stan'] > 0)
        low_stock = sum(1 for i in pantry_data if 0 < i['stan'] < i['minimum_ilosc'])
        out_of_stock = sum(1 for i in pantry_data if i['stan'] <= 0)

        md = f"# 📦 Stan Spiżarni\n"
        md += f"> Ostatnia aktualizacja: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
        md += f"**Podsumowanie:** ✅ {in_stock} dostępnych | ⚠️ {low_stock} kończy się | ❌ {out_of_stock} brak\n\n"
        
        # Group by category
        by_cat = {}
        for item in pantry_data:
            cat = item['kategoria'].upper()
            by_cat.setdefault(cat, []).append(item)

        for cat in sorted(by_cat.keys()):
            emoji = CAT_EMOJIS.get(cat, "📦")
            md += f"## {emoji} {cat}\n\n"
            md += "| Produkt | Stan | Min | Jedn | Status |\n"
            md += "|---|---:|---:|---|:---:|\n"
            
            for item in sorted(by_cat[cat], key=lambda x: x['nazwa']):
                status = "✅"
                if item['stan'] <= 0: status = "❌"
                elif item['stan'] < item['minimum_ilosc']: status = "⚠️"
                
                md += f"| {item['nazwa']} | {item['stan']:.1f} | {item['minimum_ilosc']:.0f} | {item['jednostka_miary']} | {status} |\n"
            md += "\n"

        target = self.vault_path / "Zasoby" / "Spiżarnia.md"
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(md, encoding='utf-8')
            logger.info("pantry_view_regenerated", path=str(target))
        except Exception as e:
            logger.error("pantry_view_generation_failed", error=str(e))

    def generate_shopping_list(self, pantry_data: list) -> None:
        """Generates shopping list note in Obsidian."""
        to_buy = [p for p in pantry_data if p['stan'] < p['minimum_ilosc']]

        md = f"# 📝 Lista Zakupów\n> Wygenerowano: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
        
        if not to_buy:
            md += "✅ Wszystko pod kontrolą. Spiżarnia pełna!\n"
        else:
            md += "## 🛒 Do kupienia:\n"
            for p in to_buy:
                suffix = f" (stan: {p['stan']:.1f}, min: {p['minimum_ilosc']})" if p['stan'] > 0 else " (BRAK)"
                md += f"- [ ] {p['nazwa']}{suffix}\n"
        
        md += "\n\n#shopping #pantry"

        target = self.vault_path / "Zasoby" / "Lista Zakupów.md"
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(md, encoding='utf-8')
            logger.info("shopping_list_generated", path=str(target))
        except Exception as e:
            logger.error("shopping_list_generation_failed", error=str(e))
