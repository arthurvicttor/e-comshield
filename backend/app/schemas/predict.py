from pydantic import BaseModel, Field

class PredictRequest(BaseModel):
    message: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Mensagem enviada pelo usuário",
    )