from datetime import datetime, timedelta, timezone
import pytest
from app.models.user import User
from app.models.mfa import MFAChallenge
from app.services.email_service import EmailService, EmailDeliveryError


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
    assert data["mfa_enabled"] is True

    # Verify password is never stored in plaintext
    user = db.query(User).filter(User.username == "alice").first()
    assert user is not None
    assert user.hashed_password != payload["password"]
    assert user.hashed_password.startswith("$2b$") or user.hashed_password.startswith("$2a$")

    # Duplicate username/email conflict
    resp_dup = client.post("/auth/register", json=payload)
    assert resp_dup.status_code == 409


def test_mfa_challenge_creation_and_no_premature_jwt(client, monkeypatch):
    """1. Valid email/password creates MFA challenge. 2. Final JWT is NOT issued before OTP verification."""
    sent_emails = []
    monkeypatch.setattr(
        EmailService,
        "send_otp_email",
        lambda to_email, otp: sent_emails.append((to_email, otp)) or True,
    )

    reg = {"username": "bob", "email": "bob@defense.corp", "password": "Password123!"}
    client.post("/auth/register", json=reg)

    login_resp = client.post("/auth/login", json={"username": "bob", "password": "Password123!"})
    assert login_resp.status_code == 200
    data = login_resp.json()

    # Verify MFA challenge created
    assert data["mfa_required"] is True
    assert "challenge_id" in data
    assert len(data["challenge_id"]) > 10
    assert "expires_in_seconds" in data
    assert "email_masked" in data

    # 2. Verify final JWT is NOT issued yet
    assert "access_token" not in data
    assert "token" not in data

    # 13. Verify OTP is never exposed in API response
    assert "otp" not in data
    assert "otp_code" not in data


def test_otp_sent_through_mocked_smtp(client, monkeypatch):
    """3. OTP is sent through mocked SMTP."""
    sent_emails = []
    monkeypatch.setattr(
        EmailService,
        "send_otp_email",
        lambda to_email, otp: sent_emails.append((to_email, otp)) or True,
    )

    reg = {"username": "carol", "email": "carol@defense.corp", "password": "Password123!"}
    client.post("/auth/register", json=reg)

    login_resp = client.post("/auth/login", json={"email": "carol@defense.corp", "password": "Password123!"})
    assert login_resp.status_code == 200
    assert len(sent_emails) == 1
    to_email, otp = sent_emails[0]
    assert to_email == "carol@defense.corp"
    assert len(otp) == 6
    assert otp.isdigit()


def test_correct_otp_verifies_successfully_and_me_works(client, monkeypatch):
    """4. Correct OTP verifies successfully. 15. Existing /auth/me behavior still works after successful MFA."""
    sent_emails = []
    monkeypatch.setattr(
        EmailService,
        "send_otp_email",
        lambda to_email, otp: sent_emails.append((to_email, otp)) or True,
    )

    reg = {"username": "david", "email": "david@defense.corp", "password": "Password123!"}
    client.post("/auth/register", json=reg)

    login_resp = client.post("/auth/login", json={"username": "david", "password": "Password123!"})
    challenge_id = login_resp.json()["challenge_id"]
    otp = sent_emails[0][1]

    verify_resp = client.post("/auth/mfa/verify", json={"challenge_id": challenge_id, "otp": otp})
    assert verify_resp.status_code == 200
    token_data = verify_resp.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"
    assert token_data["user"]["username"] == "david"
    token = token_data["access_token"]

    # 15. Verify /auth/me
    headers = {"Authorization": f"Bearer {token}"}
    me_resp = client.get("/auth/me", headers=headers)
    assert me_resp.status_code == 200
    assert me_resp.json()["username"] == "david"


def test_incorrect_otp_increments_attempts(client, monkeypatch):
    """5. Incorrect OTP increments attempts."""
    monkeypatch.setattr(EmailService, "send_otp_email", lambda to_email, otp: True)

    reg = {"username": "eve", "email": "eve@defense.corp", "password": "Password123!"}
    client.post("/auth/register", json=reg)

    login_resp = client.post("/auth/login", json={"username": "eve", "password": "Password123!"})
    challenge_id = login_resp.json()["challenge_id"]

    bad_verify = client.post("/auth/mfa/verify", json={"challenge_id": challenge_id, "otp": "000000"})
    assert bad_verify.status_code == 401
    assert "Invalid verification code" in bad_verify.json()["detail"]
    assert "4 attempt(s) remaining" in bad_verify.json()["detail"]


def test_fifth_failed_attempt_locks_challenge(client, monkeypatch):
    """6. Fifth failed attempt locks/rejects the challenge."""
    monkeypatch.setattr(EmailService, "send_otp_email", lambda to_email, otp: True)

    reg = {"username": "frank", "email": "frank@defense.corp", "password": "Password123!"}
    client.post("/auth/register", json=reg)

    login_resp = client.post("/auth/login", json={"username": "frank", "password": "Password123!"})
    challenge_id = login_resp.json()["challenge_id"]

    # First 4 attempts -> 401
    for i in range(4):
        resp = client.post("/auth/mfa/verify", json={"challenge_id": challenge_id, "otp": "999999"})
        assert resp.status_code == 401

    # 5th attempt -> 403 Forbidden (locked)
    fifth_resp = client.post("/auth/mfa/verify", json={"challenge_id": challenge_id, "otp": "999999"})
    assert fifth_resp.status_code == 403
    assert "Maximum verification attempts exceeded" in fifth_resp.json()["detail"]

    # Subsequent attempt still 403
    locked_resp = client.post("/auth/mfa/verify", json={"challenge_id": challenge_id, "otp": "999999"})
    assert locked_resp.status_code == 403


