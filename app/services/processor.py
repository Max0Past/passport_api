"""
Main processor service that coordinates OCR extraction and face detection.
"""
import numpy as np

from app.core.exceptions import PassportProcessingException
from app.models.passport import PassportProcessingResult
from app.services.ocr_extractor import PassportOCRExtractor
from app.services.face_detector import FaceDetector
from app.utils.image_processing import image_to_base64, resize_image


class PassportProcessor:
    """Coordinator service for passport image processing."""
    
    def __init__(self) -> None:
        """Initialize the processor with OCR and face detection services."""
        self.ocr_extractor = PassportOCRExtractor()
        self.face_detector = FaceDetector()
    
    def process_passport_image(
        self,
        image: np.ndarray,
        original_filename: str | None = None
    ) -> PassportProcessingResult:
        """
        Process passport image to extract ID and face.
        
        Args:
            image: Image as numpy array (BGR format)
            original_filename: Original filename (optional)
            
        Returns:
            PassportProcessingResult with extracted passport ID and face image
            
        Raises:
            PassportProcessingException: If processing fails
        """
        try:
            # Resize image if needed for better processing
            resized_image = resize_image(image)
            
            # Extract passport ID
            passport_id = self.ocr_extractor.extract_passport_id_from_image(resized_image)
            
            # Extract and crop face
            face_crop = self.face_detector.extract_and_crop_face(resized_image)
            
            # Convert face to base64
            face_base64 = image_to_base64(face_crop)
            
            # Create result object
            result = PassportProcessingResult(
                passport_id=passport_id,
                face_image_base64=face_base64,
                original_filename=original_filename
            )
            
            return result
        except PassportProcessingException:
            raise
        except Exception as e:
            raise PassportProcessingException(
                f"Unexpected error during passport processing: {str(e)}"
            )
