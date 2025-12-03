# Passport Processing API

A FastAPI application that processes passport images to extract passport identifiers and detect/crop face regions. The application combines OCR (Optical Character Recognition) technology with face detection to automatically extract key information from passport photos.

## Features

- **Passport ID Extraction**: Automatically extracts passport identifiers (9 digits or 1 letter + 8 digits) using RapidOCR with keyword-based search
- **Face Detection**: Detects and crops facial regions from passport images using Haar Cascade classifiers
- **Base64 Encoding**: Returns cropped face images as base64-encoded strings for easy integration
- **Robust Error Handling**: Comprehensive error handling for various failure scenarios
- **Well-Structured Code**: Single-responsibility modules with clear separation of concerns
- **Type Annotations**: Full type hints for better code clarity and IDE support

## Project Structure

```
passport_api/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py           # API endpoint definitions
│   ├── core/
│   │   ├── __init__.py
│   │   └── exceptions.py       # Custom exception classes
│   ├── models/
│   │   ├── __init__.py
│   │   └── passport.py         # Data models for responses
│   ├── services/
│   │   ├── __init__.py
│   │   ├── ocr_extractor.py   # OCR text extraction service
│   │   ├── face_detector.py   # Face detection service
│   │   └── processor.py        # Main processing coordinator
│   └── utils/
│       ├── __init__.py
│       └── image_processing.py # Image processing utilities
├── tests/
│   ├── __init__.py
│   ├── test_recognition.py     # OCR and face detection tests
│   └── test_api.py             # Full API endpoint tests
├── data/                       # Sample passport images (optional)
├── Dockerfile                  # Docker configuration
├── requirements.txt            # Python dependencies
├── run_api.py                  # API startup script
└── README.md                   # This file
```

---

## Quick Start

### Prerequisites

- Python 3.9+
- pip or Docker

### Option 1: Run with Docker (Recommended)

1. **Build the Docker image:**
   ```bash
   docker build -t passport_app .
   ```

2. **Run the container:**
   ```bash
   docker run -p 8000:8000 passport_app
   ```

3. **Access the API:**
   - Main API: http://localhost:8000
   - Interactive Docs: http://localhost:8000/docs
   - Alternative Docs: http://localhost:8000/redoc

### Option 2: Run Locally without Docker

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the server:**
   ```bash
   python run_api.py
   ```

3. **Custom host/port (optional):**
   ```bash
   python run_api.py --host 0.0.0.0 --port 8080
   ```

4. **Development mode with auto-reload:**
   ```bash
   python run_api.py --reload
   ```

---

## API Usage

### Endpoint: POST `/api/v1/upload`

Upload a passport image and extract information.

**Request:**
- **Method**: POST
- **Path**: `/api/v1/upload`
- **Content-Type**: `multipart/form-data`
- **Form Data**: `image` (required) - Image file (JPEG, PNG, BMP, or GIF)

**Success Response (200 OK):**
```json
{
  "passport_id": "A12345678",
  "face_image": "/9j/4AAQSkZJRgABAQAAAQABAAD..."
}
```

- `passport_id`: String - Extracted passport identifier (9 digits or 1 letter + 8 digits)
- `face_image`: String - Base64-encoded cropped face image (PNG format)

**Error Responses:**

| Status Code | Description |
|-------------|-------------|
| 400 Bad Request | Invalid file format, empty file, or corrupted image |
| 422 Unprocessable Entity | OCR extraction failed, face detection failed, or data parsing errors |
| 500 Internal Server Error | Unexpected server error |

---

## Usage Examples

### Using curl

```bash
curl -X POST "http://localhost:8000/api/v1/upload" \
  -H "accept: application/json" \
  -F "image=@/path/to/passport.jpg"
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
    passport_id = data["passport_id"]
    face_base64 = data["face_image"]
    
    # Decode base64 to image
    face_image = Image.open(BytesIO(base64.b64decode(face_base64)))
    face_image.save("extracted_face.png")
    
    print(f"Passport ID: {passport_id}")
    print(f"Face image saved: extracted_face.png")
else:
    print(f"Error: {response.status_code}")
    print(response.json())
```

---

## Testing

### Test Recognition Technologies

Test OCR and face detection independently:

```bash
python tests/test_recognition.py
```

This test:
- Tests OCR text extraction
- Tests face detection and cropping
- Tests the full processing pipeline
- Saves output photos to `tests/output/` directory

### Test Complete API

Test the full API endpoint with error handling:

```bash
python tests/test_api.py
```

This test:
- Tests API health and root endpoints
- Tests file upload with valid passport images
- Tests error handling (missing file, unsupported format, invalid image)
- Validates response structure and data
- Saves API response photos to `tests/output/` directory

---

## Deployment with Docker

### Build the Image

```bash
docker build -t passport_app .
```

### Run the Container

```bash
# Basic run
docker run -p 8000:8000 passport_app

# Run in detached mode
docker run -d -p 8000:8000 --name passport_api passport_app

# Run with custom port
docker run -p 8080:8000 passport_app
```

