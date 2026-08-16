"""
Basic smoke tests. Run with:
    pip install pytest httpx
    pytest tests/test_backend.py
"""
import os
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "backend"))

from fastapi.testclient import TestClient
from app import app

client = TestClient(app)


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_register_and_login_flow():
    email = "test_user_smoke@example.com"
    client.post("/register", json={
        "name": "Test User", "email": email,
        "password": "TestPass123", "confirm_password": "TestPass123",
    })
    resp = client.post("/login", json={"email": email, "password": "TestPass123"})
    assert resp.status_code == 200
    assert "token" in resp.json()


def test_login_rejects_bad_password():
    resp = client.post("/login", json={"email": "nobody@example.com", "password": "wrong"})
    assert resp.status_code == 401
