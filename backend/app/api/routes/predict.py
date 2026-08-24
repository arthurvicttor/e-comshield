

from fastapi import APIRouter, Depends

from app.schemas.predict import PredictRequest
from app.security.dependencies import get_current_user


router = APIRouter(
    prefix="/predict",
    tags=["Prediction"],
)

@router.post("")
async def predict(
     request: PredictRequest,
    current_user: str = Depends(get_current_user),
):
     return {
        "message": request.message,
        "user": current_user,
        "prediction": "placeholder",
    }