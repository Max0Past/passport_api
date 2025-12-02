#!/usr/bin/env python3
"""
Startup script for the Passport Processing API.

Usage:
    python run_api.py [--host HOST] [--port PORT] [--reload]
"""
import argparse
import sys
from pathlib import Path

import uvicorn

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))


def main():
    """Run the API server."""
    parser = argparse.ArgumentParser(
        description="Run Passport Processing API server"
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Server host (default: 127.0.0.1)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Server port (default: 8000)"
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload on file changes"
    )
    
    args = parser.parse_args()
    
    print("\n" + "="*60)
    print("Starting Passport Processing API")
    print("="*60)
    print(f"Host: {args.host}")
    print(f"Port: {args.port}")
    print(f"Reload: {args.reload}")
    print(f"\nAccess the API at: http://{args.host}:{args.port}")
    print(f"API documentation: http://{args.host}:{args.port}/docs")
    print(f"Alternative docs: http://{args.host}:{args.port}/redoc")
    print("="*60 + "\n")
    
    uvicorn.run(
        "app.main:app",
        host=args.host,
        port=args.port,
        reload=args.reload
    )


if __name__ == "__main__":
    main()