def test_expired_otp_is_rejected(client, db, monkeypatch):
    """7. Expired OTP is rejected."""
    sent_emails = []
    monkeypatch.setattr(
        EmailService,
        "send_otp_email",
        lambda to_email, otp: sent_emails.append((to_email, otp)) or True,
    )

    reg = {"username": "grace", "email": "grace@defense.corp", "password": "Password123!"}
    client.post("/auth/register", json=reg)

    login_resp = client.post("/auth/login", json={"username": "grace", "password": "Password123!"})
    challenge_id = login_resp.json()["challenge_id"]
    otp = sent_emails[0][1]

    # Manually expire the challenge in database
    challenge = db.query(MFAChallenge).filter(MFAChallenge.challenge_id == challenge_id).first()
    challenge.expires_at = datetime.now(timezone.utc) - timedelta(minutes=1)
    db.commit()

    exp_resp = client.post("/auth/mfa/verify", json={"challenge_id": challenge_id, "otp": otp})
    assert exp_resp.status_code == 400
    assert "expired" in exp_resp.json()["detail"].lower()


def test_used_otp_cannot_be_reused(client, monkeypatch):
    """8. Used OTP cannot be reused."""
    sent_emails = []
    monkeypatch.setattr(
        EmailService,
        "send_otp_email",
        lambda to_email, otp: sent_emails.append((to_email, otp)) or True,
    )

    reg = {"username": "heidi", "email": "heidi@defense.corp", "password": "Password123!"}
    client.post("/auth/register", json=reg)

    login_resp = client.post("/auth/login", json={"username": "heidi", "password": "Password123!"})
    challenge_id = login_resp.json()["challenge_id"]
    otp = sent_emails[0][1]

    # First verification succeeds
    ok_resp = client.post("/auth/mfa/verify", json={"challenge_id": challenge_id, "otp": otp})
    assert ok_resp.status_code == 200

    # Replay attempt fails
    reuse_resp = client.post("/auth/mfa/verify", json={"challenge_id": challenge_id, "otp": otp})
    assert reuse_resp.status_code == 400
    assert "already been used" in reuse_resp.json()["detail"]


def test_resend_generates_new_otp_and_invalidates_old(client, monkeypatch, db):
    """9. Resend generates a new OTP. 10. Old OTP becomes invalid after resend. 11. Resend cooldown is enforced."""
    sent_emails = []
    monkeypatch.setattr(
        EmailService,
        "send_otp_email",
        lambda to_email, otp: sent_emails.append((to_email, otp)) or True,
    )

    reg = {"username": "ivan", "email": "ivan@defense.corp", "password": "Password123!"}
    client.post("/auth/register", json=reg)

    login_resp = client.post("/auth/login", json={"username": "ivan", "password": "Password123!"})
    challenge_id = login_resp.json()["challenge_id"]
    first_otp = sent_emails[0][1]

    # 11. Immediate resend violates 60-second cooldown -> 429
    early_resend = client.post("/auth/mfa/resend", json={"challenge_id": challenge_id})
    assert early_resend.status_code == 429
    assert "wait" in early_resend.json()["detail"].lower()

    # Fast-forward last_sent_at past cooldown
    challenge = db.query(MFAChallenge).filter(MFAChallenge.challenge_id == challenge_id).first()
    challenge.last_sent_at = datetime.now(timezone.utc) - timedelta(seconds=65)
    db.commit()

    # Resend succeeds
    resend_resp = client.post("/auth/mfa/resend", json={"challenge_id": challenge_id})
    assert resend_resp.status_code == 200
    assert len(sent_emails) == 2
    second_otp = sent_emails[1][1]

    # 10. Verify old OTP is now invalid
    old_verify = client.post("/auth/mfa/verify", json={"challenge_id": challenge_id, "otp": first_otp})
    assert old_verify.status_code == 401

    # Verify new OTP succeeds
    new_verify = client.post("/auth/mfa/verify", json={"challenge_id": challenge_id, "otp": second_otp})
    assert new_verify.status_code == 200
    assert "access_token" in new_verify.json()


def test_smtp_failure_handled_safely(client, monkeypatch):
    """12. SMTP failure is handled safely without leaking credentials."""
    def failing_send(to_email, otp):
        raise EmailDeliveryError("SMTP connection timed out")

    monkeypatch.setattr(EmailService, "send_otp_email", failing_send)

    reg = {"username": "judy", "email": "judy@defense.corp", "password": "Password123!"}
    client.post("/auth/register", json=reg)

    login_resp = client.post("/auth/login", json={"username": "judy", "password": "Password123!"})
    assert login_resp.status_code == 502
    # Verify no credential leakage in error detail
    detail = login_resp.json()["detail"]
    assert "password" not in detail.lower()
    assert "secret" not in detail.lower()
    assert "smtp.gmail.com" not in detail.lower()
