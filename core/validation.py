"""
Input validation and security utilities for Vectorpenter
"""

import re
import html
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, validator, Field
from pathlib import Path

from core.logging import logger


class QueryRequest(BaseModel):
    """Validated query request model"""
    query: str = Field(..., min_length=1, max_length=10000)
    k: Optional[int] = Field(default=12, ge=1, le=100)
    hybrid: Optional[bool] = Field(default=False)
    rerank: Optional[bool] = Field(default=False)
    namespace: Optional[str] = Field(default=None, max_length=100)
    
    @validator('query')
    def validate_query(cls, v):
        """Validate and sanitize query string"""
        if not v.strip():
            raise ValueError('Query cannot be empty or only whitespace')
        
        # Remove potentially dangerous characters
        sanitized = html.escape(v.strip())
        
        # Check for suspicious patterns
        suspicious_patterns = [
            r'<script.*?>.*?</script>',
            r'javascript:',
            r'data:text/html',
            r'vbscript:',
            r'onload\s*=',
            r'onerror\s*='
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, sanitized, re.IGNORECASE):
                raise ValueError('Query contains potentially unsafe content')
        
        return sanitized
    
    @validator('k')
    def validate_k(cls, v):
        """Validate k parameter"""
        if v <= 0:
            raise ValueError('k must be positive')
        if v > 100:
            raise ValueError('k cannot exceed 100 for performance reasons')
        return v
    
    @validator('namespace')
    def validate_namespace(cls, v):
        """Validate namespace parameter"""
        if v is None:
            return v
        
        # Only allow alphanumeric, hyphens, and underscores
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Namespace can only contain alphanumeric characters, hyphens, and underscores')
        
        return v.lower()


class IngestRequest(BaseModel):
    """Validated ingestion request model"""
    path: str = Field(..., min_length=1)
    force_reindex: Optional[bool] = Field(default=False)
    
    @validator('path')
    def validate_path(cls, v):
        """Validate file path"""
        if not v.strip():
            raise ValueError('Path cannot be empty')
        
        # Basic path sanitization
        sanitized_path = str(Path(v.strip()).resolve())
        
        # Check if path exists
        if not Path(sanitized_path).exists():
            raise ValueError(f'Path does not exist: {sanitized_path}')
        
        # Security check - prevent directory traversal
        if '..' in v or '~' in v:
            raise ValueError('Path contains potentially unsafe directory traversal')
        
        return sanitized_path


class ConfigValidation:
    """Configuration validation utilities"""
    
    @staticmethod
    def validate_api_key(key: Optional[str], service_name: str) -> bool:
        """Validate API key format"""
        if not key:
            return False
        
        key = key.strip()
        
        # Basic format checks for common API key patterns
        api_key_patterns = {
            'openai': r'^sk-[a-zA-Z0-9]{48,}$',
            'pinecone': r'^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$',
            'voyage': r'^pa-[a-zA-Z0-9_-]{20,}$'
        }
        
        pattern = api_key_patterns.get(service_name.lower())
        if pattern and not re.match(pattern, key):
            logger.warning(f"API key for {service_name} doesn't match expected format")
            return False
        
        return len(key) >= 10  # Minimum reasonable key length
    
    @staticmethod
    def validate_url(url: Optional[str]) -> bool:
        """Validate URL format"""
        if not url:
            return False
        
        url_pattern = r'^https?://[a-zA-Z0-9.-]+(?:\:[0-9]+)?(?:/.*)?$'
        return bool(re.match(url_pattern, url))
    
    @staticmethod
    def validate_database_url(db_url: str) -> bool:
        """Validate database URL format"""
        if not db_url:
            return False
        
        # Support SQLite and PostgreSQL URLs
        sqlite_pattern = r'^sqlite:///.*\.db$'
        postgres_pattern = r'^postgresql://.*'
        
        return bool(re.match(sqlite_pattern, db_url) or re.match(postgres_pattern, db_url))


