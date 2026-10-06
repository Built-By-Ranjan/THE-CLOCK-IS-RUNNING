def test_login_returns_access_token(client, auth_headers):
    response = client.post(
        "/auth/login",
        json={"email": "test@example.com", "password": "password"},
    )

    assert response.status_code == 200
    assert response.json()["access_token"]


def test_login_with_wrong_password_returns_401(client, auth_headers):
    response = client.post(
        "/auth/login",
        json={"email": "test@example.com", "password": "wrong"},
    )

    assert response.status_code == 401


def test_login_with_unknown_email_returns_401(client):
    response = client.post(
        "/auth/login",
        json={"email": "unknown@example.com", "password": "password"},
    )

    assert response.status_code == 401


def test_protected_route_requires_token(client):
    response = client.get("/incidents")

    assert response.status_code == 401
