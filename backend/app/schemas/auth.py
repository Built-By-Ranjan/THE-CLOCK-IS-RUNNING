from pydantic import BaseModel


class LoginRequest(BaseModel):  # Define the login request payload.
    email: str
    password: str


class TokenResponse(BaseModel):  # Define the access-token response payload.
    access_token: str
    token_type: str
    expires_in: int
