from fastapi import APIRouter, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.security.jwt import create_access_token
from app.security.password import verify_password

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

fake_user = {
    "username": "admin",
    "hashed_password": "$2b$12$example"
}