"""Security hardening patches for NemoClaw Gateway.

Apply these improvements to enhance security posture.
"""

import hashlib
import secrets
import hmac
from datetime import datetime, timedelta
from typing import Optional
import re

class SecurityHardening:
    """Security hardening utilities."""
    
    @staticmethod
    def hash_password(password: str, salt: Optional[str] = None) -> tuple[str, str]:
        """Securely hash password with salt using PBKDF2."""
        if salt is None:
            salt = secrets.token_hex(32)
        
        # Use PBKDF2 with SHA256, 100k iterations
        key = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000  # 100k iterations
        )
        return key.hex(), salt
    
    @staticmethod
    def verify_password(password: str, hash_value: str, salt: str) -> bool:
        """Verify password against hash."""
        computed_hash, _ = SecurityHardening.hash_password(password, salt)
        return hmac.compare_digest(computed_hash, hash_value)
    
    @staticmethod
    def generate_secure_token(length: int = 32) -> str:
        """Generate cryptographically secure token."""
        return secrets.token_urlsafe(length)
    
    @staticmethod
    def sanitize_input(value: str, max_length: int = 255) -> str:
        """Sanitize user input to prevent injection."""
        # Remove control characters
        sanitized = ''.join(char for char in value if ord(char) >= 32)
        # Limit length
        return sanitized[:max_length]
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_password_strength(password: str) -> tuple[bool, str]:
        """Check password strength."""
        if len(password) < 12:
            return False, "Password must be at least 12 characters"
        if not re.search(r'[A-Z]', password):
            return False, "Password must contain uppercase letter"
        if not re.search(r'[a-z]', password):
            return False, "Password must contain lowercase letter"
        if not re.search(r'\d', password):
            return False, "Password must contain digit"
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, "Password must contain special character"
        return True, "Password is strong"

class RateLimiter:
    """Simple in-memory rate limiter."""
    
    def __init__(self, max_requests: int = 5, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window = window_seconds
        self._store: dict[str, list[datetime]] = {}
    
    def is_allowed(self, key: str) -> bool:
        """Check if request is allowed."""
        now = datetime.now()
        window_start = now - timedelta(seconds=self.window)
        
        # Get requests in window
        requests = self._store.get(key, [])
        requests = [r for r in requests if r > window_start]
        
        if len(requests) >= self.max_requests:
            return False
        
        requests.append(now)
        self._store[key] = requests
        return True
    
    def time_until_reset(self, key: str) -> int:
        """Get seconds until rate limit resets."""
        requests = self._store.get(key, [])
        if not requests:
            return 0
        oldest = min(requests)
        reset_time = oldest + timedelta(seconds=self.window)
        remaining = (reset_time - datetime.now()).total_seconds()
        return max(0, int(remaining))

class InputValidator:
    """Input validation utilities."""
    
    # Whitelist patterns for common inputs
    SANDBOX_NAME_PATTERN = re.compile(r'^[a-zA-Z0-9_-]{3,64}$')
    UUID_PATTERN = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')
    PATH_PATTERN = re.compile(r'^[a-zA-Z0-9_/.-]+$')
    
    @classmethod
    def validate_sandbox_name(cls, name: str) -> bool:
        """Validate sandbox name format."""
        return bool(cls.SANDBOX_NAME_PATTERN.match(name))
    
    @classmethod
    def validate_uuid(cls, value: str) -> bool:
        """Validate UUID format."""
        return bool(cls.UUID_PATTERN.match(value))
    
    @classmethod
    def validate_path(cls, path: str) -> bool:
        """Validate file path format."""
        # Prevent path traversal
        if '..' in path or '~' in path:
            return False
        return bool(cls.PATH_PATTERN.match(path))
    
    @classmethod
    def sanitize_filename(cls, filename: str) -> str:
        """Sanitize filename to prevent directory traversal."""
        # Remove path components
        filename = filename.replace('/', '_').replace('\\', '_')
        # Remove null bytes
        filename = filename.replace('\x00', '')
        # Limit length
        return filename[:255]

# Security headers for Streamlit
SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'",
    "Referrer-Policy": "strict-origin-when-cross-origin"
}

# Session configuration
SESSION_CONFIG = {
    "max_age_hours": 8,
    "idle_timeout_minutes": 30,
    "require_reauth_for_sensitive": True,
    "rotate_session_on_privilege_change": True
}

# Audit logging configuration
AUDIT_CONFIG = {
    "log_all_auth_events": True,
    "log_all_admin_actions": True,
    "log_data_access": True,
    "retention_days": 2555,  # 7 years
    "immutable_logs": True,
    "sign_logs": True
}