class InputSanitizer:
    """Input sanitization utilities"""
    
    @staticmethod
    def sanitize_text(text: str, max_length: int = 100000) -> str:
        """Sanitize text input"""
        if not isinstance(text, str):
            raise ValueError("Input must be a string")
        
        # Truncate if too long
        if len(text) > max_length:
            text = text[:max_length]
            logger.warning(f"Text truncated to {max_length} characters")
        
        # HTML escape for safety
        sanitized = html.escape(text)
        
        # Remove null bytes and other control characters
        sanitized = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', sanitized)
        
        return sanitized
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename for safe storage"""
        if not isinstance(filename, str):
            raise ValueError("Filename must be a string")
        
        # Remove path separators and dangerous characters
        dangerous_chars = r'[<>:"/\\|?*\x00-\x1f]'
        sanitized = re.sub(dangerous_chars, '_', filename)
        
        # Limit length
        if len(sanitized) > 255:
            name, ext = Path(sanitized).stem, Path(sanitized).suffix
            sanitized = name[:250-len(ext)] + ext
        
        return sanitized


class SecurityValidator:
    """Security validation utilities"""
    
    @staticmethod
    def check_rate_limit(user_id: str, action: str, limit: int = 100, window: int = 3600) -> bool:
        """
        Check if user is within rate limits
        
        Args:
            user_id: User identifier
            action: Action being performed
            limit: Maximum actions per window
            window: Time window in seconds
            
        Returns:
            True if within limits, False otherwise
        """
        # TODO: Implement actual rate limiting with Redis or in-memory store
        # For now, always return True
        return True
    
    @staticmethod
    def validate_file_safety(file_path: Path) -> bool:
        """
        Validate that file is safe to process
        
        Args:
            file_path: Path to file
            
        Returns:
            True if file is safe, False otherwise
        """
        if not file_path.exists():
            return False
        
        # Check file size (max 100MB)
        max_size = 100 * 1024 * 1024
        if file_path.stat().st_size > max_size:
            logger.warning(f"File {file_path} exceeds maximum size of {max_size} bytes")
            return False
        
        # Check file extension
        allowed_extensions = {'.pdf', '.txt', '.md', '.docx', '.pptx', '.csv', '.xlsx'}
        if file_path.suffix.lower() not in allowed_extensions:
            logger.warning(f"File {file_path} has unsupported extension")
            return False
        
        return True
    
    @staticmethod
    def detect_pii(text: str) -> List[str]:
        """
        Detect potential PII in text
        
        Args:
            text: Text to scan
            
        Returns:
            List of detected PII types
        """
        pii_patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
            'credit_card': r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'
        }
        
        detected = []
        for pii_type, pattern in pii_patterns.items():
            if re.search(pattern, text):
                detected.append(pii_type)
        
        if detected:
            logger.warning(f"Potential PII detected: {', '.join(detected)}")
        
        return detected


def validate_environment() -> Dict[str, bool]:
    """
    Validate environment configuration
    
    Returns:
        Dictionary of validation results
    """
    from core.config import settings
    
    validation_results = {}
    
    # Required services
    validation_results['openai_api_key'] = ConfigValidation.validate_api_key(
        settings.openai_api_key, 'openai'
    )
    validation_results['pinecone_api_key'] = ConfigValidation.validate_api_key(
        settings.pinecone_api_key, 'pinecone'
    )
    
    # Optional services
    validation_results['voyage_api_key'] = (
        settings.voyage_api_key is None or 
        ConfigValidation.validate_api_key(settings.voyage_api_key, 'voyage')
    )
    validation_results['typesense_api_key'] = (
        settings.typesense_api_key is None or
        len(settings.typesense_api_key.strip()) > 0
    )
    
    # Database URL
    validation_results['database_url'] = ConfigValidation.validate_database_url(settings.db_url)
    
    # Log validation results
    for service, is_valid in validation_results.items():
        if not is_valid:
            logger.error(f"Invalid configuration for {service}")
        else:
            logger.debug(f"Valid configuration for {service}")
    
    return validation_results


def startup_validation() -> bool:
    """
    Perform startup validation checks
    
    Returns:
        True if all critical validations pass
    """
    logger.info("Performing startup validation...")
    
    validation_results = validate_environment()
    
    # Check critical services
    critical_services = ['openai_api_key', 'pinecone_api_key', 'database_url']
    
    for service in critical_services:
        if not validation_results.get(service, False):
            logger.error(f"Critical service validation failed: {service}")
            return False
    
    logger.info("Startup validation completed successfully")
    return True
