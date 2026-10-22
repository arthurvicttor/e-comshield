
from fastapi import APIRouter, Depends

from app.schemas.predict import PredictRequest, PredictResponse
from app.security.dependencies import get_current_user


router = APIRouter(
    prefix="/predict",
    tags=["Prediction"],
)


@router.post(
    "",
    response_model=PredictResponse,
    summary="Processar mensagem do cliente",
    description=(
        "Recebe uma mensagem de atendimento e retorna "
        "uma resposta provisória. "
        "O classificador de intenções será integrado "
        "em uma etapa posterior. "
        "Requer autenticação JWT."
    ),
    responses={
        401: {"description": "Token ausente, inválido ou expirado"},
        422: {"description": "Dados de entrada inválidos"},
    },
)
async def predict(
    request: PredictRequest,
    current_user: str = Depends(get_current_user),
):
    return {
        "message": request.message,
        "user": current_user,
        "prediction": "placeholder",
    }
