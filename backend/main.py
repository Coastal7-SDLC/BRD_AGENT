#!/usr/bin/env python3
"""
FastAPI application for BRD Agent - LLM-Powered with Google Gemini Integration
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import logging
from datetime import datetime, timezone

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables first, before importing any other modules
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not available, using system environment variables
except Exception:
    pass  # Error loading .env file, using system environment variables

from routes.llm_routes import router as llm_router
from services.llm_service import LLMService
from config import Config

def validate_environment():
    """Validate required environment variables"""
    required_vars = {
        'SECRET_KEY': 'Secret key for security'
    }
    
    # Google API key is optional (service works with fallback)
    google_key = os.environ.get('GOOGLE_API_KEY')
    if not google_key or google_key.startswith('your_'):
        print("⚠️ Google API key not configured - using fallback mode")
    else:
        print("✅ Google API key configured")
    
    missing_vars = []
    for var, description in required_vars.items():
        if not os.environ.get(var) or os.environ.get(var).startswith('your_'):
            missing_vars.append(f"{var}: {description}")
    
    if missing_vars:
        print("❌ Missing environment variables - check your .env file")
        return False
    
    return True

# Load environment variables
load_dotenv()

# Set default SECRET_KEY for development if not provided
if not os.environ.get('SECRET_KEY'):
    import secrets
    os.environ['SECRET_KEY'] = secrets.token_urlsafe(32)
    print("⚠️ Generated random SECRET_KEY for development")

# Create FastAPI app
app = FastAPI(
    title="BRD Agent API",
            description="LLM-Powered Business Requirements Document Generator with Google Gemini Integration",
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=Config.CORS_ORIGINS,
    allow_credentials=Config.CORS_CREDENTIALS,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Initialize LLM service
llm_service = LLMService()

# Include routers
app.include_router(llm_router, prefix="/api", tags=["LLM"])

# Root route - Redirect to frontend
@app.get("/")
async def root():
    """Redirect to frontend application"""
    return {
        "message": "BRD Agent API",
        "frontend_url": "http://localhost:3000",
        "api_docs": "/docs",
        "health_check": "/health"
    }

# API info route
@app.get("/api-info")
async def api_info():
    """Get API information"""
    return {
        'message': 'BRD Agent - LLM-Powered API with Google Gemini Integration',
        'version': '3.0.0',
        'framework': 'FastAPI',
        'database': 'None (In-Memory Storage)',
        'endpoints': {
            'generate_brd_from_input': '/api/generate_brd_from_input',
            'generate_brd_with_files': '/api/generate_brd_with_files',
            'download_brd': '/api/download_brd/{project_name}'
        },
        'llm_provider': {
            'google_gemini': f'Primary provider - Direct access to {Config.GOOGLE_MODEL} model for BRD generation and improvement'
        },
        'features': {
            'brd_generation': 'Generate new BRD documents from text input and files',
            'brd_improvement': 'Analyze and improve existing BRD documents using AI',
            'file_processing': 'Support for PDF, Markdown, and DOCX files',
            'ai_enhancement': 'AI-powered content analysis and improvement'
        },
        'usage': 'Use the web interface at / for BRD generation and improvement'
    }

# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check LLM service status
        llm_status = "available"
        
        # Simple check if Google API key is configured
        google_key = Config.GOOGLE_API_KEY
        if google_key and not google_key.startswith('your_'):
            llm_status = "available"
        else:
            llm_status = "fallback_mode"  # Service works but with fallback
        
        # Service is healthy even in fallback mode
        overall_status = "healthy"
        
        return {
            "status": overall_status,
            "llm_service": llm_status,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    # Get configuration from environment
    host = Config.API_HOST
    port = Config.API_PORT
    debug = Config.API_DEBUG
    
    # Security check for production
    if not debug and host == "0.0.0.0":
        print("⚠️ WARNING: Running in production mode with 0.0.0.0 host")
    
    print("🚀 BRD Agent starting...")
    
    # Validate environment configuration
    if not validate_environment():
        print("❌ Environment validation failed. Please check your .env file.")
        import sys
        sys.exit(1)
    
    # Check Google API key (minimal output)
    google_key = Config.GOOGLE_API_KEY
    if google_key and not google_key.startswith('your_'):
        logger.info("✅ Google Gemini configured")
    else:
        logger.warning("⚠️ Using fallback mode (no API key)")
    
    # Start the server
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    )
