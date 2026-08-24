

from fastapi import APIRouter, Depends
from app.security.dependencies import get_current_user


router = APIRouter(
    prefix="/predict",
    tags=["Prediction"],
)

@router.post("")
async def predict(
    current_user: str = Depends(get_current_user),
):
     return {
        "message": "Prediction endpoint",
        "user": current_user,
        "prediction": "placeholder",
    }