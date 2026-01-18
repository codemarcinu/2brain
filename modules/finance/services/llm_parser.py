"""
LLM Parser do wyciągania strukturalnych danych z OCR
"""
import json
from typing import Optional, Dict
from openai import OpenAI
from shared.logging import get_logger
from config import config

logger = get_logger(__name__)


class ReceiptParser:
    """Parser paragonów używający DeepSeek/GPT"""

    def __init__(self):
        self.client = OpenAI(
            api_key=config.llm_api_key,
            base_url=config.llm_base_url
        )
        self.model = config.llm_model

    def parse_receipt(self, ocr_text: str) -> Optional[Dict]:
        """
        Parse OCR text do strukturalnego JSON

        Args:
            ocr_text: Surowy tekst z OCR

        Returns:
            Dict z shop, date, items, total
        """
        prompt = f"""You are a receipt parser. Extract structured data from this OCR text.

OCR Text:
{ocr_text}

Extract the following information:
1. Shop name
2. Purchase date (format: YYYY-MM-DD)
3. Items list (name, price, quantity)
4. Total amount
5. Tax number (NIP) if present

Return ONLY valid JSON (no markdown, no code blocks):
{{
  "shop_name": "...",
  "purchase_date": "YYYY-MM-DD",
  "total_amount": 123.45,
  "tax_number": "...",
  "items": [
    {{"name": "...", "price": 12.34, "quantity": 2}},
    ...
  ]
}}

If you cannot extract certain fields, use null. Be precise with numbers.
"""

        try:
            logger.info("llm_parsing_started")

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,  # Deterministyczne dla danych liczbowych
                max_tokens=1500
            )

            content = response.choices[0].message.content

            # Parse JSON
            # Remove markdown if present
            cleaned = content.strip()
            if cleaned.startswith('```'):
                start = cleaned.find('{')
                end = cleaned.rfind('}') + 1
                cleaned = cleaned[start:end]

            result = json.loads(cleaned)

            logger.info(
                "llm_parsing_success",
                shop=result.get('shop_name'),
                total=result.get('total_amount')
            )

            return result

        except json.JSONDecodeError as e:
            logger.error("llm_json_parse_failed", error=str(e))
            return None
        except Exception as e:
            logger.error("llm_parsing_failed", error=str(e))
            return None
