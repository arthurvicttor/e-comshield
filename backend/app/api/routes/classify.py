
from fastapi import APIRouter, Depends, HTTPException

from app.schemas.classify import (
    ClassifyRequest,
    ClassifyResponse,
)
from app.security.dependencies import get_current_user
from app.services.classifier import (
    ModelUnavailableError,
    predict_intent,
)


router = APIRouter(
    prefix="/classify",
    tags=["Classification"],
)


@router.post(
    "",
    response_model=ClassifyResponse,
    summary="Classificar intenção do cliente",
    description=(
        "Recebe um texto de atendimento e retorna "
        "a intenção prevista e sua probabilidade. "
        "Requer autenticação JWT."
    ),
    responses={
        401: {
            "description": "Token ausente, inválido ou expirado"
        },
        422: {
            "description": "Dados de entrada inválidos"
        },
        503: {
            "description": "Modelo indisponível"
        },
    },
)
async def classify(
    request: ClassifyRequest,
    current_user: str = Depends(get_current_user),
):
    try:
        return predict_intent(request.text)

    except ModelUnavailableError:
        raise HTTPException(
            status_code=503,
            detail="Serviço de classificação indisponível.",
        )
