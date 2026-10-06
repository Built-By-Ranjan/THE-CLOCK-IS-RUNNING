import base64
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import bcrypt
from cryptography.fernet import Fernet
from jose import JWTError, jwt

from app.core.config import settings


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a bcrypt hashed password."""
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Generate a signed JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify and decode a JWT access token."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None


def _get_fernet() -> Fernet:
    """Retrieve or derive a Fernet cipher instance for MFA secret encryption."""
    if settings.MFA_ENCRYPTION_KEY and len(settings.MFA_ENCRYPTION_KEY) == 44:
        key = settings.MFA_ENCRYPTION_KEY.encode("utf-8")
    else:
        # Deterministically derive 32-byte key from settings.SECRET_KEY
        derived = hashlib.sha256(settings.SECRET_KEY.encode("utf-8")).digest()
        key = base64.urlsafe_b64encode(derived)
    return Fernet(key)


def encrypt_mfa_secret(secret: str) -> str:
    """Encrypt a plaintext TOTP secret before persisting."""
    cipher = _get_fernet()
    return cipher.encrypt(secret.encode("utf-8")).decode("utf-8")


def decrypt_mfa_secret(encrypted_secret: str) -> str:
    """Decrypt an encrypted TOTP secret."""
    cipher = _get_fernet()
    return cipher.decrypt(encrypted_secret.encode("utf-8")).decode("utf-8")


def generate_otp() -> str:
    """Generate a cryptographically secure 6-digit numeric OTP code."""
    code = secrets.randbelow(1_000_000)
    return f"{code:06d}"


def hash_otp(otp: str, salt: str = "") -> str:
    """Hash an OTP code using HMAC-SHA256 with the server SECRET_KEY and an optional salt."""
    key = f"{settings.SECRET_KEY}:{salt}".encode("utf-8")
    return hmac.new(key, otp.encode("utf-8"), hashlib.sha256).hexdigest()


def verify_otp_hash(plain_otp: str, hashed_otp: str, salt: str = "") -> bool:
    """Constant-time verification of an OTP code against its stored hash."""
    expected = hash_otp(plain_otp, salt=salt)
    return hmac.compare_digest(expected, hashed_otp)


def mask_email(email: str) -> str:
    """Mask email address for privacy in API responses, e.g. a***t@defense.corp."""
    if "@" not in email:
        return email
    local, domain = email.split("@", 1)
    if len(local) <= 2:
        masked_local = f"{local[0]}*" if local else "*"
    else:
        masked_local = f"{local[0]}{'*' * (len(local) - 2)}{local[-1]}"
    return f"{masked_local}@{domain}"
