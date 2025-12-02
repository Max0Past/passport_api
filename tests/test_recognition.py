"""
Test script for OCR and face detection technologies.

Tests the core recognition technologies (OCR and face detection) independently
without the full API.
"""
import sys
from pathlib import Path

import cv2

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.utils.image_processing import load_image_from_bytes, image_to_base64, resize_image
from app.services.ocr_extractor import PassportOCRExtractor
from app.services.face_detector import FaceDetector
from app.core.exceptions import (
    PassportProcessingException,
    OCRExtractionException,
    FaceDetectionException,
)


def test_ocr_extraction(image_path: str) -> None:
    """
    Test OCR extraction on a single image.
    
    Args:
        image_path: Path to passport image file
    """
    print(f"\n{'='*60}")
    print(f"Testing OCR Extraction: {image_path}")
    print(f"{'='*60}")
    
    try:
        # Load image
        image = cv2.imread(image_path)
        if image is None:
            print(f"❌ Failed to load image: {image_path}")
            return
        
        print(f"✓ Image loaded successfully")
        print(f"  Image dimensions: {image.shape[1]}x{image.shape[0]}")
        
        # Resize for better processing
        resized = resize_image(image)
        print(f"  Resized dimensions: {resized.shape[1]}x{resized.shape[0]}")
        
        # Initialize OCR extractor
        ocr_extractor = PassportOCRExtractor()
        print(f"✓ OCR engine initialized")
        
        # Extract text
        text = ocr_extractor.extract_text(resized)
        print(f"✓ Text extracted successfully")
        print(f"\n--- Extracted Text ---")
        print(text[:500])  # Print first 500 chars
        if len(text) > 500:
            print(f"... ({len(text) - 500} more characters)")
        
        # Extract passport ID
        passport_id = ocr_extractor.extract_passport_id(text)
        print(f"\n✓ Passport ID extracted: {passport_id}")
        
    except OCRExtractionException as e:
        print(f"❌ OCR Extraction Error: {str(e)}")
    except Exception as e:
        print(f"❌ Unexpected Error: {str(e)}")


def test_face_detection(image_path: str) -> None:
    """
    Test face detection and cropping on a single image.
    
    Args:
        image_path: Path to passport image file
    """
    print(f"\n{'='*60}")
    print(f"Testing Face Detection: {image_path}")
    print(f"{'='*60}")
    
    try:
        # Load image
        image = cv2.imread(image_path)
        if image is None:
            print(f"❌ Failed to load image: {image_path}")
            return
        
        print(f"✓ Image loaded successfully")
        print(f"  Image dimensions: {image.shape[1]}x{image.shape[0]}")
        
        # Resize for better processing
        resized = resize_image(image)
        print(f"  Resized dimensions: {resized.shape[1]}x{resized.shape[0]}")
        
        # Initialize face detector
        face_detector = FaceDetector()
        print(f"✓ Face detector initialized")
        
        # Detect faces
        faces = face_detector.detect_faces(resized)
        print(f"✓ Face detection completed")
        print(f"  Found {len(faces)} face(s)")
        
        for i, (x, y, w, h) in enumerate(faces):
            print(f"  Face {i+1}: x={x}, y={y}, w={w}, h={h}")
        
        # Extract and crop face
        face_crop = face_detector.extract_and_crop_face(resized)
        print(f"✓ Face cropped successfully")
        print(f"  Cropped face dimensions: {face_crop.shape[1]}x{face_crop.shape[0]}")
        
        # Convert to base64
        face_base64 = image_to_base64(face_crop)
        print(f"✓ Face converted to base64")
        print(f"  Base64 string length: {len(face_base64)} characters")
        
    except FaceDetectionException as e:
        print(f"❌ Face Detection Error: {str(e)}")
    except Exception as e:
        print(f"❌ Unexpected Error: {str(e)}")


def test_full_pipeline(image_path: str) -> None:
    """
    Test the complete processing pipeline on a single image.
    
    Args:
        image_path: Path to passport image file
    """
    print(f"\n{'='*60}")
    print(f"Testing Full Pipeline: {image_path}")
    print(f"{'='*60}")
    
    try:
        # Load image
        image = cv2.imread(image_path)
        if image is None:
            print(f"❌ Failed to load image: {image_path}")
            return
        
        print(f"✓ Image loaded successfully")
        
        # Resize
        resized = resize_image(image)
        print(f"✓ Image resized: {image.shape[1]}x{image.shape[0]} → {resized.shape[1]}x{resized.shape[0]}")
        
        # Test OCR
        ocr_extractor = PassportOCRExtractor()
        passport_id = ocr_extractor.extract_passport_id_from_image(resized)
        print(f"✓ Passport ID extracted: {passport_id}")
        
        # Test face detection
        face_detector = FaceDetector()
        face_crop = face_detector.extract_and_crop_face(resized)
        print(f"✓ Face detected and cropped: {face_crop.shape[1]}x{face_crop.shape[0]}")
        
        # Convert to base64
        face_base64 = image_to_base64(face_crop)
        print(f"✓ Face converted to base64: {len(face_base64)} characters")
        
        print(f"\n✅ FULL PIPELINE SUCCESS")
        print(f"  Passport ID: {passport_id}")
        print(f"  Face image size: {face_crop.shape[1]}x{face_crop.shape[0]}")
        print(f"  Base64 length: {len(face_base64)}")
        
    except PassportProcessingException as e:
        print(f"❌ Processing Error: {str(e)}")
    except Exception as e:
        print(f"❌ Unexpected Error: {str(e)}")


def main():
    """Main test runner."""
    print("\n" + "="*60)
    print("PASSPORT RECOGNITION TEST SUITE")
    print("="*60)
    
    # Find sample data
    data_dir = Path(__file__).parent.parent / "data"
    sample_data_dir = data_dir / "Trainee Test Assignment-20251202T201105Z-3-001(1)" / "Trainee Test Assignment" / "sample_data"
    
    if not sample_data_dir.exists():
        print(f"\n❌ Sample data directory not found: {sample_data_dir}")
        return
    
    # Find all image files
    image_files = sorted(sample_data_dir.glob("*.jpeg")) + sorted(sample_data_dir.glob("*.jpg")) + sorted(sample_data_dir.glob("*.png"))
    
    if not image_files:
        print(f"\n❌ No image files found in: {sample_data_dir}")
        return
    
    print(f"\nFound {len(image_files)} image file(s)")
    
    # Test on first image only for brevity
    test_image = str(image_files[3])
    
    print(f"\nTesting on first image: {image_files[3].name}")
    
    # Run tests
    test_ocr_extraction(test_image)
    test_face_detection(test_image)
    test_full_pipeline(test_image)
    
    print(f"\n{'='*60}")
    print("TEST SUITE COMPLETED")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
