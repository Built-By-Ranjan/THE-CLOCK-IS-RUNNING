import pyotp
import pytest
from app.models.user import User
from app.core.security import decrypt_mfa_secret


def test_user_registration_and_password_hashing(client, db):
    payload = {
        "username": "alice",
        "email": "alice@example.com",
        "password": "SuperSecretPassword123!",
    }
    resp = client.post("/auth/register", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["username"] == "alice"
    assert data["email"] == "alice@example.com"
    assert data["mfa_enabled"] is False

    # Verify password is never stored in plaintext
    user = db.query(User).filter(User.username == "alice").first()
    assert user is not None
    assert user.hashed_password != payload["password"]
    assert user.hashed_password.startswith("$2b$") or user.hashed_password.startswith("$2a$")

    # Duplicate username/email conflict
    resp_dup = client.post("/auth/register", json=payload)
    assert resp_dup.status_code == 409


def test_login_and_token_authentication(client):
    reg = {
        "username": "bob",
        "email": "bob@example.com",
        "password": "Password123!",
    }
    client.post("/auth/register", json=reg)

    # Wrong password
    bad_login = client.post("/auth/login", json={"username": "bob", "password": "WrongPassword"})
    assert bad_login.status_code == 401

    # Valid login
    login_resp = client.post("/auth/login", json={"username": "bob", "password": "Password123!"})
    assert login_resp.status_code == 200
    token_data = login_resp.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"
    token = token_data["access_token"]

    # Access protected /auth/me
    headers = {"Authorization": f"Bearer {token}"}
    me_resp = client.get("/auth/me", headers=headers)
    assert me_resp.status_code == 200
    assert me_resp.json()["username"] == "bob"

    # Protected route with missing or invalid token
    assert client.get("/auth/me").status_code == 401
    assert client.get("/auth/me", headers={"Authorization": "Bearer invalidtoken"}).status_code == 401


def test_totp_mfa_full_lifecycle(client, db):
    # 1. Register & login user
    reg = {
        "username": "charlie",
        "email": "charlie@example.com",
        "password": "CharliePassword123!",
    }
    client.post("/auth/register", json=reg)
    login_resp = client.post("/auth/login", json={"username": "charlie", "password": "CharliePassword123!"})
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. MFA Setup
    setup_resp = client.post("/auth/mfa/setup", headers=headers)
    assert setup_resp.status_code == 200
    setup_data = setup_resp.json()
    secret = setup_data["secret"]
    assert "provisioning_uri" in setup_data
    assert "otpauth://" in setup_data["provisioning_uri"]

    # Verify secret is protected and not stored plaintext in db
    user = db.query(User).filter(User.username == "charlie").first()
    assert user.encrypted_mfa_secret != secret
    assert decrypt_mfa_secret(user.encrypted_mfa_secret) == secret
    assert user.mfa_enabled is False

    # 3. MFA Enable with invalid OTP
    bad_enable = client.post("/auth/mfa/enable", json={"otp_code": "000000"}, headers=headers)
    assert bad_enable.status_code == 400

    # 4. MFA Enable with valid OTP
    valid_otp = pyotp.TOTP(secret).now()
    enable_resp = client.post("/auth/mfa/enable", json={"otp_code": valid_otp}, headers=headers)
    assert enable_resp.status_code == 200
    assert enable_resp.json()["mfa_enabled"] is True

    # 5. Login with MFA enabled
    # Attempt login without OTP -> 401
    no_otp = client.post("/auth/login", json={"username": "charlie", "password": "CharliePassword123!"})
    assert no_otp.status_code == 401
    assert "MFA OTP code is required" in no_otp.json()["detail"]

    # Attempt login with invalid OTP -> 401
    wrong_otp = client.post("/auth/login", json={"username": "charlie", "password": "CharliePassword123!", "otp_code": "999999"})
    assert wrong_otp.status_code == 401

    # Attempt login with valid OTP -> 200
    fresh_otp = pyotp.TOTP(secret).now()
    good_login = client.post("/auth/login", json={"username": "charlie", "password": "CharliePassword123!", "otp_code": fresh_otp})
    assert good_login.status_code == 200
    assert "access_token" in good_login.json()

    # 6. Disable MFA
    current_otp = pyotp.TOTP(secret).now()
    disable_resp = client.post("/auth/mfa/disable", json={"otp_code": current_otp}, headers=headers)
    assert disable_resp.status_code == 200
    assert disable_resp.json()["mfa_enabled"] is False

    # Normal login now works without OTP again
    login_after_disable = client.post("/auth/login", json={"username": "charlie", "password": "CharliePassword123!"})
    assert login_after_disable.status_code == 200
