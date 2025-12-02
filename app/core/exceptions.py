"""
Custom exceptions for passport processing application.
"""


class PassportProcessingException(Exception):
    """Base exception for all passport processing errors."""
    pass


class ImageValidationException(PassportProcessingException):
    """Raised when image validation fails."""
    pass


class FileUploadException(PassportProcessingException):
    """Raised when file upload has issues."""
    pass


class UnsupportedFileTypeException(FileUploadException):
    """Raised when uploaded file type is not supported."""
    pass


class UnreadableImageException(PassportProcessingException):
    """Raised when image cannot be read or decoded."""
    pass


class OCRExtractionException(PassportProcessingException):
    """Raised when OCR extraction fails."""
    pass


class PassportIDParsingException(OCRExtractionException):
    """Raised when passport ID extraction/parsing fails."""
    pass


class FaceDetectionException(PassportProcessingException):
    """Raised when face detection fails."""
    pass


class NoFaceDetectedException(FaceDetectionException):
    """Raised when no face is detected in the image."""
    pass


class MultipleFacesDetectedException(FaceDetectionException):
    """Raised when multiple faces are detected."""
    pass


class ImageProcessingException(PassportProcessingException):
    """Raised when general image processing fails."""
    pass