### Verify the Container

```bash
# Check running containers
docker ps

# View logs
docker logs passport_api

# Stop the container
docker stop passport_api

# Remove the container
docker rm passport_api
```

### Test the Deployed API

```bash
# Health check
curl http://localhost:8000/health

# Upload a passport image
curl -X POST "http://localhost:8000/api/v1/upload" \
  -F "image=@/path/to/passport.jpg"
```

---

## Exception Handling

The application implements comprehensive exception handling for various error scenarios:

### Exception Hierarchy

```
PassportProcessingException (base)
├── FileUploadException
│   └── UnsupportedFileTypeException
├── ImageValidationException
├── UnreadableImageException
├── OCRExtractionException
│   └── PassportIDParsingException
├── FaceDetectionException
│   ├── NoFaceDetectedException
│   └── MultipleFacesDetectedException
└── ImageProcessingException
```

### Error Scenarios Handled

| Scenario | Status Code | Message |
|----------|------------|---------|
| Missing file | 400 | No file provided in upload request |
| Unsupported format | 400 | Unsupported file format: .xyz |
| Empty file | 400 | Uploaded file is empty |
| Corrupted image | 400 | Failed to decode image |
| No text detected | 422 | No text detected in image |
| No passport ID found | 422 | No passport ID found matching required format |
| No face detected | 422 | No face detected in the passport image |
| Multiple faces | 422 | Multiple faces detected (expected exactly one) |
| Face cropping failed | 422 | Error cropping face |

---

## Implementation Details

### OCR Extraction

**File**: `app/services/ocr_extractor.py`

- Uses **RapidOCR** for fast, accurate text recognition
- Implements CLAHE image enhancement for better OCR results
- Accepts two passport ID formats:
  - 9 consecutive digits (e.g., "123456789")
  - 1 letter followed by 8 digits (e.g., "A12345678")
- Keyword-based search near:
  - "Document Number"
  - "Passport No"
  - "Document No"
  - "Passport Number"
- Falls back to full text search if keywords not found

### Face Detection

**File**: `app/services/face_detector.py`

- Uses **Haar Cascade Classifier** for face detection
- Preprocesses images to grayscale for optimal detection
- Validates that exactly one face is detected
- Crops face region with 10% padding
- Returns cropped face as numpy array

### Image Processing

**File**: `app/utils/image_processing.py`

- Validates file formats (JPG, PNG, BMP, GIF)
- Loads and decodes images from bytes
- Resizes large images (>1920x1080) for better processing
- Converts images to base64 for API responses

---

## Configuration

### Face Detection Parameters

Configured in `app/services/face_detector.py`:
- `SCALE_FACTOR`: 1.1 (face detection scale)
- `MIN_NEIGHBORS`: 5 (face detection neighbors)
- `MIN_FACE_SIZE`: (50, 50) (minimum face region size)
- `padding_percent`: 0.1 (10% padding around face)

### Supported Image Formats

- JPEG (`.jpg`, `.jpeg`)
- PNG (`.png`)
- BMP (`.bmp`)
- GIF (`.gif`)

---

## Dependencies

Core dependencies listed in `requirements.txt`:

- **fastapi** - Modern web framework for building APIs
- **uvicorn** - ASGI web server
- **python-multipart** - File upload handling
- **opencv-python-headless** - Computer vision (no GUI)
- **rapidocr-onnxruntime** - OCR text detection
- **pillow** - Image processing library
- **numpy** - Numerical computations
- **requests** - HTTP library
- **httpx** - Modern HTTP client

---

## Troubleshooting

### Common Issues

**Issue**: "No module named 'rapidocr_onnxruntime'"
- **Solution**: Ensure dependencies are installed: `pip install -r requirements.txt`

**Issue**: "No face detected" for valid passport image
- **Solution**: Ensure image has good lighting and the face is clearly visible
- Try adjusting `SCALE_FACTOR` or `MIN_NEIGHBORS` in `face_detector.py`

**Issue**: Wrong passport ID extracted
- **Solution**: This may occur if OCR has low confidence or multiple numbers are visible
- Check image quality and lighting
- Ensure passport is positioned correctly

**Issue**: API returns 422 error
- **Solution**: Check the error message in response for specific details
- Common causes: OCR failed to detect text, face detection issues, or invalid image format

**Issue**: Docker container won't start
- **Solution**: Check logs with `docker logs passport_api`
- Ensure port 8000 is not already in use

**Issue**: Connection refused when testing
- **Solution**: Ensure API server is running: `python run_api.py` or Docker container is up

---

## Performance Considerations

- Images larger than 1920x1080 are automatically resized to preserve processing speed
- RapidOCR is optimized for CPU-bound text detection
- Face detection uses efficient Haar Cascade classifier
- Base64 encoding adds ~33% to response size
- Typical processing time: 2-5 seconds per image

---

## License

This project is provided as-is for passport processing applications.

---

## Support

For issues, questions, or contributions, please refer to the project repository or contact the development team.
