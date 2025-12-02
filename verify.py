#!/usr/bin/env python3
"""
Comprehensive verification script for the Passport Processing API.

This script verifies:
1. All required modules can be imported
2. All dependencies are installed
3. Core functionality works correctly
"""
import sys
from pathlib import Path


def check_imports():
    """Check that all required modules can be imported."""
    print("\n" + "="*60)
    print("CHECKING MODULE IMPORTS")
    print("="*60 + "\n")
    
    modules_to_check = [
        ("fastapi", "FastAPI"),
        ("uvicorn", "Uvicorn"),
        ("cv2", "OpenCV"),
        ("numpy", "NumPy"),
        ("PIL", "Pillow"),
        ("rapidocr_onnxruntime", "RapidOCR"),
        ("requests", "Requests"),
        ("httpx", "HTTPX"),
    ]
    
    all_ok = True
    for module_name, display_name in modules_to_check:
        try:
            __import__(module_name)
            print(f"✓ {display_name:<20} OK")
        except ImportError:
            print(f"❌ {display_name:<20} FAILED - Not installed")
            all_ok = False
    
    return all_ok


def check_app_modules():
    """Check that all application modules can be imported."""
    print("\n" + "="*60)
    print("CHECKING APPLICATION MODULES")
    print("="*60 + "\n")
    
    sys.path.insert(0, str(Path(__file__).parent))
    
    modules_to_check = [
        ("app.core.exceptions", "Exceptions"),
        ("app.models.passport", "Models"),
        ("app.utils.image_processing", "Image Processing"),
        ("app.services.ocr_extractor", "OCR Extractor"),
        ("app.services.face_detector", "Face Detector"),
        ("app.services.processor", "Processor"),
        ("app.api.routes", "API Routes"),
        ("app.main", "Main App"),
    ]
    
    all_ok = True
    for module_name, display_name in modules_to_check:
        try:
            __import__(module_name)
            print(f"✓ {display_name:<25} OK")
        except ImportError as e:
            print(f"❌ {display_name:<25} FAILED - {str(e)}")
            all_ok = False
    
    return all_ok


def check_services():
    """Check that services can be instantiated."""
    print("\n" + "="*60)
    print("CHECKING SERVICE INSTANTIATION")
    print("="*60 + "\n")
    
    sys.path.insert(0, str(Path(__file__).parent))
    
    try:
        from app.services.ocr_extractor import PassportOCRExtractor
        ocr = PassportOCRExtractor()
        print(f"✓ OCR Extractor initialized successfully")
    except Exception as e:
        print(f"❌ OCR Extractor failed: {str(e)}")
        return False
    
    try:
        from app.services.face_detector import FaceDetector
        detector = FaceDetector()
        print(f"✓ Face Detector initialized successfully")
    except Exception as e:
        print(f"❌ Face Detector failed: {str(e)}")
        return False
    
    try:
        from app.services.processor import PassportProcessor
        processor = PassportProcessor()
        print(f"✓ Passport Processor initialized successfully")
    except Exception as e:
        print(f"❌ Passport Processor failed: {str(e)}")
        return False
    
    return True


def check_project_structure():
    """Check that all required files and directories exist."""
    print("\n" + "="*60)
    print("CHECKING PROJECT STRUCTURE")
    print("="*60 + "\n")
    
    required_files = [
        "app/main.py",
        "app/core/exceptions.py",
        "app/models/passport.py",
        "app/api/routes.py",
        "app/services/ocr_extractor.py",
        "app/services/face_detector.py",
        "app/services/processor.py",
        "app/utils/image_processing.py",
        "tests/test_api.py",
        "tests/test_recognition.py",
        "requirements.txt",
        "README.md",
        "run_api.py",
    ]
    
    base_path = Path(__file__).parent
    all_ok = True
    
    for file_path in required_files:
        full_path = base_path / file_path
        if full_path.exists():
            print(f"✓ {file_path:<40} OK")
        else:
            print(f"❌ {file_path:<40} MISSING")
            all_ok = False
    
    return all_ok


def check_sample_data():
    """Check that sample data exists."""
    print("\n" + "="*60)
    print("CHECKING SAMPLE DATA")
    print("="*60 + "\n")
    
    base_path = Path(__file__).parent
    sample_data_dir = base_path / "data" / "Trainee Test Assignment-20251202T201105Z-3-001(1)" / "Trainee Test Assignment" / "sample_data"
    
    if sample_data_dir.exists():
        image_files = list(sample_data_dir.glob("*.jpeg")) + list(sample_data_dir.glob("*.jpg")) + list(sample_data_dir.glob("*.png"))
        if image_files:
            print(f"✓ Sample data directory exists")
            print(f"✓ Found {len(image_files)} sample passport images")
            return True
        else:
            print(f"❌ No sample images found in {sample_data_dir}")
            return False
    else:
        print(f"❌ Sample data directory not found: {sample_data_dir}")
        return False


def main():
    """Run all checks."""
    print("\n" + "="*60)
    print("PASSPORT PROCESSING API - VERIFICATION")
    print("="*60)
    
    results = []
    
    # Run checks
    results.append(("Dependencies", check_imports()))
    results.append(("Project Structure", check_project_structure()))
    results.append(("Application Modules", check_app_modules()))
    results.append(("Service Instantiation", check_services()))
    results.append(("Sample Data", check_sample_data()))
    
    # Summary
    print("\n" + "="*60)
    print("VERIFICATION SUMMARY")
    print("="*60 + "\n")
    
    all_passed = True
    for check_name, result in results:
        status = "✓ PASS" if result else "❌ FAIL"
        print(f"{check_name:<30} {status}")
        if not result:
            all_passed = False
    
    print("\n" + "="*60)
    
    if all_passed:
        print("✅ ALL CHECKS PASSED - API IS READY TO USE")
        print("\nNext steps:")
        print("1. Start the API: python run_api.py")
        print("2. Access API docs: http://localhost:8000/docs")
        print("3. Run tests: python tests/test_api.py")
        print("4. Try demo: python demo.py")
    else:
        print("❌ SOME CHECKS FAILED - PLEASE FIX ISSUES ABOVE")
    
    print("="*60 + "\n")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
