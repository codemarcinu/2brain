"""
Receipt Processor
Handles OCR, caching, and LLM extraction for receipts.
"""
import json
import logging
import asyncio
import io
from pathlib import Path
from typing import Dict, Optional, List
import pytesseract
from PIL import Image
from shared.logging import get_logger
from config import config
from google.cloud import vision
from services.async_receipt_pipeline import AsyncReceiptPipeline

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
        """Run OCR on image based on provider"""
        if config.ocr_provider == "google_vision":
            return self._perform_google_vision_ocr(image_path)
        else:
            return self._perform_tesseract_ocr(image_path)

    def _perform_tesseract_ocr(self, image_path: Path) -> str:
        """Run Tesseract OCR on image"""
        try:
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image, lang=config.ocr_lang)
            return text.strip()
        except Exception as e:
            logger.error("tesseract_ocr_failed", error=str(e))
            return ""

    def _perform_google_vision_ocr(self, image_path: Path) -> str:
        """Run Google Vision OCR on image"""
        try:
            client = vision.ImageAnnotatorClient()
            
            with io.open(image_path, 'rb') as image_file:
                content = image_file.read()

            image = vision.Image(content=content)
            response = client.text_detection(image=image)
            texts = response.text_annotations

            if response.error.message:
                raise Exception(f"{response.error.message}")

            if texts:
                return texts[0].description.strip()
            return ""
        except Exception as e:
            logger.error("google_vision_ocr_failed", error=str(e))
            # Fallback to Tesseract
            logger.info("falling_back_to_tesseract")
            return self._perform_tesseract_ocr(image_path)
