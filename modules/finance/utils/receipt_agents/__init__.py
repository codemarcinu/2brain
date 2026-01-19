from .base import BaseReceiptAgent

class GenericAgent(BaseReceiptAgent):
    def preprocess(self, text: str) -> str:
        # Default: just return text, maybe trim lines
        return "\n".join([l.strip() for l in text.split('\n') if l.strip()])

class BiedronkaAgent(BaseReceiptAgent):
    """Specific logic for Biedronka receipts"""
    def preprocess(self, text: str) -> str:
        # Filter out common ad lines or footer noise
        lines = []
        for line in text.split('\n'):
            line = line.strip()
            if not line: continue
            
            normalized = line.lower()
            if any(x in normalized for x in ["biedronka", "nasza", "codziennie", "niskie ceny"]):
                continue
            lines.append(line)
        return "\n".join(lines)

SHOP_AGENTS = {
    "Biedronka": BiedronkaAgent
}

def detect_shop(text: str) -> str:
    lower = text.lower()
    if "biedronka" in lower: return "Biedronka"
    if "lidl" in lower: return "Lidl"
    if "auchan" in lower: return "Auchan"
    if "carrefour" in lower: return "Carrefour"
    if "rossmann" in lower: return "Rossmann"
    if "zabka" in lower or "żabka" in lower: return "Zabka"
    return "Sklep"

def get_agent(shop_name: str) -> BaseReceiptAgent:
    return SHOP_AGENTS.get(shop_name, GenericAgent)(shop_name)
