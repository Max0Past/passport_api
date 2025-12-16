"""
API routes for passport processing.
"""
from typing import Optional

from fastapi import APIRouter, File, UploadFile, HTTPException, status

from app.core.exceptions import (
    PassportProcessingException,
    UnsupportedFileTypeException,
    UnreadableImageException,
    OCRExtractionException,
    PassportIDParsingException,
    FaceDetectionException,
    NoFaceDetectedException,
    MultipleFacesDetectedException,
)
from app.services.processor import PassportProcessor
from app.utils.image_processing import validate_file_format, load_image_from_bytes, MAX_FILE_SIZE_MB


# Initialize router and processor
router = APIRouter(prefix="/api/v1", tags=["passport"])
processor = PassportProcessor()


class PassportResponse:
    """Response model for passport processing."""
    def __init__(self, passport_id: str, face_image: str):
        self.passport_id = passport_id
        self.face_image = face_image


@router.post("/upload")
def upload_passport(file: UploadFile = File(...)):
    """
    Upload and process a passport image.
    
    Extract passport ID and detect/crop face region.
    
    Args:
        file: Passport image file (JPG, PNG)
        
    Returns:
        JSON response with passport_id and face_image (base64-encoded)
        
    Raises:
        400: Bad request (missing file, unsupported format, unreadable image)
        422: Unprocessable entity (data extraction or face detection errors)
        500: Internal server error
    """
    try:
        # Validate file is provided
        if not file or not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No file provided in upload request"
            )
        
        # Validate file format
        try:
            validate_file_format(file.filename)
        except UnsupportedFileTypeException as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
            
        # Validate file size
        try:
            file.file.seek(0, 2)
            file_size = file.file.tell()
            file.file.seek(0)
            
            if file_size > MAX_FILE_SIZE_MB * 1024 * 1024:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File too large. Maximum size allowed is {MAX_FILE_SIZE_MB}MB"
                )
        except Exception as e:
            if isinstance(e, HTTPException):
                raise
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error checking file size: {str(e)}"
            )
        
        # Read file content
        file_content = file.file.read()
        
        if not file_content:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file is empty"
            )
        
        # Load and validate image
        try:
            image = load_image_from_bytes(file_content)
        except UnreadableImageException as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        
        # Process passport image
        try:
            result = processor.process_passport_image(image, file.filename)
        except (PassportIDParsingException, OCRExtractionException) as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Data extraction failed: {str(e)}"
            )
        except (NoFaceDetectedException, MultipleFacesDetectedException) as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Face detection failed: {str(e)}"
            )
        except FaceDetectionException as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Face detection error: {str(e)}"
            )
        except PassportProcessingException as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Processing error: {str(e)}"
            )
        
        # Return response
        return {
            "passport_id": result.passport_id,
            "face_image": result.face_image
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )
