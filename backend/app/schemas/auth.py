from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)


class UserLogin(BaseModel):
    username: str
    password: str
    otp_code: Optional[str] = None


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


class MFASetupResponse(BaseModel):
    secret: str
    provisioning_uri: str


class MFAEnableRequest(BaseModel):
    otp_code: str = Field(..., min_length=6, max_length=6)


class MFADisableRequest(BaseModel):
    otp_code: Optional[str] = None
    password: Optional[str] = None


class MFAResponse(BaseModel):
    message: str
    mfa_enabled: bool
