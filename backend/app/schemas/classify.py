
from pydantic import BaseModel, ConfigDict, Field


class ClassifyRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    text: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Texto de atendimento a ser classificado",
        examples=["Where is my order?"],
    )

class ClassifyResponse(BaseModel):
    intent: str = Field(
        description="Intenção prevista pelo classificador",
        examples=["track_order"],
    )

    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Probabilidade da intenção prevista",
        examples=[0.98],
    )

    model_version: str = Field(
        description="Versão do modelo utilizado",
        examples=["svm_linear"],
    )

