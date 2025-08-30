# Document Reader Application by Cline

A full-stack application that uses Angular for the frontend and Python with PyTorch for the backend to read and analyze documents using AI.

## Features

- **Multi-format Support**: Process PDF, DOCX, TXT, and image files (JPG, PNG, etc.)
- **AI-Powered Analysis**: Uses PyTorch and Transformers for intelligent text extraction and quality assessment
- **OCR Capabilities**: Extract text from images using Tesseract OCR with advanced preprocessing
- **Real-time Processing**: Live feedback with confidence scores and processing times
- **Modern UI**: Responsive Angular interface with drag-and-drop file upload
- **RESTful API**: FastAPI backend with automatic documentation

## Architecture

```
document-reader-app/
├── frontend/          # Angular application
│   ├── src/
│   │   ├── app/       # Angular components
│   │   ├── assets/    # Static assets
│   │   └── styles.css # Global styles
│   ├── package.json
│   └── angular.json
├── backend/           # Python FastAPI server
│   ├── main.py        # Main application
│   ├── start.py       # Startup script
│   └── requirements.txt
└── README.md
```

## Prerequisites

### System Requirements

- **Python 3.8+** (for backend)
- **Node.js 16+** (for frontend)
- **npm or yarn** (package manager)

### Optional Dependencies

- **Tesseract OCR** (for image text extraction)
  - macOS: `brew install tesseract`
  - Ubuntu: `sudo apt-get install tesseract-ocr`
  - Windows: [Download installer](https://github.com/UB-Mannheim/tesseract/wiki)

## Quick Start

### 1. Backend Setup

Navigate to the backend directory and run the startup script:

```bash
cd document-reader-app/backend
python start.py
```

The startup script will:

- Check Python version compatibility
- Install required dependencies
- Check for Tesseract OCR installation
- Start the FastAPI server on `http://localhost:8000`

**Manual Setup (Alternative):**

```bash
cd document-reader-app/backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Frontend Setup

Open a new terminal and navigate to the frontend directory:

```bash
cd document-reader-app/frontend
npm install
npm start
```

The Angular development server will start on `http://localhost:4200`

### 3. Access the Application

- **Frontend**: http://localhost:4200
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## Usage

1. **Upload Document**: Click the file input or drag and drop a supported file
2. **Analyze**: Click "Analyze Document" to process the file
3. **View Results**: See extracted text with confidence scores and processing time

### Supported File Types

- **Images**: JPG, JPEG, PNG, BMP, TIFF
- **Documents**: PDF, DOCX, TXT
- **Size Limit**: 10MB per file

## API Endpoints

### `POST /analyze-document`

Upload and analyze a document file.

**Request**: Multipart form data with file
**Response**:

```json
{
  "text": "Extracted text content...",
  "confidence": 0.95,
  "processing_time": 1.23
}
```

### `GET /health`

Check API health and system status.

**Response**:

```json
{
  "status": "healthy",
  "pytorch_available": true,
  "device": "cpu",
  "text_classifier_loaded": true
}
```

## Technology Stack

### Frontend

- **Angular 17**: Modern web framework
- **TypeScript**: Type-safe JavaScript
- **RxJS**: Reactive programming
- **CSS3**: Modern styling with gradients and animations

### Backend

- **FastAPI**: High-performance Python web framework
- **PyTorch**: Deep learning framework
- **Transformers**: Hugging Face NLP models
- **Tesseract**: OCR engine
- **OpenCV**: Computer vision library
- **Pillow**: Image processing

### AI/ML Components

- **DistilBERT**: Text quality classification
- **Tesseract OCR**: Optical character recognition
- **OpenCV**: Image preprocessing
- **PyTorch**: Neural network inference

## Development

### Frontend Development

```bash
cd frontend
npm run start    # Development server
npm run build    # Production build
npm run test     # Run tests
```

### Backend Development

```bash
cd backend
python main.py              # Start server
python -m pytest           # Run tests (if tests exist)
uvicorn main:app --reload  # Development with auto-reload
```

### Adding New Document Types

To support additional file formats:

1. Add the file extension to the frontend's `accept` attribute
2. Implement a new extraction method in `DocumentProcessor`
3. Add the file type to the processing logic in `process_document()`

## Troubleshooting

### Common Issues

**1. Tesseract not found**

- Install Tesseract OCR for your operating system
- Ensure it's in your system PATH

**2. PyTorch installation issues**

- Use the official PyTorch installation guide: https://pytorch.org/get-started/locally/
- For CPU-only: `pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu`

**3. CORS errors**

- Ensure the backend is running on port 8000
- Check that CORS origins in `main.py` include your frontend URL

**4. Large file uploads**

- Files are limited to 10MB by default
- Modify the size check in `analyze_document()` if needed

**5. Angular build errors**

- Delete `node_modules` and run `npm install` again
- Ensure Node.js version is 16 or higher

### Performance Optimization

- **GPU Acceleration**: Install CUDA-compatible PyTorch for faster processing
- **Model Caching**: Models are cached after first load
- **Image Preprocessing**: Optimized OpenCV pipeline for better OCR results

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Support

For issues and questions:

1. Check the troubleshooting section
2. Review API documentation at `/docs`
3. Check server logs for error details
4. Ensure all dependencies are properly installed
