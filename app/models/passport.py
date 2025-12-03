"""
Data models for passport processing API responses.
"""
from dataclasses import dataclass


@dataclass
class PassportProcessingResult:
    """Result of passport image processing."""
    passport_id: str
    face_image: str
    original_filename: str | None = None
