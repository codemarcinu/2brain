"""
Receipt Processor
Handles OCR, caching, and LLM extraction for receipts.
"""
import json
import logging
import asyncio
from pathlib import Path
from typing import Dict, Optional, List
import pytesseract
from PIL import Image
from shared.logging import get_logger
from config import config
from modules.finance.services.async_receipt_pipeline import AsyncReceiptPipeline

logger = get_logger(__name__)

class ReceiptProcessor:
    """Core logic for receipt processing"""

    def __init__(self):
        # Initialize the Async Pipeline
        self.pipeline = AsyncReceiptPipeline()

    def process_image(self, image_path: Path) -> Dict:
        """
        Full pipeline: Image -> OCR -> Data Extraction (Async Pipeline)
        """
        logger.info("receipt_processing_started", file=image_path.name)
        
        # 1. OCR (Sync, CPU bound)
        text = self._perform_ocr(image_path)
        if not text:
            return {"error": "OCR failed (empty text)"}
            
        logger.debug("ocr_completed", text_length=len(text))
        
        # 2. Extract Data (Async Pipeline)
        try:
            # We run the async pipeline in a synchronous context
            data = asyncio.run(self.pipeline.process_receipt_async(text))
            return data
        except Exception as e:
            logger.error("pipeline_failed", error=str(e))
            return {"error": str(e), "raw_text": text}

    def _perform_ocr(self, image_path: Path) -> str:
        """Run Tesseract OCR on image"""
        try:
            image = Image.open(image_path)
            # Basic preprocessing could be added here (contrast, greyscale)
            text = pytesseract.image_to_string(image, lang=config.ocr_lang)
            return text.strip()
        except Exception as e:
            logger.error("ocr_failed", error=str(e))
            return ""
