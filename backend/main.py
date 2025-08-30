from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import torch
import torchvision.transforms as transforms
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
from PIL import Image
import pytesseract
import PyPDF2
from docx import Document
import cv2
import numpy as np
import io
import time
import logging
from typing import Dict, Any
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Document Reader API",
    description="AI-powered document analysis using PyTorch",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200", "http://127.0.0.1:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class DocumentProcessor:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Using device: {self.device}")

        # Initialize image preprocessing transforms
        self.image_transforms = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

        # Initialize text classification pipeline (for confidence scoring)
        try:
            self.text_classifier = pipeline(
                "text-classification",
                model="distilbert-base-uncased-finetuned-sst-2-english",
                device=0 if torch.cuda.is_available() else -1
            )
        except Exception as e:
            logger.warning(f"Could not load text classifier: {e}")
            self.text_classifier = None

    def extract_text_from_image(self, image: Image.Image) -> tuple[str, float]:
        """Extract text from image using OCR with confidence scoring"""
        try:
            # Convert PIL image to OpenCV format for preprocessing
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

            # Preprocess image for better OCR results
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)

            # Apply denoising
            denoised = cv2.fastNlMeansDenoising(gray)

            # Apply adaptive thresholding
            thresh = cv2.adaptiveThreshold(
                denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )

            # Extract text using Tesseract
            custom_config = r'--oem 3 --psm 6'
            text = pytesseract.image_to_string(thresh, config=custom_config)

            # Get confidence data
            data = pytesseract.image_to_data(thresh, output_type=pytesseract.Output.DICT)
            confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0

            return text.strip(), avg_confidence / 100.0

        except Exception as e:
            logger.error(f"Error in OCR processing: {e}")
            return "", 0.0

    def extract_text_from_pdf(self, file_content: bytes) -> tuple[str, float]:
        """Extract text from PDF file"""
        try:
            pdf_file = io.BytesIO(file_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)

            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"

            # Simple confidence based on text length and readability
            confidence = min(len(text.strip()) / 1000.0, 1.0) if text.strip() else 0.0

            return text.strip(), confidence

        except Exception as e:
            logger.error(f"Error in PDF processing: {e}")
            return "", 0.0

    def extract_text_from_docx(self, file_content: bytes) -> tuple[str, float]:
        """Extract text from DOCX file"""
        try:
            docx_file = io.BytesIO(file_content)
            doc = Document(docx_file)

            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"

            # Simple confidence based on text length
            confidence = min(len(text.strip()) / 1000.0, 1.0) if text.strip() else 0.0

            return text.strip(), confidence

        except Exception as e:
            logger.error(f"Error in DOCX processing: {e}")
            return "", 0.0

    def extract_text_from_txt(self, file_content: bytes) -> tuple[str, float]:
        """Extract text from TXT file"""
        try:
            text = file_content.decode('utf-8')
            confidence = 1.0  # High confidence for plain text
            return text.strip(), confidence

        except UnicodeDecodeError:
            try:
                text = file_content.decode('latin-1')
                confidence = 0.8  # Lower confidence due to encoding issues
                return text.strip(), confidence
            except Exception as e:
                logger.error(f"Error in TXT processing: {e}")
                return "", 0.0

    def analyze_text_quality(self, text: str) -> float:
        """Analyze text quality using PyTorch-based classifier"""
        if not text.strip() or not self.text_classifier:
            return 0.5

        try:
            # Use text classifier to assess quality
            result = self.text_classifier(text[:512])  # Limit text length

            # Convert sentiment score to quality score
            if result[0]['label'] == 'POSITIVE':
                return min(result[0]['score'], 1.0)
            else:
                return max(1.0 - result[0]['score'], 0.0)

        except Exception as e:
            logger.error(f"Error in text quality analysis: {e}")
            return 0.5

    def process_document(self, file: UploadFile) -> Dict[str, Any]:
        """Main document processing function"""
        start_time = time.time()

        try:
            file_content = file.file.read()
            file_extension = file.filename.lower().split('.')[-1] if file.filename else ""

            text = ""
            confidence = 0.0

            if file_extension in ['jpg', 'jpeg', 'png', 'bmp', 'tiff']:
                # Process image file
                image = Image.open(io.BytesIO(file_content))
                text, confidence = self.extract_text_from_image(image)

            elif file_extension == 'pdf':
                # Process PDF file
                text, confidence = self.extract_text_from_pdf(file_content)

            elif file_extension == 'docx':
                # Process DOCX file
                text, confidence = self.extract_text_from_docx(file_content)

            elif file_extension == 'txt':
                # Process TXT file
                text, confidence = self.extract_text_from_txt(file_content)

            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported file type: {file_extension}"
                )

            # Enhance confidence with text quality analysis
            if text:
                quality_score = self.analyze_text_quality(text)
                confidence = (confidence + quality_score) / 2.0

            processing_time = time.time() - start_time

            return {
                "text": text,
                "confidence": confidence,
                "processing_time": processing_time,
                "file_type": file_extension,
                "file_size": len(file_content)
            }

        except Exception as e:
            logger.error(f"Error processing document: {e}")
            raise HTTPException(status_code=500, detail=str(e))

# Initialize document processor
processor = DocumentProcessor()

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Document Reader API is running",
        "version": "1.0.0",
        "pytorch_version": torch.__version__,
        "device": str(processor.device)
    }

@app.post("/analyze-document")
async def analyze_document(file: UploadFile = File(...)):
    """Analyze uploaded document and extract text"""

    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    # Check file size (limit to 10MB)
    file_content = await file.read()
    if len(file_content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large (max 10MB)")

    # Reset file pointer
    await file.seek(0)

    try:
        result = processor.process_document(file)

        logger.info(f"Processed {file.filename}: {len(result['text'])} characters extracted")

        return JSONResponse(content={
            "text": result["text"],
            "confidence": result["confidence"],
            "processing_time": result["processing_time"]
        })

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "pytorch_available": torch.cuda.is_available(),
        "device": str(processor.device),
        "text_classifier_loaded": processor.text_classifier is not None
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
