"""
OCR service for extracting passport ID from images.
"""
import re
from typing import Optional

import cv2
import numpy as np
from rapidocr_onnxruntime import RapidOCR

from app.core.exceptions import (
    OCRExtractionException,
    PassportIDParsingException,
)


class PassportOCRExtractor:
    """Service for extracting text and passport ID from images using RapidOCR."""
    
    # Passport ID patterns: 9 digits OR 1 letter followed by 8 digits
    PASSPORT_ID_PATTERN_DIGITS = r"\b\d{9}\b"
    PASSPORT_ID_PATTERN_LETTER = r"\b[A-Z]\d{8}\b"
    MIN_PASSPORT_ID_LENGTH = 9
    
    # Keywords to search near for passport ID
    PASSPORT_KEYWORDS = [
        "Document Number",
        "Passport No",
        "Document No", 
        "Passport Number",
    ]
    
    def __init__(self) -> None:
        """Initialize OCR engine."""
        try:
            self.ocr_engine = RapidOCR()
        except Exception as e:
            raise OCRExtractionException(
                f"Failed to initialize OCR engine: {str(e)}"
            )
    
    def _preprocess_for_ocr(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocess image for better OCR results.
        
        Args:
            image: Image as numpy array (BGR format)
            
        Returns:
            Enhanced grayscale image
        """
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(gray)
            
            return enhanced
        except Exception:
            # If enhancement fails, return grayscale version
            return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    def extract_text(self, image: np.ndarray) -> str:
        """
        Extract text from image using OCR.
        
        Args:
            image: Image as numpy array (BGR format)
            
        Returns:
            Extracted text
            
        Raises:
            OCRExtractionException: If OCR extraction fails
        """
        try:
            # Preprocess image for better OCR results
            enhanced_image = self._preprocess_for_ocr(image)
            
            # Run OCR
            result = self.ocr_engine(enhanced_image)
            
            if result is None or len(result) == 0:
                raise OCRExtractionException(
                    "No text detected in image"
                )
            
            # RapidOCR returns a tuple: (detection_results, timing_info)
            # detection_results is a list of [coordinates, text, confidence]
            detection_results = result[0]
            
            if not detection_results:
                raise OCRExtractionException(
                    "No text detected in image"
                )
            
            # Extract text from OCR results
            # Each item is [[[x1, y1], [x2, y2], ...], text, confidence]
            extracted_text = "\n".join([item[1] for item in detection_results])
            
            return extracted_text
        except OCRExtractionException:
            raise
        except Exception as e:
            raise OCRExtractionException(
                f"Error during OCR extraction: {str(e)}"
            )
    
    def extract_passport_id(self, text: str) -> str:
        """
        Extract passport ID from OCR-extracted text.
        
        The passport ID must be either:
        - 9 consecutive digits (e.g., "123456789")
        - 1 letter followed by 8 digits (e.g., "A12345678")
        
        Strategy:
        1. Search for passport ID near keywords (Document Number, Passport No, etc.)
        2. Fall back to searching entire text
        3. Validate format strictly
        
        Args:
            text: Extracted text from OCR
            
        Returns:
            Extracted passport ID
            
        Raises:
            PassportIDParsingException: If passport ID cannot be found
        """
        try:
            if not text or not isinstance(text, str):
                raise PassportIDParsingException(
                    "No text provided for passport ID extraction"
                )
            
            # Clean and normalize text
            cleaned_text = text.upper().strip()
            
            # Remove common spacing/newline issues
            cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
            
            # Strategy 1: Look for passport ID near keywords
            for keyword in self.PASSPORT_KEYWORDS:
                keyword_upper = keyword.upper()
                if keyword_upper in cleaned_text:
                    # Get text around the keyword (300 chars after)
                    keyword_pos = cleaned_text.find(keyword_upper)
                    search_region = cleaned_text[keyword_pos:keyword_pos + 300]
                    
                    # Try to find passport ID in this region
                    # First try: 9 digits
                    digit_match = re.search(self.PASSPORT_ID_PATTERN_DIGITS, search_region)
                    if digit_match:
                        return digit_match.group(0)
                    
                    # Second try: 1 letter + 8 digits
                    letter_match = re.search(self.PASSPORT_ID_PATTERN_LETTER, search_region)
                    if letter_match:
                        return letter_match.group(0)
            
            # Strategy 2: Search entire text if keyword search failed
            # First try: 9 digits
            digit_match = re.search(self.PASSPORT_ID_PATTERN_DIGITS, cleaned_text)
            if digit_match:
                return digit_match.group(0)
            
            # Second try: 1 letter + 8 digits
            letter_match = re.search(self.PASSPORT_ID_PATTERN_LETTER, cleaned_text)
            if letter_match:
                return letter_match.group(0)
            
            # If we get here, no valid passport ID was found
            raise PassportIDParsingException(
                f"No passport ID found matching required format. "
                f"Expected: 9 digits OR 1 letter + 8 digits."
            )
        except PassportIDParsingException:
            raise
        except Exception as e:
            raise PassportIDParsingException(
                f"Error parsing passport ID: {str(e)}"
            )
    
    def extract_passport_id_from_image(self, image: np.ndarray) -> str:
        """
        Extract passport ID directly from image.
        
        Args:
            image: Image as numpy array
            
        Returns:
            Extracted passport ID
            
        Raises:
            OCRExtractionException: If OCR extraction fails
            PassportIDParsingException: If passport ID parsing fails
        """
        text = self.extract_text(image)
        return self.extract_passport_id(text)
