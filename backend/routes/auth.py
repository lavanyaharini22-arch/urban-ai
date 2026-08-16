from fastapi import APIRouter, HTTPException, Header
from schemas.schemas import RegisterRequest, LoginRequest, AuthResponse
from database.db import get_conn
from utils.security import (
    hash_password, verify_password, is_valid_email, is_strong_password,
    create_session, get_session_email, destroy_session,
)

router = APIRouter()


@router.post("/register", response_model=AuthResponse)
def register(payload: RegisterRequest):
    if not is_valid_email(payload.email):
        raise HTTPException(status_code=400, detail="Please enter a valid email address.")

    if payload.password != payload.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match.")

    ok, msg = is_strong_password(payload.password)
    if not ok:
        raise HTTPException(status_code=400, detail=msg)

    with get_conn() as conn:
        existing = conn.execute(
            "SELECT id FROM users WHERE email = ?", (payload.email.lower(),)
        ).fetchone()
        if existing:
            raise HTTPException(status_code=409, detail="An account with this email already exists.")

        conn.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            (payload.name.strip(), payload.email.lower(), hash_password(payload.password)),
        )

    return AuthResponse(success=True, message="Registration successful. Please log in.")


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest):
    with get_conn() as conn:
        user = conn.execute(
            "SELECT * FROM users WHERE email = ?", (payload.email.lower(),)
        ).fetchone()

    if not user or not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    token = create_session(user["email"])
    return AuthResponse(success=True, message="Login successful.", token=token,
                         name=user["name"], email=user["email"])


@router.post("/logout")
def logout(authorization: str = Header(default="")):
    token = authorization.replace("Bearer ", "").strip()
    destroy_session(token)
    return {"success": True, "message": "Logged out."}


def require_auth(authorization: str = Header(default="")):
    token = authorization.replace("Bearer ", "").strip()
    email = get_session_email(token)
    if not email:
        raise HTTPException(status_code=401, detail="Not authenticated. Please log in.")
    return email
