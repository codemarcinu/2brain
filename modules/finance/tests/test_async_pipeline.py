import pytest
import asyncio
import json
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "modules" / "finance"))

from unittest.mock import MagicMock, AsyncMock, patch

# Mock dependencies that might be missing in test env
sys.modules["pytesseract"] = MagicMock()
sys.modules["PIL"] = MagicMock()
# sys.modules["rapidfuzz"] = MagicMock() # We need this for the test logic, so assume it exists or install it. 
# Rapidfuzz is pure python/C ext, usually easy. Pytesseract requires binary.

from modules.finance.services.async_receipt_pipeline import AsyncReceiptPipeline
from modules.finance.utils.receipt_cache import ProductMatch

# Sample OCR text
OCR_SAMPLE_BIEDRONKA = """
Biedronka
Codziennie niskie ceny
2024-01-19
Jeronimo Martins Polska S.A.
MLEKO 3,2% LACIATE 12,99
BULKA KAJZERKA     0,99
SUMA: 13,98
"""

@pytest.fixture
def mock_brain():
    adapter = MagicMock()
    # Setup async return value
    adapter.generate_content_async = AsyncMock(return_value=json.dumps({
        "items": [
            {"nazwa": "Mleko 3.2%", "kategoria": "SPOŻYWCZE", "jednostka": "l", "cena_jedn": 12.99, "suma": 12.99},
            {"nazwa": "Bułka Kajzerka", "kategoria": "SPOŻYWCZE", "jednostka": "szt", "cena_jedn": 0.99, "suma": 0.99}
        ]
    }))
    return adapter

@pytest.mark.asyncio
async def test_pipeline_flow(mock_brain):
    """Test full flow: Cache Miss -> Fuzzy Miss -> AI Fallback"""
    
    # 1. Setup Pipeline with mocked Brain
    with patch("modules.finance.services.async_receipt_pipeline.LLMAdapter", return_value=mock_brain):
        pipeline = AsyncReceiptPipeline()
        
        # 2. Process Receipt
        result = await pipeline.process_receipt_async(OCR_SAMPLE_BIEDRONKA)
        
        # 3. Verify
        assert result['shop'] == "Biedronka"
        assert result['date'] == "2024-01-19"
        assert len(result['items']) == 2
        assert result['total_amount'] == 13.98
        
        # Verify AI was called because cache was empty
        mock_brain.generate_content_async.assert_called_once()
        print("\nTest 1 (AI Fallback): PASS")

@pytest.mark.asyncio
async def test_cache_hit_logic():
    """Test flow: Cache Hit -> No AI"""
    
    # 1. Setup Pipeline with pre-filled cache
    pipeline = AsyncReceiptPipeline()
    pipeline.brain = MagicMock() # Should not be called
    pipeline.brain.generate_content_async = AsyncMock()
    
    # Pre-fill cache
    match_milk = ProductMatch("Mleko 3.2%", "SPOŻYWCZE", "l", 1.0)
    pipeline.cache.update("MLEKO 3,2% LACIATE", match_milk, "Biedronka")
    
    match_roll = ProductMatch("Bułka Kajzerka", "SPOŻYWCZE", "szt", 1.0)
    pipeline.cache.update("BULKA KAJZERKA", match_roll, "Biedronka")
    
    # 2. Process
    result = await pipeline.process_receipt_async(OCR_SAMPLE_BIEDRONKA)
    
    # 3. Verify
    assert len(result['items']) == 2
    assert result['items'][0]['nazwa'] == "Mleko 3.2%"
    
    # AI should NOT be called (high coverage from cache)
    pipeline.brain.generate_content_async.assert_not_called()
    assert result['stats']['used_ai'] is False
    print("\nTest 2 (Cache Hit): PASS")

if __name__ == "__main__":
    # Helper to run async tests manually if pytest not avail
    loop = asyncio.new_event_loop()
    loop.run_until_complete(test_pipeline_flow(mock_brain()))
    loop.run_until_complete(test_cache_hit_logic())
    loop.close()
