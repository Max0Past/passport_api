#!/usr/bin/env python3
"""
Demo script showing how to use the Passport Processing API.

This script demonstrates:
1. Starting the API server
2. Sending requests to the API
3. Handling responses
4. Saving extracted face images
"""
import base64
import json
import time
from pathlib import Path

import requests
from PIL import Image
from io import BytesIO


def demo_api_usage():
    """Demonstrate API usage with a sample passport image."""
    
    print("\n" + "="*60)
    print("PASSPORT PROCESSING API DEMO")
    print("="*60)
    
    # API endpoint
    api_url = "http://localhost:8000/api/v1/upload"
    
    # Find sample passport image
    data_dir = Path(__file__).parent / "data"
    sample_data_dir = data_dir / "Trainee Test Assignment-20251202T201105Z-3-001(1)" / "Trainee Test Assignment" / "sample_data"
    
    image_files = sorted(sample_data_dir.glob("*.jpeg"))
    
    if not image_files:
        print("\n❌ No sample images found. Please ensure sample data is in data/ folder")
        return
    
    # Test with first 3 images
    for i, image_path in enumerate(image_files[:3], 1):
        print(f"\n--- Processing Image {i}: {image_path.name} ---")
        
        try:
            # Upload image
            print(f"Uploading to {api_url}...")
            
            with open(image_path, "rb") as f:
                files = {"file": (image_path.name, f, "image/jpeg")}
                response = requests.post(api_url, files=files, timeout=30)
            
            # Check response
            if response.status_code != 200:
                print(f"❌ Request failed with status {response.status_code}")
                print(f"   Error: {response.json().get('detail', 'Unknown error')}")
                continue
            
            # Parse response
            data = response.json()
            passport_id = data["passport_id"]
            face_base64 = data["face_image_base64"]
            
            print(f"✓ Success!")
            print(f"  Passport ID: {passport_id}")
            print(f"  Face image size: {len(face_base64)} characters (base64)")
            
            # Decode and save face image
            face_image_bytes = base64.b64decode(face_base64)
            face_image = Image.open(BytesIO(face_image_bytes))
            
            # Save with meaningful filename
            output_path = Path(f"extracted_face_{i}_{passport_id}.png")
            face_image.save(output_path)
            print(f"  Saved face image: {output_path}")
            print(f"  Face image dimensions: {face_image.size}")
            
        except requests.exceptions.ConnectionError:
            print(f"❌ Connection error: Could not reach {api_url}")
            print(f"   Please ensure the API server is running: python run_api.py")
        except requests.exceptions.Timeout:
            print(f"❌ Request timeout")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    print("\n" + "="*60)
    print("DEMO COMPLETED")
    print("="*60 + "\n")


if __name__ == "__main__":
    print("\nPassport Processing API Demo")
    print("\nBefore running this demo, please ensure the API server is running:")
    print("  python run_api.py")
    print("\nWaiting for API to be ready...\n")
    
    # Check if API is available
    max_retries = 5
    for attempt in range(max_retries):
        try:
            response = requests.get("http://localhost:8000/health", timeout=2)
            if response.status_code == 200:
                print("✓ API is ready!")
                demo_api_usage()
                break
        except requests.exceptions.RequestException:
            if attempt < max_retries - 1:
                print(f"API not ready yet (attempt {attempt + 1}/{max_retries})... retrying in 2 seconds")
                time.sleep(2)
            else:
                print("\n❌ Could not connect to API server")
                print("Please start the API server with: python run_api.py")
