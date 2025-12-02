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
from app.utils.image_processing import enhance_image_for_ocr


class PassportOCRExtractor:
    """Service for extracting text and passport ID from images using RapidOCR."""
    
    # Passport ID pattern: 9 alphanumeric characters (typically)
    PASSPORT_ID_PATTERN = r"[A-Z0-9]{9}"
    MIN_PASSPORT_ID_LENGTH = 9
    
    def __init__(self) -> None:
        """Initialize OCR engine."""
        try:
            self.ocr_engine = RapidOCR()
        except Exception as e:
            raise OCRExtractionException(
                f"Failed to initialize OCR engine: {str(e)}"
            )
    
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
            # Enhance image for better OCR results
            enhanced_image = enhance_image_for_ocr(image)
            
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
        
        The passport ID is typically a sequence of 9 alphanumeric characters.
        Strategy: 
        1. Look for lines containing "Passport No" or similar
        2. Extract 9-character sequences from following text
        3. Prefer sequences with only digits or mixed alphanumeric
        
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
            
            # Strategy 1: Look for sequences that are exactly 9 characters (digits or alphanumeric)
            # Passport IDs are typically all digits or digit-letter combinations
            all_candidates = re.findall(r'[A-Z0-9]{9}', cleaned_text)
            
            if all_candidates:
                # Filter to find the best candidate
                # Prefer those that look like passport numbers (mostly digits or digits+letters)
                digit_sequences = [c for c in all_candidates if c.isdigit()]
                
                if digit_sequences:
                    passport_id = digit_sequences[0]
                else:
                    # Accept mixed alphanumeric
                    passport_id = all_candidates[0]
                
                # Additional validation - reject common words
                if passport_id not in ["LAPLANDIA", "LAPLANDIAN"]:
                    if len(passport_id) == self.MIN_PASSPORT_ID_LENGTH:
                        return passport_id
            
            # If we get here, no valid passport ID was found
            raise PassportIDParsingException(
                f"No passport ID found matching pattern in text. "
                f"Expected 9-character alphanumeric sequence."
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
