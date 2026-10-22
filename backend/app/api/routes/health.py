
from fastapi import APIRouter

from app.schemas.health import HealthResponse


router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Verificar disponibilidade da API",
    description=(
        "Retorna o status operacional básico da API "
        "E-ComShield. Não exige autenticação."
    ),
)
async def health_check():
    return {"status": "ok"}
