"""
Data models for passport processing API responses.
"""
from dataclasses import dataclass


@dataclass
class PassportProcessingResult:
    """Result of passport image processing."""
    passport_id: str
    face_image_base64: str
    original_filename: str | None = None
