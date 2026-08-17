import pytest


# ── Register ────────────────────────────────────────────────────────────────

async def test_register_business(client):
    response = await client.post("/auth/register/business", json={
        "name": "Acme Corp",
        "email": "acme@test.com",
        "password": "secret123",
        "location": "New York",
        "working_hours": "9-5",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["role"] == "business"
    assert data["name"] == "Acme Corp"
    assert "access_token" in data


async def test_register_worker(client):
    response = await client.post("/auth/register/worker", json={
        "name": "John Smith",
        "email": "john@test.com",
        "password": "secret123",
        "location": "Brooklyn",
        "profession": "Chef",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["role"] == "worker"
    assert data["name"] == "John Smith"
    assert "access_token" in data


async def test_register_duplicate_email(client):
    payload = {
        "name": "Acme Corp",
        "email": "duplicate@test.com",
        "password": "secret123",
    }
    await client.post("/auth/register/business", json=payload)
    response = await client.post("/auth/register/business", json=payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"


# ── Login ────────────────────────────────────────────────────────────────────

async def test_login_success(client):
    await client.post("/auth/register/business", json={
        "name": "Acme Corp",
        "email": "acme@test.com",
        "password": "secret123",
    })
    response = await client.post("/auth/login", json={
        "email": "acme@test.com",
        "password": "secret123",
        "role": "business",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["role"] == "business"
    assert "access_token" in data


async def test_login_wrong_password(client):
    await client.post("/auth/register/business", json={
        "name": "Acme Corp",
        "email": "acme@test.com",
        "password": "secret123",
    })
    response = await client.post("/auth/login", json={
        "email": "acme@test.com",
        "password": "wrongpassword",
        "role": "business",
    })
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"


# ── Logout + Blacklist ───────────────────────────────────────────────────────

async def test_logout_blacklists_token(client):
    # step 1 — register and grab token
    register = await client.post("/auth/register/business", json={
        "name": "Acme Corp",
        "email": "acme@test.com",
        "password": "secret123",
    })
    token = register.json()["access_token"]

    # step 2 — logout with that token
    logout = await client.post(
        "/auth/logout",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert logout.status_code == 200

    # step 3 — try to use the same token again, should be rejected
    response = await client.get(
        "/shifts/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Token has been revoked"


# ── Rate Limiting ────────────────────────────────────────────────────────────

async def test_rate_limit_login(client):
    await client.post("/auth/register/business", json={
        "name": "Acme Corp",
        "email": "acme@test.com",
        "password": "secret123",
    })

    # fire 5 failed attempts
    for _ in range(5):
        await client.post("/auth/login", json={
            "email": "acme@test.com",
            "password": "wrongpassword",
            "role": "business",
        })

    # 6th attempt should be blocked regardless of password
    response = await client.post("/auth/login", json={
        "email": "acme@test.com",
        "password": "secret123",
        "role": "business",
    })
    assert response.status_code == 429
    assert response.json()["detail"] == "Too many login attempts. Try again in 60 seconds."