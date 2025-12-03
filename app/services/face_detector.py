"""
Face detection service for extracting and cropping face regions from passport images.
"""
from typing import Tuple

import cv2
import numpy as np

from app.core.exceptions import (
    FaceDetectionException,
    NoFaceDetectedException,
    MultipleFacesDetectedException,
)


class FaceDetector:
    """Service for detecting and cropping faces from images."""
    
    # Use pre-trained cascade classifier for face detection
    CASCADE_PATH = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    
    # Face detection parameters
    SCALE_FACTOR = 1.1
    MIN_NEIGHBORS = 5
    MIN_FACE_SIZE = (50, 50)
    
    def __init__(self) -> None:
        """Initialize face detector with cascade classifier."""
        try:
            self.face_cascade = cv2.CascadeClassifier(self.CASCADE_PATH)
            
            if self.face_cascade.empty():
                raise FaceDetectionException(
                    "Failed to load face cascade classifier"
                )
        except Exception as e:
            if isinstance(e, FaceDetectionException):
                raise
            raise FaceDetectionException(
                f"Error initializing face detector: {str(e)}"
            )
    
    def _preprocess_for_face_detection(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocess image for face detection.
        
        Args:
            image: Image as numpy array (BGR format)
            
        Returns:
            Grayscale image for face detection
        """
        # Convert to grayscale for detection
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return gray
    
    def detect_faces(self, image: np.ndarray) -> list[Tuple[int, int, int, int]]:
        """
        Detect faces in image using cascade classifier.
        
        Args:
            image: Image as numpy array (BGR format)
            
        Returns:
            List of face rectangles as (x, y, width, height) tuples
            
        Raises:
            FaceDetectionException: If detection fails
        """
        try:
            # Preprocess image for detection
            gray = self._preprocess_for_face_detection(image)
            
            # Detect faces
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=self.SCALE_FACTOR,
                minNeighbors=self.MIN_NEIGHBORS,
                minSize=self.MIN_FACE_SIZE,
            )
            
            # Convert to list of tuples
            faces_list = [(int(x), int(y), int(w), int(h)) for x, y, w, h in faces]
            
            return faces_list
        except Exception as e:
            raise FaceDetectionException(
                f"Error during face detection: {str(e)}"
            )
    
    def validate_face_detection(self, faces: list) -> None:
        """
        Validate that exactly one face was detected.
        
        Args:
            faces: List of detected faces
            
        Raises:
            NoFaceDetectedException: If no faces are detected
            MultipleFacesDetectedException: If multiple faces are detected
        """
        if len(faces) == 0:
            raise NoFaceDetectedException(
                "No face detected in the passport image"
            )
        
        if len(faces) > 1:
            raise MultipleFacesDetectedException(
                f"Multiple faces detected ({len(faces)}). "
                "Expected exactly one face in passport image."
            )
    
    def crop_face(
        self,
        image: np.ndarray,
        x: int,
        y: int,
        width: int,
        height: int,
        padding_percent: float = 0.1
    ) -> np.ndarray:
        """
        Crop face region from image with optional padding.
        
        Args:
            image: Image as numpy array
            x: Face region x coordinate
            y: Face region y coordinate
            width: Face region width
            height: Face region height
            padding_percent: Padding as percentage of face size
            
        Returns:
            Cropped face image
            
        Raises:
            FaceDetectionException: If cropping fails
        """
        try:
            # Calculate padding
            padding_x = int(width * padding_percent)
            padding_y = int(height * padding_percent)
            
            # Calculate crop boundaries
            crop_x = max(0, x - padding_x)
            crop_y = max(0, y - padding_y)
            crop_x_end = min(image.shape[1], x + width + padding_x)
            crop_y_end = min(image.shape[0], y + height + padding_y)
            
            # Crop the face
            face_crop = image[crop_y:crop_y_end, crop_x:crop_x_end]
            
            if face_crop.size == 0:
                raise FaceDetectionException(
                    "Cropped face region is empty"
                )
            
            return face_crop
        except FaceDetectionException:
            raise
        except Exception as e:
            raise FaceDetectionException(
                f"Error cropping face: {str(e)}"
            )
    
    def extract_and_crop_face(
        self,
        image: np.ndarray,
        padding_percent: float = 0.1
    ) -> np.ndarray:
        """
        Detect and crop a single face from image.
        
        Args:
            image: Image as numpy array
            padding_percent: Padding around face as percentage
            
        Returns:
            Cropped face image
            
        Raises:
            FaceDetectionException: If detection fails
            NoFaceDetectedException: If no face is found
            MultipleFacesDetectedException: If multiple faces are found
        """
        # Detect faces to validate that exactly one face exists
        faces = self.detect_faces(image)
        self.validate_face_detection(faces)
        
        # Get the first (and only) face
        x, y, width, height = faces[0]
        
        # Crop and return the face
        face_crop = self.crop_face(image, x, y, width, height, padding_percent)
        
        return face_crop
