from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)


class UserLogin(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    mfa_enabled: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class LoginMFAChallengeResponse(BaseModel):
    mfa_required: bool = True
    challenge_id: str
    email_masked: str
    expires_in_seconds: int


class MFAVerifyRequest(BaseModel):
    challenge_id: str
    otp: str = Field(..., min_length=6, max_length=6)


class MFAResendRequest(BaseModel):
    challenge_id: str


class MFAResendResponse(BaseModel):
    message: str
    challenge_id: str
    cooldown_seconds: int
    expires_in_seconds: int
