# Walkthrough - Async Receipt Pipeline

I have successfully implemented the **Async Receipt Pipeline**, a high-performance, cost-effective system for processing receipts.

## 🚀 Key Improvements

- **Architecture**: Shifted from a simple linear process to a multi-stage async pipeline.
- **Caching**: Implemented a 3-tier cache (Exact Match, LRU, Shop Patterns) to instantly resolve known items.
- **Fuzzy Matching**: Added parallel CPU-bound fuzzy matching using partial_ratio.
- **Cost Reduction**: LLM (DeepSeek/Ollama) is now only invoked as a fallback when cache/fuzzy coverage is low (<30%).
- **Speed**: Expected processing time drop from ~15s to ~2s for recurring purchases.

## 📂 New Components

| Component | File | Description |
| --- | --- | --- |
| **Pipeline Service** | `modules/finance/services/async_receipt_pipeline.py` | Orchestrates the flow (Cache -> Fuzzy -> AI). |
| **Receipt Cache** | `modules/finance/utils/receipt_cache.py` | Manages persisting and looking up known products. |
| **Taxonomy Guard** | `modules/finance/utils/taxonomy.py` | Normalizes OCR text to canonical product names (from `product_taxonomy.json`). |
| **Shop Agents** | `modules/finance/utils/receipt_agents/` | Heuristics for specific shops (e.g. Biedronka) to clean text/dates. |
| **LLM Adapter** | `modules/finance/adapters/llm_adapter.py` | Async wrapper for OpenAI-compatible local LLMs. |

## 🧪 Verification

I created a unit test suite `modules/finance/tests/test_async_pipeline.py` to verify the logic.

### Test Results
- **AI Fallback**: Verified that when cache misses, the pipeline correctly calls the Mock brain.
- **Cache Hit**: Verified that when cache is pre-filled, the pipeline skips the AI call entirely.

### Manual Verification Command
To run the validation suite:
```bash
python modules/finance/tests/test_async_pipeline.py
# Or with pytest
pytest modules/finance/tests/test_async_pipeline.py
```

## 📜 Usage

The system is fully integrated into the existing flow. Just use the standard CLI or drop files into Inbox.

```bash
# Process a receipt (will now use the fast path)
python brain.py finance receipts/zakupy.jpg
```
