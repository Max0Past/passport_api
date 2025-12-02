# Passport Processing API

A FastAPI application that processes passport images to extract passport identifiers and detect/crop face regions. The application combines OCR (Optical Character Recognition) technology with face detection to automatically extract key information from passport photos.

## Features

- **Passport ID Extraction**: Automatically extracts 9-character passport identifiers using RapidOCR
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
├── data/                       # Sample passport images
├── requirements.txt            # Python dependencies
├── run_api.py                  # API startup script
└── README.md                   # This file
```

## Installation

### Prerequisites

- Python 3.9+
- pip or conda

### Setup

1. **Clone/navigate to the project directory**
   ```bash
   cd /home/max/Projects/passport_api
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Starting the API Server

```bash
# Start the server on localhost:8000
python run_api.py

# Custom host and port
python run_api.py --host 0.0.0.0 --port 8080

# Enable auto-reload for development
python run_api.py --reload
```

The API will be available at:
- **Main API**: `http://localhost:8000`
- **Interactive Docs**: `http://localhost:8000/docs` (Swagger UI)
- **Alternative Docs**: `http://localhost:8000/redoc` (ReDoc)

### API Endpoint

#### POST `/api/v1/upload`

Upload a passport image and extract information.

**Request:**
- **Content-Type**: `multipart/form-data`
- **Parameter**: `file` (required) - Image file (JPEG, PNG, BMP, or GIF)

**Response (200 OK):**
```json
{
  "passport_id": "728491530",
  "face_image_base64": "iVBORw0KGgoAAAANSUhEUgAAAAUA..."
}
```

**Error Responses:**

- `400 Bad Request`: Invalid file format, empty file, or corrupted image
- `422 Unprocessable Entity`: OCR extraction failed, face detection failed, or data parsing errors
- `500 Internal Server Error`: Unexpected server error

### Example Usage with cURL

```bash
# Upload a passport image
curl -X POST "http://localhost:8000/api/v1/upload" \
  -H "accept: application/json" \
  -F "file=@/path/to/passport.jpg"

# Response will include passport_id and base64-encoded face image
```

### Example Usage with Python

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
    face_base64 = data["face_image_base64"]
    
    # Decode base64 to image
    face_image = Image.open(BytesIO(base64.b64decode(face_base64)))
    face_image.save("extracted_face.png")
    
    print(f"Passport ID: {passport_id}")
    print(f"Face image saved: extracted_face.png")
else:
    print(f"Error: {response.status_code}")
    print(response.json())
```

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
- Uses sample passport images from the `data/` folder

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
| No passport ID found | 422 | No passport ID found in extracted text |
| No face detected | 422 | No face detected in the passport image |
| Multiple faces | 422 | Multiple faces detected (expected exactly one) |
| Face cropping failed | 422 | Error cropping face |

## Implementation Details

### OCR Extraction (`app/services/ocr_extractor.py`)

- Uses **RapidOCR** for fast, accurate text recognition
- Implements image enhancement for better OCR results
- Extracts 9-character passport ID sequences
- Intelligent filtering to distinguish passport numbers from country names

### Face Detection (`app/services/face_detector.py`)

- Uses **Haar Cascade Classifier** for face detection
- Validates that exactly one face is detected
- Crops face region with configurable padding
- Returns cropped face as numpy array

### Image Processing (`app/utils/image_processing.py`)

- Validates file formats (JPG, PNG, BMP, GIF)
- Loads and decodes images from bytes
- Resizes large images for better processing
- Enhances images for OCR using CLAHE (Contrast Limited Adaptive Histogram Equalization)
- Converts images to base64 for API responses

### API Routes (`app/api/routes.py`)

- Single endpoint: `POST /api/v1/upload`
- File validation and error handling
- Integrates OCR and face detection services
- Returns structured JSON response

## Configuration

### Image Processing Parameters

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

## Performance Considerations

- Images larger than 1920x1080 are automatically resized to preserve processing speed
- RapidOCR is optimized for CPU-bound text detection
- Face detection uses efficient Haar Cascade classifier
- Base64 encoding adds ~33% to response size

## Dependencies

- **fastapi**: Modern web framework for building APIs
- **uvicorn**: ASGI web server
- **python-multipart**: File upload handling
- **opencv-python-headless**: Computer vision (no GUI)
- **rapidocr-onnxruntime**: OCR text detection
- **pillow**: Image processing library
- **numpy**: Numerical computations
- **pytesseract**: Tesseract OCR wrapper (optional, included for compatibility)
- **requests**: HTTP library
- **httpx**: Modern HTTP client

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

## Future Enhancements

- Support for additional document types (visas, IDs)
- Batch processing of multiple images
- Face recognition/matching capabilities
- Document verification/validation
- Support for non-Latin scripts
- Caching layer for repeated images
- Rate limiting and authentication

## License

This project is provided as-is for passport processing applications.

## Support

For issues, questions, or contributions, please refer to the project repository or contact the development team.
