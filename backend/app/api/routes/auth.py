from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.security.jwt import create_access_token
from app.security.password import verify_password

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)

fake_user = {
    "username": "admin",
    "hashed_password": "$2b$12$tO21q5wD3YQCNuY/Xbm/XucRN47IebTaEfesjMFkpeOUFrtvAaPce",
}

@router.post("/token")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    if form_data.username != fake_user["username"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    if not verify_password(
        form_data.password,
        fake_user["hashed_password"],
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    access_token = create_access_token(
        data={"sub": fake_user["username"]}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
     }