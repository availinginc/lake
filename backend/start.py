#!/usr/bin/env python3
"""
Startup script for the Document Reader API
"""

import subprocess
import sys
import os
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required")
        sys.exit(1)
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor} detected")

def install_dependencies():
    """Install required dependencies"""
    print("Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")
        sys.exit(1)

def check_tesseract():
    """Check if Tesseract OCR is installed"""
    try:
        subprocess.check_output(["tesseract", "--version"], stderr=subprocess.STDOUT)
        print("✓ Tesseract OCR is installed")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️  Tesseract OCR not found. Please install it:")
        print("   macOS: brew install tesseract")
        print("   Ubuntu: sudo apt-get install tesseract-ocr")
        print("   Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki")
        print("   The application will still work but OCR functionality will be limited.")

def start_server():
    """Start the FastAPI server"""
    print("Starting Document Reader API server...")
    print("Server will be available at: http://localhost:8000")
    print("API documentation at: http://localhost:8000/docs")
    print("Press Ctrl+C to stop the server")

    try:
        subprocess.run([sys.executable, "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"])
    except KeyboardInterrupt:
        print("\n✓ Server stopped")

def main():
    """Main startup function"""
    print("🚀 Document Reader API Startup")
    print("=" * 40)

    # Change to backend directory
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)

    # Run checks and setup
    check_python_version()
    check_tesseract()
    install_dependencies()

    print("\n" + "=" * 40)
    start_server()

if __name__ == "__main__":
    main()
