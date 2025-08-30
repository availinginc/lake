#!/bin/bash

# Document Reader Application Startup Script
# This script starts both the backend and frontend servers

echo "🚀 Starting Document Reader Application"
echo "========================================"

# Check if we're in the right directory
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "❌ Error: Please run this script from the document-reader-app directory"
    echo "   Current directory: $(pwd)"
    echo "   Expected structure:"
    echo "   document-reader-app/"
    echo "   ├── backend/"
    echo "   ├── frontend/"
    echo "   └── start-app.sh"
    exit 1
fi

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo "🔍 Checking prerequisites..."

if ! command_exists python3; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

if ! command_exists node; then
    echo "❌ Node.js is not installed. Please install Node.js 16 or higher."
    exit 1
fi

if ! command_exists npm; then
    echo "❌ npm is not installed. Please install npm."
    exit 1
fi

echo "✅ Prerequisites check passed"

# Function to start backend
start_backend() {
    echo "🐍 Starting Python backend..."
    cd backend

    # Check if virtual environment exists, create if not
    if [ ! -d "venv" ]; then
        echo "📦 Creating virtual environment..."
        python3 -m venv venv
    fi

    # Activate virtual environment
    source venv/bin/activate

    # Install dependencies
    echo "📦 Installing Python dependencies..."
    pip install -r requirements.txt

    # Start the server
    echo "🚀 Starting FastAPI server on http://localhost:8000"
    python start.py &
    BACKEND_PID=$!

    cd ..
    echo "✅ Backend started (PID: $BACKEND_PID)"
}

# Function to start frontend
start_frontend() {
    echo "🅰️  Starting Angular frontend..."
    cd frontend

    # Install dependencies if node_modules doesn't exist
    if [ ! -d "node_modules" ]; then
        echo "📦 Installing Node.js dependencies..."
        npm install
    fi

    # Start the development server
    echo "🚀 Starting Angular dev server on http://localhost:4200"
    npm start &
    FRONTEND_PID=$!

    cd ..
    echo "✅ Frontend started (PID: $FRONTEND_PID)"
}

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down servers..."

    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
        echo "✅ Backend server stopped"
    fi

    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
        echo "✅ Frontend server stopped"
    fi

    echo "👋 Goodbye!"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Start both servers
start_backend
sleep 3  # Give backend time to start
start_frontend

echo ""
echo "🎉 Application is starting up!"
echo "================================"
echo "📱 Frontend: http://localhost:4200"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "💡 Tips:"
echo "   - Upload a document to test the application"
echo "   - Check the sample-documents/ folder for test files"
echo "   - Press Ctrl+C to stop both servers"
echo ""
echo "⏳ Waiting for servers to fully start..."

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
