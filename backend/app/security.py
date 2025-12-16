"""
Security utilities for the RF Spectrum Analyzer API
- Rate limiting
- Authentication
- Input validation
"""

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets
from typing import Optional
from functools import wraps

from .config import settings

# Basic HTTP Authentication
security = HTTPBasic(auto_error=False)

def verify_credentials(credentials: Optional[HTTPBasicCredentials] = Depends(security)) -> bool:
    """
    Verify HTTP Basic Auth credentials.
    Returns True if auth is disabled or credentials are valid.
    """
    if not settings.ENABLE_AUTH:
        return True
    
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    correct_username = secrets.compare_digest(
        credentials.username.encode("utf8"),
        settings.AUTH_USERNAME.encode("utf8")
    )
    correct_password = secrets.compare_digest(
        credentials.password.encode("utf8"),
        settings.AUTH_PASSWORD.encode("utf8")
    )
    
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    return True

def validate_file_size(content: bytes, max_size_mb: int = None) -> bool:
    """
    Validate file size is within limits.
    """
    max_size = (max_size_mb or settings.MAX_UPLOAD_SIZE_MB) * 1024 * 1024
    if len(content) > max_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE_MB}MB"
        )
    return True

def sanitize_string(value: str, max_length: int = 255) -> str:
    """
    Sanitize string input to prevent injection attacks.
    """
    if value is None:
        return None
    
    # Remove null bytes
    value = value.replace('\x00', '')
    
    # Truncate to max length
    value = value[:max_length]
    
    # Remove potentially dangerous characters for SQL
    dangerous_chars = [';', '--', '/*', '*/', 'xp_', 'UNION', 'SELECT', 'DROP', 'DELETE', 'INSERT', 'UPDATE']
    value_upper = value.upper()
    for char in dangerous_chars:
        if char.upper() in value_upper:
            # Only block if it looks like SQL injection attempt
            if any(x in value_upper for x in ['SELECT', 'DROP', 'DELETE', 'INSERT', 'UPDATE', 'UNION']):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid characters in input"
                )
    
    return value

def validate_numeric_range(value: float, min_val: float = None, max_val: float = None, name: str = "value") -> float:
    """
    Validate numeric value is within acceptable range.
    """
    if value is None:
        return None
    
    if min_val is not None and value < min_val:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{name} must be at least {min_val}"
        )
    
    if max_val is not None and value > max_val:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{name} must be at most {max_val}"
        )
    
    return value

def get_client_ip(request: Request) -> str:
    """
    Get client IP address, considering proxy headers.
    """
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"
