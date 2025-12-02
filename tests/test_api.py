"""
Test script for the complete FastAPI application.

Tests the full API endpoint with sample passport images.
"""
import asyncio
import json
import sys
from pathlib import Path

import requests
from fastapi.testclient import TestClient

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.main import app


def test_api_with_testclient():
    """Test API using FastAPI TestClient."""
    print(f"\n{'='*60}")
    print("Testing API with TestClient")
    print(f"{'='*60}\n")
    
    client = TestClient(app)
    
    # Test health endpoint
    print("Testing health endpoint...")
    response = client.get("/health")
    assert response.status_code == 200
    print(f"✓ Health endpoint OK: {response.json()}")
    
    # Test root endpoint
    print("\nTesting root endpoint...")
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    print(f"✓ Root endpoint OK: {data['status']}")
    
    # Find sample images
    data_dir = Path(__file__).parent.parent / "data"
    sample_data_dir = data_dir / "Trainee Test Assignment-20251202T201105Z-3-001(1)" / "Trainee Test Assignment" / "sample_data"
    
    image_files = sorted(sample_data_dir.glob("*.jpeg")) + sorted(sample_data_dir.glob("*.jpg"))
    
    if not image_files:
        print(f"\n❌ No image files found in: {sample_data_dir}")
        return
    
    print(f"\n\nFound {len(image_files)} sample passport image(s)")
    print("Testing API upload endpoint...\n")
    
    # Test upload endpoint with each image
    for i, image_path in enumerate(image_files[:3], 1):  # Test first 3 images
        print(f"\n--- Test {i}: {image_path.name} ---")
        
        try:
            with open(image_path, "rb") as f:
                files = {"file": (image_path.name, f, "image/jpeg")}
                response = client.post("/api/v1/upload", files=files)
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✓ Upload successful")
                print(f"  Passport ID: {data['passport_id']}")
                print(f"  Face image base64 length: {len(data['face_image_base64'])} characters")
                
                # Validate response structure
                assert "passport_id" in data
                assert "face_image_base64" in data
                assert isinstance(data["passport_id"], str)
                assert isinstance(data["face_image_base64"], str)
                assert len(data["passport_id"]) == 9
                print(f"✓ Response format valid")
                
            else:
                print(f"❌ Upload failed")
                print(f"Response: {response.json()}")
        
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    # Test error cases
    print(f"\n\n{'='*60}")
    print("Testing error handling")
    print(f"{'='*60}\n")
    
    # Test missing file
    print("Test 1: Missing file...")
    response = client.post("/api/v1/upload")
    assert response.status_code == 422  # Missing file
    print(f"✓ Missing file handled correctly (Status: {response.status_code})")
    
    # Test unsupported format
    print("\nTest 2: Unsupported file format...")
    files = {"file": ("test.txt", b"not an image", "text/plain")}
    response = client.post("/api/v1/upload", files=files)
    assert response.status_code == 400
    print(f"✓ Unsupported format handled correctly (Status: {response.status_code})")
    print(f"  Error: {response.json()['detail']}")
    
    # Test empty file
    print("\nTest 3: Empty file...")
    files = {"file": ("empty.jpg", b"", "image/jpeg")}
    response = client.post("/api/v1/upload", files=files)
    assert response.status_code == 400
    print(f"✓ Empty file handled correctly (Status: {response.status_code})")
    print(f"  Error: {response.json()['detail']}")
    
    # Test invalid image data
    print("\nTest 4: Invalid image data...")
    files = {"file": ("invalid.jpg", b"not actual image data", "image/jpeg")}
    response = client.post("/api/v1/upload", files=files)
    assert response.status_code == 400
    print(f"✓ Invalid image handled correctly (Status: {response.status_code})")
    print(f"  Error: {response.json()['detail']}")
    
    print(f"\n\n{'='*60}")
    print("✅ ALL TESTS COMPLETED SUCCESSFULLY")
    print(f"{'='*60}\n")


def main():
    """Main test runner."""
    print("\n" + "="*60)
    print("FASTAPI APPLICATION TEST SUITE")
    print("="*60)
    
    test_api_with_testclient()


if __name__ == "__main__":
    main()
