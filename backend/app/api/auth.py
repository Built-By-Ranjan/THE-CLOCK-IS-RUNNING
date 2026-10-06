from datetime import datetime, timezone
import pyotp
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.config import settings
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    encrypt_mfa_secret,
    decrypt_mfa_secret,
)
from app.models.user import User
from app.schemas.auth import (
    UserRegister,
    UserLogin,
    UserResponse,
    TokenResponse,
    MFASetupResponse,
    MFAEnableRequest,
    MFADisableRequest,
    MFAResponse,
)
from app.api.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication & MFA"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: UserRegister, db: Session = Depends(get_db)):
    """Register a new user account with hashed password."""
    existing_user = db.query(User).filter(
        (User.username == user_in.username) | (User.email == user_in.email)
    ).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username or email is already registered",
        )

    now = datetime.now(timezone.utc)
    user = User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        is_active=True,
        mfa_enabled=False,
        created_at=now,
        updated_at=now,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=TokenResponse)
def login(login_in: UserLogin, db: Session = Depends(get_db)):
    """Authenticate user with username and password, requiring MFA OTP if enabled."""
    user = db.query(User).filter(User.username == login_in.username).first()
    if not user or not verify_password(login_in.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive",
        )

    # Check MFA if enabled
    if user.mfa_enabled:
        if not login_in.otp_code:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="MFA OTP code is required for this account",
            )
        try:
            plaintext_secret = decrypt_mfa_secret(user.encrypted_mfa_secret)
            totp = pyotp.TOTP(plaintext_secret)
            if not totp.verify(login_in.otp_code, valid_window=1):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid MFA OTP code",
                )
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid MFA OTP code or verification error",
            )

    token = create_access_token({"sub": user.username})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user,
    }


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Retrieve details for the currently authenticated user."""
    return current_user


@router.post("/mfa/setup", response_model=MFASetupResponse)
def setup_mfa(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Generate a new TOTP secret for the authenticated user and store it encrypted.
    Never exposes or persists plaintext secrets.
    """
    secret = pyotp.random_base32()
    encrypted_secret = encrypt_mfa_secret(secret)

    current_user.encrypted_mfa_secret = encrypted_secret
    # Do not set mfa_enabled=True until confirmed via /auth/mfa/enable
    current_user.updated_at = datetime.now(timezone.utc)
    db.commit()

    provisioning_uri = pyotp.totp.TOTP(secret).provisioning_uri(
        name=current_user.email,
        issuer_name=settings.PROJECT_NAME,
    )
    return {
        "secret": secret,
        "provisioning_uri": provisioning_uri,
    }


@router.post("/mfa/enable", response_model=MFAResponse)
def enable_mfa(
    req: MFAEnableRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Verify an initial OTP code against the configured secret and activate MFA."""
    if not current_user.encrypted_mfa_secret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA has not been initialized. Call /auth/mfa/setup first.",
        )

    try:
        secret = decrypt_mfa_secret(current_user.encrypted_mfa_secret)
        totp = pyotp.TOTP(secret)
        if not totp.verify(req.otp_code, valid_window=1):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid verification OTP code",
            )
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to verify MFA OTP",
        )

    current_user.mfa_enabled = True
    current_user.updated_at = datetime.now(timezone.utc)
    db.commit()

    return {
        "message": "MFA has been successfully enabled.",
        "mfa_enabled": True,
    }


@router.post("/mfa/disable", response_model=MFAResponse)
def disable_mfa(
    req: MFADisableRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Disable MFA on the account after verifying OTP code or password."""
    if not current_user.mfa_enabled:
        return {
            "message": "MFA is already disabled on this account.",
            "mfa_enabled": False,
        }

    verified = False
    if req.otp_code and current_user.encrypted_mfa_secret:
        try:
            secret = decrypt_mfa_secret(current_user.encrypted_mfa_secret)
            totp = pyotp.TOTP(secret)
            if totp.verify(req.otp_code, valid_window=1):
                verified = True
        except Exception:
            pass

    if not verified and req.password:
        if verify_password(req.password, current_user.hashed_password):
            verified = True

    if not verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Valid MFA OTP code or current account password is required to disable MFA",
        )

    current_user.mfa_enabled = False
    current_user.encrypted_mfa_secret = None
    current_user.updated_at = datetime.now(timezone.utc)
    db.commit()

    return {
        "message": "MFA has been disabled.",
        "mfa_enabled": False,
    }
