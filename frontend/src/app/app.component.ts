import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient, HttpClientModule } from '@angular/common/http';

interface DocumentAnalysis {
  text: string;
  confidence: number;
  processing_time: number;
}

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, FormsModule, HttpClientModule],
  template: `
    <div class="container">
      <header>
        <h1>Document Reader with PyTorch</h1>
        <p>Upload documents to extract and analyze text using AI</p>
      </header>

      <main>
        <div class="upload-section">
          <h2>Upload Document</h2>
          <div class="file-input-container">
            <input
              type="file"
              (change)="onFileSelected($event)"
              accept=".pdf,.txt,.doc,.docx,.png,.jpg,.jpeg"
              #fileInput
            />
            <button
              (click)="uploadDocument()"
              [disabled]="!selectedFile || isProcessing"
              class="upload-btn"
            >
              {{ isProcessing ? 'Processing...' : 'Analyze Document' }}
            </button>
          </div>

          <div class="file-info" *ngIf="selectedFile">
            <p><strong>Selected file:</strong> {{ selectedFile.name }}</p>
            <p>
              <strong>Size:</strong> {{ formatFileSize(selectedFile.size) }}
            </p>
            <p><strong>Type:</strong> {{ selectedFile.type || 'Unknown' }}</p>
          </div>
        </div>

        <div class="results-section" *ngIf="analysisResult">
          <h2>Analysis Results</h2>
          <div class="result-card">
            <div class="result-header">
              <span
                class="confidence-badge"
                [class.high-confidence]="analysisResult.confidence > 0.8"
              >
                Confidence: {{ (analysisResult.confidence * 100).toFixed(1) }}%
              </span>
              <span class="processing-time">
                Processed in {{ analysisResult.processing_time.toFixed(2) }}s
              </span>
            </div>
            <div class="extracted-text">
              <h3>Extracted Text:</h3>
              <pre>{{ analysisResult.text }}</pre>
            </div>
          </div>
        </div>

        <div class="error-section" *ngIf="errorMessage">
          <div class="error-card">
            <h3>Error</h3>
            <p>{{ errorMessage }}</p>
          </div>
        </div>

        <div class="loading-section" *ngIf="isProcessing">
          <div class="loading-spinner"></div>
          <p>Processing document with PyTorch...</p>
        </div>
      </main>
    </div>
  `,
  styles: [
    `
      .container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 20px;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      }

      header {
        text-align: center;
        margin-bottom: 40px;
        padding: 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
      }

      header h1 {
        margin: 0 0 10px 0;
        font-size: 2.5em;
      }

      header p {
        margin: 0;
        opacity: 0.9;
        font-size: 1.1em;
      }

      .upload-section {
        background: white;
        padding: 30px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 30px;
      }

      .upload-section h2 {
        margin-top: 0;
        color: #333;
      }

      .file-input-container {
        display: flex;
        gap: 15px;
        align-items: center;
        margin-bottom: 20px;
      }

      input[type='file'] {
        flex: 1;
        padding: 10px;
        border: 2px dashed #ddd;
        border-radius: 5px;
        background: #f9f9f9;
      }

      .upload-btn {
        padding: 12px 24px;
        background: #667eea;
        color: white;
        border: none;
        border-radius: 5px;
        cursor: pointer;
        font-size: 16px;
        transition: background 0.3s;
      }

      .upload-btn:hover:not(:disabled) {
        background: #5a67d8;
      }

      .upload-btn:disabled {
        background: #ccc;
        cursor: not-allowed;
      }

      .file-info {
        background: #f0f4f8;
        padding: 15px;
        border-radius: 5px;
        border-left: 4px solid #667eea;
      }

      .file-info p {
        margin: 5px 0;
      }

      .results-section {
        background: white;
        padding: 30px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 30px;
      }

      .results-section h2 {
        margin-top: 0;
        color: #333;
      }

      .result-card {
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        overflow: hidden;
      }

      .result-header {
        background: #f7fafc;
        padding: 15px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid #e2e8f0;
      }

      .confidence-badge {
        background: #fed7d7;
        color: #c53030;
        padding: 5px 10px;
        border-radius: 15px;
        font-size: 14px;
        font-weight: bold;
      }

      .confidence-badge.high-confidence {
        background: #c6f6d5;
        color: #2f855a;
      }

      .processing-time {
        color: #666;
        font-size: 14px;
      }

      .extracted-text {
        padding: 20px;
      }

      .extracted-text h3 {
        margin-top: 0;
        color: #333;
      }

      .extracted-text pre {
        background: #f7fafc;
        padding: 15px;
        border-radius: 5px;
        white-space: pre-wrap;
        word-wrap: break-word;
        max-height: 400px;
        overflow-y: auto;
        border: 1px solid #e2e8f0;
      }

      .error-section {
        background: white;
        padding: 30px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 30px;
      }

      .error-card {
        background: #fed7d7;
        border: 1px solid #feb2b2;
        border-radius: 8px;
        padding: 20px;
      }

      .error-card h3 {
        color: #c53030;
        margin-top: 0;
      }

      .error-card p {
        color: #742a2a;
        margin-bottom: 0;
      }

      .loading-section {
        text-align: center;
        padding: 40px;
        background: white;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
      }

      .loading-spinner {
        width: 50px;
        height: 50px;
        border: 5px solid #f3f3f3;
        border-top: 5px solid #667eea;
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin: 0 auto 20px;
      }

      @keyframes spin {
        0% {
          transform: rotate(0deg);
        }
        100% {
          transform: rotate(360deg);
        }
      }

      .loading-section p {
        color: #666;
        font-size: 18px;
        margin: 0;
      }
    `,
  ],
})
export class AppComponent {
  selectedFile: File | null = null;
  analysisResult: DocumentAnalysis | null = null;
  errorMessage: string = '';
  isProcessing: boolean = false;

  private apiUrl = 'http://localhost:8000';

  constructor(private http: HttpClient) {}

  onFileSelected(event: any): void {
    const file = event.target.files[0];
    if (file) {
      this.selectedFile = file;
      this.analysisResult = null;
      this.errorMessage = '';
    }
  }

  uploadDocument(): void {
    if (!this.selectedFile) {
      return;
    }

    this.isProcessing = true;
    this.errorMessage = '';
    this.analysisResult = null;

    const formData = new FormData();
    formData.append('file', this.selectedFile);

    this.http
      .post<DocumentAnalysis>(`${this.apiUrl}/analyze-document`, formData)
      .subscribe({
        next: (result) => {
          this.analysisResult = result;
          this.isProcessing = false;
        },
        error: (error) => {
          console.error('Error analyzing document:', error);
          this.errorMessage =
            error.error?.detail ||
            'Failed to analyze document. Please try again.';
          this.isProcessing = false;
        },
      });
  }

  formatFileSize(bytes: number): string {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }
}
