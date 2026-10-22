from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select

from app.api.deps import get_db
from app.models.user import User
from app.security.jwt import create_access_token
from app.security.password import verify_password
from app.core.rate_limit import limiter
from app.schemas.auth import TokenResponse

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)

# Limita a rota de login para 5 solicitações por minuto
@router.post(
    "/token",
    response_model=TokenResponse,
    summary="Autenticar usuário",
    description=(
        "Valida username e password enviados como "
        "formulário OAuth2 e retorna um token JWT. "
        "Limite de 5 requisições por minuto por IP."
    ),
    responses={
        401: {"description": "Credenciais inválidas"},
        429: {"description": "Limite de autenticações excedido"},
        422: {"description": "Formulário inválido"},
    },
)
@limiter.limit("5/minute")
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    statement = select(User).where(
    User.username == form_data.username
)

    user = db.exec(statement).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    if not verify_password(
        form_data.password,
        user.hashed_password,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    access_token = create_access_token(
        data={"sub": user.username}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }