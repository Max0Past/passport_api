"""
Main FastAPI application for passport processing.
"""
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.api.routes import router
from app.core.exceptions import PassportProcessingException


# Create FastAPI app
app = FastAPI(
    title="Passport Processing API",
    description="API for extracting passport ID and detecting face from passport images",
    version="1.0.0"
)

# Include routes
app.include_router(router)





@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy"
    }


@app.exception_handler(PassportProcessingException)
async def passport_processing_exception_handler(request, exc):
    """Handle passport processing exceptions."""
    return JSONResponse(
        status_code=422,
        content={
            "detail": str(exc)
        }
    )
