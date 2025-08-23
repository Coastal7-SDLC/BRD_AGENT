# 🚀 BRD Agent

**AI-Powered Business Requirements Document Generator with Google Gemini Integration**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18+-blue.svg)](https://reactjs.org)
[![Gemini](https://img.shields.io/badge/Google%20Gemini-2.0%20Flash-orange.svg)](https://ai.google.dev/gemini)

Transform your project ideas into comprehensive Business Requirements Documents (BRDs) using the power of Google's Gemini AI. This intelligent agent analyzes your project descriptions and generates professional, structured BRDs automatically.

## ✨ Features

### 🤖 AI-Powered Generation
- **Dynamic Content Creation**: No rigid templates - pure AI-generated content tailored to your project
- **Intelligent Analysis**: Automatically extracts business requirements, stakeholders, and objectives
- **Smart Context Understanding**: Processes both text input and supporting documents for comprehensive analysis

### 📄 Multi-Format Support
- **Text Input**: Describe your project in natural language
- **File Upload**: Support for PDF, Markdown, and DOCX files
- **Existing BRD Enhancement**: Upload current BRDs for AI-powered improvements
- **Hybrid Processing**: Combine text descriptions with supporting documents

### 📊 Comprehensive BRD Structure
- Executive Summary
- Project Overview & Objectives
- Stakeholder Identification
- Scope Definition (In/Out of Scope)
- Business, Functional, and Non-functional Requirements
- User Roles & Permissions
- Success Criteria & Metrics
- Assumptions & Constraints
- Implementation Roadmap

### 🎯 Quality Assurance
- **Completeness Scoring**: AI evaluates BRD quality and suggests improvements
- **Validation**: Ensures proper structure and data integrity
- **Fallback Mechanisms**: Graceful degradation when AI services are unavailable

## 🏗️ Architecture

```
BRD_A1/
├── backend/                 # FastAPI Backend
│   ├── main.py             # FastAPI application entry point
│   ├── config.py           # Configuration management
│   ├── routes/             # API endpoints
│   │   └── llm_routes.py  # LLM-powered routes
│   ├── services/           # Business logic
│   │   ├── llm_service.py # Google Gemini integration
│   │   └── brd.py         # BRD generation logic
│   └── utils/              # Utility functions
│       └── rate_limiter.py # Rate limiting implementation
└── frontend/               # React Frontend
    ├── src/
    │   ├── components/     # React components
    │   │   ├── Dashboard.jsx
    │   │   └── ErrorBoundary.jsx
    │   └── App.jsx         # Main application
    └── package.json        # Dependencies
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+**
- **Node.js 16+**
- **Google Gemini API Key** ([Get it here](https://makersuite.google.com/app/apikey))

### 1. Clone the Repository

```bash
git clone <repository-url>
cd BRD_AGENT
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### 4. Start Backend

```bash
cd backend

# Start FastAPI server
python main.py
```

The application will be available at:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```env
# Required
GOOGLE_API_KEY=your_gemini_api_key_here

# Optional
SECRET_KEY=your_secret_key_here
HOST=0.0.0.0
PORT=8000
DEBUG=False
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### Google Gemini Configuration

- **Model**: `gemini-2.0-flash` (default)
- **Temperature**: 0.3 (balanced creativity)
- **Max Output Tokens**: 4000
- **Max Input Length**: 5000 characters

## 📖 Usage

### 1. Basic BRD Generation

1. **Navigate** to the BRD Agent dashboard
2. **Describe** your project in the Project Description section
3. **Add** any additional context or requirements
4. **Click** "Generate BRD Document"
5. **Review** the AI-generated BRD
6. **Download** in Markdown or PDF format

### 2. Enhanced BRD Generation with Files

1. **Upload** supporting documents (PDF, MD, DOCX)
2. **Provide** project description
3. **Generate** comprehensive BRD with enhanced context
4. **Download** your professional BRD

### 3. Existing BRD Improvement

1. **Upload** your current BRD document
2. **Specify** improvement requirements
3. **Let AI** analyze and enhance your document
4. **Download** the improved version

## 🔌 API Endpoints

### Generate BRD from Input
```http
POST /api/generate_brd_from_input
Content-Type: application/json

{
  "project_description": "Your project description here",
  "model": "gemini-2.0-flash"
}
```

### Generate BRD with Files
```http
POST /api/generate_brd_with_files
Content-Type: application/json

{
  "project_description": "Your project description",
  "uploaded_files": [
    {
      "filename": "requirements.pdf",
      "content": "File content here",
      "type": "application/pdf"
    }
  ],
  "model": "gemini-2.0-flash"
}
```

### Download BRD
```http
GET /api/download_brd/{project_name}
```

## 🛠️ Development

### Backend Development

```bash
cd backend

# Install development dependencies
pip install -r requirements.txt

# Run with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Run tests (if available)
python -m pytest
```

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

### Code Structure

- **Backend**: Follows FastAPI best practices with service-oriented architecture
- **Frontend**: React functional components with hooks and modern patterns
- **AI Integration**: Modular LLM service with fallback mechanisms
- **Error Handling**: Comprehensive error boundaries and user feedback

## 📁 File Processing

### Supported Formats
- **PDF**: Business documents, requirements, specifications
- **Markdown**: Technical documentation, README files
- **DOCX**: Word documents, project proposals

### File Limits
- **Maximum Size**: 10MB per file
- **Maximum Count**: 10 files per request
- **Content Length**: 50KB per file for processing

## 🔒 Security Features

- **CORS Configuration**: Secure cross-origin requests
- **Rate Limiting**: Per-client request throttling
- **Input Validation**: Comprehensive request validation
- **Environment Security**: Secure API key management

## 🚀 Deployment

### Production Deployment

1. **Environment Setup**
   ```bash
   # Set production environment variables
   export DEBUG=False
   export HOST=0.0.0.0
   export PORT=8000
   ```

2. **Backend Deployment**
   ```bash
   # Using Gunicorn
   gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
   ```

3. **Frontend Deployment**
   ```bash
   npm run build
   # Deploy dist/ folder to your web server
   ```

### Docker Deployment

```dockerfile
# Backend Dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🧪 Testing

### Backend Testing
```bash
cd backend
python -m pytest tests/
```

### Frontend Testing
```bash
cd frontend
npm test
```

## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Development Guidelines

- Follow PEP 8 for Python code
- Use ESLint and Prettier for JavaScript/React code
- Write comprehensive tests for new features
- Update documentation for API changes

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Google Gemini AI** for providing the LLM capabilities
- **FastAPI** for the robust backend framework
- **React** for the modern frontend framework
- **Tailwind CSS** for the beautiful UI components

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-repo/discussions)
- **Documentation**: [API Docs](http://localhost:8000/docs)

## 🔄 Version History

- **v3.0.0**: Google Gemini integration, enhanced file processing
- **v2.0.0**: React frontend, improved AI generation
- **v1.0.0**: Initial FastAPI backend implementation

---

**Made with ❤️ using AI and modern web technologies**
