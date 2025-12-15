"""
Test script for OCR and face detection technologies.

Tests the core recognition technologies (OCR and face detection) independently
without the full API.
"""
import sys
from pathlib import Path
import os

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
            print(f"FAIL: Failed to load image: {image_path}")
            return
        
        print(f"PASS: Image loaded successfully")
        print(f"  Image dimensions: {image.shape[1]}x{image.shape[0]}")
        
        # Resize for better processing
        resized = resize_image(image)
        print(f"  Resized dimensions: {resized.shape[1]}x{resized.shape[0]}")
        
        # Initialize OCR extractor
        ocr_extractor = PassportOCRExtractor()
        print(f"PASS: OCR engine initialized")
        
        # Extract text
        text = ocr_extractor.extract_text(resized)
        print(f"PASS: Text extracted successfully")
        print(f"\n--- Extracted Text ---")
        print(text[:500])  # Print first 500 chars
        if len(text) > 500:
            print(f"... ({len(text) - 500} more characters)")
        
        # Extract passport ID
        passport_id = ocr_extractor.extract_passport_id(text)
        print(f"\nPASS: Passport ID extracted: {passport_id}")
        
    except OCRExtractionException as e:
        print(f"FAIL: OCR Extraction Error: {str(e)}")
    except Exception as e:
        print(f"FAIL: Unexpected Error: {str(e)}")


def test_face_detection(image_path: str, output_dir: Path) -> None:
    """
    Test face detection and cropping on a single image.
    
    Args:
        image_path: Path to passport image file
        output_dir: Directory to save output photos
    """
    print(f"\n{'='*60}")
    print(f"Testing Face Detection: {image_path}")
    print(f"{'='*60}")
    
    try:
        # Load image
        image = cv2.imread(image_path)
        if image is None:
            print(f"FAIL: Failed to load image: {image_path}")
            return
        
        print(f"PASS: Image loaded successfully")
        print(f"  Image dimensions: {image.shape[1]}x{image.shape[0]}")
        
        # Resize for better processing
        resized = resize_image(image)
        print(f"  Resized dimensions: {resized.shape[1]}x{resized.shape[0]}")
        
        # Initialize face detector
        face_detector = FaceDetector()
        print(f"PASS: Face detector initialized")
        
        # Detect faces
        faces = face_detector.detect_faces(resized)
        print(f"PASS: Face detection completed")
        print(f"  Found {len(faces)} face(s)")
        
        for i, (x, y, w, h) in enumerate(faces):
            print(f"  Face {i+1}: x={x}, y={y}, w={w}, h={h}")
        
        # Extract and get full passport photo
        passport_photo = face_detector.extract_and_crop_face(resized)
        print(f"PASS: Face validated and full passport photo returned")
        print(f"  Passport photo dimensions: {passport_photo.shape[1]}x{passport_photo.shape[0]}")
        
        # Save photo to output directory
        image_name = Path(image_path).stem
        output_path = output_dir / f"{image_name}_photo.png"
        cv2.imwrite(str(output_path), passport_photo)
        print(f"PASS: Photo saved to: {output_path}")
        
        # Convert to base64
        photo_base64 = image_to_base64(passport_photo)
        print(f"PASS: Photo converted to base64")
        print(f"  Base64 string length: {len(photo_base64)} characters")
        
    except FaceDetectionException as e:
        print(f"FAIL: Face Detection Error: {str(e)}")
    except Exception as e:
        print(f"FAIL: Unexpected Error: {str(e)}")


def test_full_pipeline(image_path: str, output_dir: Path) -> None:
    """
    Test the complete processing pipeline on a single image.
    
    Args:
        image_path: Path to passport image file
        output_dir: Directory to save output photos
    """
    print(f"\n{'='*60}")
    print(f"Testing Full Pipeline: {image_path}")
    print(f"{'='*60}")
    
    try:
        # Load image
        image = cv2.imread(image_path)
        if image is None:
            print(f"FAIL: Failed to load image: {image_path}")
            return
        
        print(f"PASS: Image loaded successfully")
        
        # Resize
        resized = resize_image(image)
        print(f"PASS: Image resized: {image.shape[1]}x{image.shape[0]} -> {resized.shape[1]}x{resized.shape[0]}")
        
        # Test OCR
        ocr_extractor = PassportOCRExtractor()
        passport_id = ocr_extractor.extract_passport_id_from_image(resized)
        print(f"PASS: Passport ID extracted: {passport_id}")
        
        # Test face detection (returns cropped face)
        face_detector = FaceDetector()
        face_photo = face_detector.extract_and_crop_face(resized)
        print(f"PASS: Face detected and cropped: {face_photo.shape[1]}x{face_photo.shape[0]}")
        
        # Save results to output directory
        image_name = Path(image_path).stem
        
        id_output_path = output_dir / f"{image_name}_passport_id.txt"
        with open(id_output_path, 'w') as f:
            f.write(passport_id)
        
        print(f"PASS: Results saved:")
        print(f"  Passport ID: {id_output_path}")
        
        # Convert to base64
        face_base64 = image_to_base64(face_photo)
        print(f"PASS: Face converted to base64: {len(face_base64)} characters")
        
        print(f"\nSUCCESS: FULL PIPELINE COMPLETED")
        print(f"  Passport ID: {passport_id}")
        print(f"  Face size: {face_photo.shape[1]}x{face_photo.shape[0]}")
        print(f"  Base64 length: {len(face_base64)}")
        
    except PassportProcessingException as e:
        print(f"FAIL: Processing Error: {str(e)}")
    except Exception as e:
        print(f"FAIL: Unexpected Error: {str(e)}")


def main():
    """Main test runner."""
    print("\n" + "="*60)
    print("PASSPORT RECOGNITION TEST SUITE")
    print("="*60)
    
    # Create output directory
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)
    print(f"\nOutput directory: {output_dir}")
    
    # Find sample data
    data_dir = Path(__file__).parent.parent / "data"
    sample_data_dir = data_dir / "sample_data"
    
    if not sample_data_dir.exists():
        print(f"\nFAIL: Sample data directory not found: {sample_data_dir}")
        return
    
    # Find all image files
    image_files = sorted(sample_data_dir.glob("*.jpeg")) + sorted(sample_data_dir.glob("*.jpg")) + sorted(sample_data_dir.glob("*.png"))
    
    if not image_files:
        print(f"\nFAIL: No image files found in: {sample_data_dir}")
        return
    
    print(f"\nFound {len(image_files)} image file(s)")
    
    # Test on first image only for brevity
    selected_image_index = None
    while selected_image_index is None:
        try:
            max_index_display = len(image_files)
            user_input = input(f"Введіть номер фото для тестування (від 1 до {max_index_display}): ")
            photo_number = int(user_input)

            if 1 <= photo_number <= max_index_display:
                selected_image_index = photo_number
                test_image = image_files[selected_image_index]
                print(f"\nТестування на фото №{photo_number}: {image_files[selected_image_index].name}")
            else:
                print(f"Помилка: Номер фото має бути від 1 до {max_index_display}.")
        except ValueError:
            print("Помилка: Будь ласка, введіть ціле число.")
    
    # Run tests
    test_ocr_extraction(test_image)
    test_face_detection(test_image, output_dir)
    test_full_pipeline(test_image, output_dir)
    
    print(f"\n{'='*60}")
    print("TEST SUITE COMPLETED")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
