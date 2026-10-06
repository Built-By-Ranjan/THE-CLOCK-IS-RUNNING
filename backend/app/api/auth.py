import uuid
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.config import settings
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    generate_otp,
    hash_otp,
    verify_otp_hash,
    mask_email,
)
from app.models.user import User
from app.models.mfa import MFAChallenge
from app.schemas.auth import (
    UserRegister,
    UserLogin,
    UserResponse,
    TokenResponse,
    LoginMFAChallengeResponse,
    MFAVerifyRequest,
    MFAResendRequest,
    MFAResendResponse,
)
from app.services.email_service import EmailService, EmailDeliveryError
from app.api.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication & MFA"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: UserRegister, db: Session = Depends(get_db)):
    """Register a new user account with hashed password and email-based MFA enabled."""
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
        mfa_enabled=True,
        created_at=now,
        updated_at=now,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=LoginMFAChallengeResponse)
def login(login_in: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate user credentials (username or email + password).
    Does NOT issue the final JWT.
    Generates a cryptographically secure 6-digit OTP, stores its secure hash,
    sends it via Gmail SMTP, and returns an MFA challenge ID.
    """
    identifier = (login_in.email or login_in.username or "").strip()
    if not identifier:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email is required",
        )

    user = db.query(User).filter(
        (User.username == identifier) | (User.email == identifier)
    ).first()

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

    # Invalidate previous unused challenges for this user
    previous_challenges = db.query(MFAChallenge).filter(
        MFAChallenge.user_id == user.id,
        MFAChallenge.is_used.is_(False),
    ).all()
    for prev in previous_challenges:
        prev.is_used = True

    # Generate cryptographically secure OTP & hash
    otp = generate_otp()
    otp_h = hash_otp(otp, salt=str(user.id))

    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(minutes=settings.OTP_EXPIRY_MINUTES)
    challenge_id = uuid.uuid4().hex

    challenge = MFAChallenge(
        challenge_id=challenge_id,
        user_id=user.id,
        otp_hash=otp_h,
        attempts=0,
        max_attempts=settings.OTP_MAX_ATTEMPTS,
        is_used=False,
        created_at=now,
        expires_at=expires_at,
        last_sent_at=now,
    )
    db.add(challenge)
    db.commit()

    # Deliver OTP via Gmail SMTP
    try:
        EmailService.send_otp_email(user.email, otp)
    except EmailDeliveryError:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to deliver verification code via email. Please check email service configuration or try again later.",
        )

    return {
        "mfa_required": True,
        "challenge_id": challenge.challenge_id,
        "email_masked": mask_email(user.email),
        "expires_in_seconds": settings.OTP_EXPIRY_MINUTES * 60,
    }


@router.post("/mfa/verify", response_model=TokenResponse)
def verify_mfa(req: MFAVerifyRequest, db: Session = Depends(get_db)):
    """
    Verify the 6-digit email OTP against the MFA challenge.
    Upon successful single-use verification, issues the authenticated JWT access token.
    Enforces expiration and maximum failed attempts.
    """
    challenge = db.query(MFAChallenge).filter(
        MFAChallenge.challenge_id == req.challenge_id
    ).first()

    if not challenge:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired MFA challenge",
        )

    if challenge.is_used:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA challenge has already been used",
        )

    if challenge.attempts >= challenge.max_attempts:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Maximum verification attempts exceeded. Please log in again.",
        )

    now = datetime.now(timezone.utc)
    if now > challenge.expires_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification code has expired. Please request a new code or log in again.",
        )

    # Constant-time OTP hash verification
    if not verify_otp_hash(req.otp, challenge.otp_hash, salt=str(challenge.user_id)):
        challenge.attempts += 1
        db.commit()
        remaining = max(0, challenge.max_attempts - challenge.attempts)
        if remaining == 0:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Maximum verification attempts exceeded. Please log in again.",
            )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid verification code. {remaining} attempt(s) remaining.",
        )

    # Valid OTP: mark challenge as used
    challenge.is_used = True
    db.commit()

    user = db.query(User).filter(User.id == challenge.user_id).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    token = create_access_token({"sub": user.username})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user,
    }


@router.post("/mfa/resend", response_model=MFAResendResponse)
def resend_mfa(req: MFAResendRequest, db: Session = Depends(get_db)):
    """
    Resend a new 6-digit email OTP for an active MFA challenge.
    Invalidates the previous OTP and enforces a 60-second cooldown.
    """
    challenge = db.query(MFAChallenge).filter(
        MFAChallenge.challenge_id == req.challenge_id
    ).first()

    if not challenge:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid MFA challenge",
        )

    if challenge.is_used:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA challenge has already been completed",
        )

    if challenge.attempts >= challenge.max_attempts:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Challenge has been locked due to excessive failed attempts. Please log in again.",
        )

    now = datetime.now(timezone.utc)
    elapsed = (now - challenge.last_sent_at).total_seconds()
    if elapsed < settings.OTP_RESEND_COOLDOWN_SECONDS:
        wait_seconds = int(settings.OTP_RESEND_COOLDOWN_SECONDS - elapsed)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Please wait {wait_seconds} seconds before requesting a new verification code.",
        )

    # Generate new OTP, invalidate previous OTP by updating hash & timestamps
    new_otp = generate_otp()
    challenge.otp_hash = hash_otp(new_otp, salt=str(challenge.user_id))
    challenge.last_sent_at = now
    challenge.expires_at = now + timedelta(minutes=settings.OTP_EXPIRY_MINUTES)
    db.commit()

    user = db.query(User).filter(User.id == challenge.user_id).first()
    try:
        EmailService.send_otp_email(user.email, new_otp)
    except EmailDeliveryError:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to deliver verification code via email. Please check email service configuration or try again later.",
        )

    return {
        "message": "A new verification code has been sent to your email.",
        "challenge_id": challenge.challenge_id,
        "cooldown_seconds": settings.OTP_RESEND_COOLDOWN_SECONDS,
        "expires_in_seconds": settings.OTP_EXPIRY_MINUTES * 60,
    }


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Retrieve details for the currently authenticated user."""
    return current_user
