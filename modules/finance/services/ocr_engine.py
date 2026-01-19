"""
OCR Engine using Tesseract
"""
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import cv2
import numpy as np
from pathlib import Path
from shared.logging import get_logger

logger = get_logger(__name__)


class OCREngine:
    """Wrapper dla Tesseract OCR"""

    def __init__(self, language: str = "pol+eng", dpi: int = 300):
        self.language = language
        self.dpi = dpi

    def preprocess_image(self, image: Image.Image) -> Image.Image:
        """
        Preprocessing obrazu dla lepszego OCR
        - Grayscale
        - Contrast enhancement
        - Denoising
        - Thresholding
        """
        # Convert PIL to OpenCV
        img_array = np.array(image)

        # Grayscale
        if len(img_array.shape) == 3:
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        else:
            gray = img_array

        # Denoise
        denoised = cv2.fastNlMeansDenoising(gray)

        # Adaptive threshold (lepiej radzi sobie z nierónym oświetleniem)
        thresh = cv2.adaptiveThreshold(
            denoised,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            11,
            2
        )

        # Convert back to PIL
        return Image.fromarray(thresh)

    def extract_text(self, image_path: Path) -> str:
        """
        Wyciągnij tekst z obrazu

        Args:
            image_path: Ścieżka do zdjęcia paragonu

        Returns:
            Surowy tekst z OCR
        """
        try:
            logger.info("ocr_started", image=image_path.name)

            # Load image
            image = Image.open(image_path)

            # Preprocessing
            processed = self.preprocess_image(image)

            # OCR
            custom_config = f'--oem 3 --psm 6 -l {self.language}'
            text = pytesseract.image_to_string(
                processed,
                config=custom_config
            )

            logger.info(
                "ocr_completed",
                image=image_path.name,
                text_length=len(text)
            )

            return text

        except Exception as e:
            logger.error("ocr_failed", image=image_path.name, error=str(e))
            return ""
