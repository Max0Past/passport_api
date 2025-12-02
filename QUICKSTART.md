# Quick Start Guide

## Prerequisites

- Python 3.9 or higher
- pip (Python package manager)

## Installation & Setup

### 1. Install Dependencies

```bash
cd /home/max/Projects/passport_api
pip install -r requirements.txt
```

### 2. Verify Installation

```bash
python verify.py
```

You should see:
```
✅ ALL CHECKS PASSED - API IS READY TO USE
```

## Running the Application

### Option 1: Start the API Server

```bash
python run_api.py
```

The API will be available at:
- **Main API**: http://localhost:8000
- **Interactive Docs (Swagger UI)**: http://localhost:8000/docs
- **Alternative Docs (ReDoc)**: http://localhost:8000/redoc

### Option 2: Run with Custom Host/Port

```bash
python run_api.py --host 0.0.0.0 --port 8080
```

### Option 3: Development Mode (with auto-reload)

```bash
python run_api.py --reload
```

## Testing

### Test Recognition Technologies

Test OCR and face detection independently:

```bash
python tests/test_recognition.py
```

### Test Complete API

Test the API endpoint with error handling:

```bash
python tests/test_api.py
```

### Demo with Running API

In a separate terminal while API is running:

```bash
python demo.py
```

## API Usage Examples

### Using curl

```bash
curl -X POST "http://localhost:8000/api/v1/upload" \
  -H "accept: application/json" \
  -F "file=@/path/to/passport.jpg"
```

### Using Python

```python
import requests
import base64
from PIL import Image
from io import BytesIO

# Upload passport image
with open("passport.jpg", "rb") as f:
    files = {"file": f}
    response = requests.post("http://localhost:8000/api/v1/upload", files=files)

if response.status_code == 200:
    data = response.json()
    
    # Get passport ID
    passport_id = data["passport_id"]
    print(f"Passport ID: {passport_id}")
    
    # Decode and save face image
    face_base64 = data["face_image_base64"]
    face_image = Image.open(BytesIO(base64.b64decode(face_base64)))
    face_image.save("extracted_face.png")
    print("Face image saved!")
```

## Response Format

### Success (200 OK)

```json
{
  "passport_id": "728491530",
  "face_image_base64": "iVBORw0KGgoAAAANSUhEUgAAAAUA..."
}
```

### Error (400 Bad Request)

```json
{
  "detail": "Unsupported file format: .txt. Supported formats: .png, .gif, .jpeg, .bmp, .jpg"
}
```

### Error (422 Unprocessable Entity)

```json
{
  "detail": "Data extraction failed: No passport ID found..."
}
```

## Supported Image Formats

- JPEG (.jpg, .jpeg)
- PNG (.png)
- BMP (.bmp)
- GIF (.gif)

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError: No module named 'rapidocr_onnxruntime'` | Run: `pip install -r requirements.txt` |
| API won't start | Check if port 8000 is already in use. Use: `python run_api.py --port 8080` |
| "No face detected" error | Ensure image has good lighting and face is clearly visible |
| Wrong passport ID extracted | Check image quality; OCR accuracy depends on clear text visibility |
| Connection refused when testing | Ensure API server is running: `python run_api.py` |

## Project Structure Overview

```
app/
├── main.py              # FastAPI application
├── api/
│   └── routes.py        # API endpoints
├── core/
│   └── exceptions.py    # Custom exceptions
├── models/
│   └── passport.py      # Data models
├── services/
│   ├── processor.py     # Main coordinator
│   ├── ocr_extractor.py # OCR service
│   └── face_detector.py # Face detection service
└── utils/
    └── image_processing.py # Image utilities

tests/
├── test_api.py          # API endpoint tests
└── test_recognition.py  # Recognition technology tests
```

## Key Features

✓ Extract 9-character passport IDs
✓ Detect and crop facial regions
✓ Return face images as base64
✓ Comprehensive error handling
✓ Type-annotated code
✓ Single-responsibility modules
✓ Full test coverage

## Performance Notes

- Images larger than 1920x1080 are automatically resized
- OCR processing typically takes 1-3 seconds per image
- Face detection typically takes <1 second
- Full processing usually completes in 2-5 seconds
- Base64 encoding adds ~33% to response size

## Next Steps

1. Start the API: `python run_api.py`
2. Open browser: http://localhost:8000/docs
3. Try uploading a passport image
4. View extracted passport ID and face image
5. Integrate into your application!

## Support

For detailed documentation, see `README.md`.

For API documentation in browser, visit: http://localhost:8000/docs

---

**Ready to process passports!** 🚀
