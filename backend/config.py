#!/usr/bin/env python3
"""
Configuration file for BRD Agent
Centralizes all constants, limits, and configuration values
"""

import os
from typing import Dict, Any

def _load_environment():
    """Load environment variables from .env file"""
    try:
        from dotenv import load_dotenv
        load_dotenv()
        return True
    except ImportError:
        return False

def _get_env(key: str, default: str = None, convert_type=None):
    """Get environment variable with optional type conversion"""
    value = os.getenv(key, default)
    if convert_type and value is not None:
        try:
            return convert_type(value)
        except (ValueError, TypeError):
            return default
    return value

# Load environment variables immediately
_load_environment()

class Config:
    """Centralized configuration for BRD Agent"""
    
    # API Configuration
    API_HOST = _get_env("HOST", "0.0.0.0")
    API_PORT = _get_env("PORT", 8000, int)
    API_DEBUG = _get_env("DEBUG", "False", lambda x: x.lower() == "true")
    
    # Security Configuration
    SECRET_KEY = _get_env("SECRET_KEY")
    CORS_ORIGINS = _get_env("ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")
    CORS_CREDENTIALS = _get_env("CORS_CREDENTIALS", "true", lambda x: x.lower() == "true")
    
    # Google Gemini Configuration
    GOOGLE_API_KEY = _get_env("GOOGLE_API_KEY")
    GOOGLE_MODEL = _get_env("GOOGLE_MODEL", "gemini-2.0-flash")
    
    # LLM Configuration
    MAX_INPUT_LENGTH = 5000
    MAX_OUTPUT_TOKENS = 4000
    LLM_TEMPERATURE = 0.3
    
    # File Processing Configuration
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    MAX_FILES_COUNT = 10
    MAX_FILE_CONTENT_LENGTH = 50000
    
    # BRD Configuration
    MAX_PROJECT_NAME_LENGTH = 50
    MIN_PROJECT_DESCRIPTION_LENGTH = 10
    MAX_PROJECT_DESCRIPTION_LENGTH = 5000
    
    # Rate Limiting Configuration
    RATE_LIMIT_MAX_REQUESTS = 100
    RATE_LIMIT_WINDOW_SECONDS = 3600  # 1 hour
    
    # Validation Rules
    VALID_FILE_TYPES = [
        'application/pdf',
        'text/markdown', 
        'text/x-markdown',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    ]
    
    @classmethod
    def validate(cls) -> Dict[str, Any]:
        """Validate configuration and return status"""
        validation_results = {
            'valid': True,
            'warnings': [],
            'errors': []
        }
        
        # Check required configurations
        if not cls.SECRET_KEY:
            validation_results['warnings'].append("SECRET_KEY not set - will generate random key")
        
        if not cls.GOOGLE_API_KEY or cls.GOOGLE_API_KEY.startswith('your_'):
            validation_results['warnings'].append("GOOGLE_API_KEY not set - LLM features will use fallback mode")
        
        # Check security configurations
        if cls.API_HOST == "0.0.0.0" and not cls.API_DEBUG:
            validation_results['warnings'].append("Running in production with 0.0.0.0 host - consider restricting")
        
        return validation_results
    
    @classmethod
    def get_llm_config(cls) -> Dict[str, Any]:
        """Get LLM-specific configuration"""
        return {
            'model': cls.GOOGLE_MODEL,
            'max_output_tokens': cls.MAX_OUTPUT_TOKENS,
            'temperature': cls.LLM_TEMPERATURE
        }
    
    @classmethod
    def get_file_config(cls) -> Dict[str, Any]:
        """Get file processing configuration"""
        return {
            'max_size': cls.MAX_FILE_SIZE,
            'max_count': cls.MAX_FILES_COUNT,
            'max_content_length': cls.MAX_FILE_CONTENT_LENGTH,
            'valid_types': cls.VALID_FILE_TYPES
        }
    

