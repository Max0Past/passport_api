"""
Image processing utilities for passport recognition.
"""
import base64
from io import BytesIO
from typing import Tuple

import cv2
import numpy as np
from PIL import Image

from app.core.exceptions import (
    ImageProcessingException,
    UnreadableImageException,
    UnsupportedFileTypeException,
)


SUPPORTED_FORMATS = {".jpg", ".jpeg", ".png", ".bmp", ".gif"}
MAX_FILE_SIZE_MB = 10


def validate_file_format(filename: str) -> None:
    """
    Validate that the uploaded file has a supported format.
    
    Args:
        filename: Name of the uploaded file
        
    Raises:
        UnsupportedFileTypeException: If file format is not supported
    """
    file_extension = "." + filename.rsplit(".", 1)[-1].lower()
    if file_extension not in SUPPORTED_FORMATS:
        raise UnsupportedFileTypeException(
            f"Unsupported file format: {file_extension}. "
            f"Supported formats: {', '.join(SUPPORTED_FORMATS)}"
        )


def load_image_from_bytes(image_bytes: bytes) -> np.ndarray:
    """
    Load image from bytes and convert to OpenCV format.
    
    Args:
        image_bytes: Raw image bytes
        
    Returns:
        Image as numpy array in BGR format (OpenCV format)
        
    Raises:
        UnreadableImageException: If image cannot be decoded
    """
    try:
        # Convert bytes to numpy array
        nparr = np.frombuffer(image_bytes, np.uint8)
        # Decode image
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            raise UnreadableImageException(
                "Failed to decode image. File may be corrupted or invalid."
            )
        
        return image
    except Exception as e:
        if isinstance(e, UnreadableImageException):
            raise
        raise UnreadableImageException(
            f"Error reading image: {str(e)}"
        )


def get_image_dimensions(image: np.ndarray) -> Tuple[int, int]:
    """
    Get image dimensions.
    
    Args:
        image: Image as numpy array
        
    Returns:
        Tuple of (height, width)
    """
    return image.shape[:2]


def crop_image(
    image: np.ndarray,
    x: int,
    y: int,
    width: int,
    height: int
) -> np.ndarray:
    """
    Crop a region from image.
    
    Args:
        image: Image as numpy array
        x: Top-left x coordinate
        y: Top-left y coordinate
        width: Crop width
        height: Crop height
        
    Returns:
        Cropped image
        
    Raises:
        ImageProcessingException: If crop region is invalid
    """
    try:
        # Ensure coordinates are within bounds
        y = max(0, y)
        x = max(0, x)
        y_end = min(image.shape[0], y + height)
        x_end = min(image.shape[1], x + width)
        
        if y >= y_end or x >= x_end:
            raise ImageProcessingException(
                "Crop region is completely out of bounds"
            )
        
        cropped = image[y:y_end, x:x_end]
        return cropped
    except ImageProcessingException:
        raise
    except Exception as e:
        raise ImageProcessingException(
            f"Error cropping image: {str(e)}"
        )


def image_to_base64(image: np.ndarray) -> str:
    """
    Convert OpenCV image to base64 string.
    
    Args:
        image: Image as numpy array (BGR format)
        
    Returns:
        Base64 encoded string
        
    Raises:
        ImageProcessingException: If encoding fails
    """
    try:
        # Encode image to PNG format in memory
        _, buffer = cv2.imencode(".png", image)
        image_bytes = buffer.tobytes()
        # Convert to base64
        base64_str = base64.b64encode(image_bytes).decode("utf-8")
        return base64_str
    except Exception as e:
        raise ImageProcessingException(
            f"Error converting image to base64: {str(e)}"
        )


def resize_image(
    image: np.ndarray,
    max_width: int = 1920,
    max_height: int = 1080
) -> np.ndarray:
    """
    Resize image if it exceeds maximum dimensions.
    
    Args:
        image: Image as numpy array
        max_width: Maximum width
        max_height: Maximum height
        
    Returns:
        Resized image if needed, otherwise original
    """
    height, width = image.shape[:2]
    
    if width <= max_width and height <= max_height:
        return image
    
    # Calculate scaling factor
    scale = min(max_width / width, max_height / height)
    new_width = int(width * scale)
    new_height = int(height * scale)
    
    resized = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
    return resized
