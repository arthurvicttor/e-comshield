
from functools import lru_cache
from pathlib import Path

import joblib
import numpy as np


# Caminho absoluto do modelo dentro do backend
MODEL_PATH = (
    Path(__file__).resolve().parents[1]
    / "models_ml"
    / "intent-v1.joblib"
)

MODEL_VERSION = "svm_linear"


class ModelUnavailableError(Exception):
    """Erro quando o modelo não pode ser utilizado."""
    pass


@lru_cache(maxsize=1)
def load_classifier():
    """Carrega o pipeline treinado e mantém em memória."""

    if not MODEL_PATH.is_file():
        raise ModelUnavailableError(
            "Arquivo do modelo não encontrado."
        )

    try:
        pipeline = joblib.load(MODEL_PATH)

        if not hasattr(pipeline, "predict_proba"):
            raise ValueError(
                "O modelo não suporta predict_proba."
            )

        return pipeline

    except Exception as exc:
        raise ModelUnavailableError(
            "Falha ao carregar o modelo."
        ) from exc


def predict_intent(text: str) -> dict:
    """Classifica uma mensagem e retorna a intenção prevista."""

    pipeline = load_classifier()

    try:
        probabilities = pipeline.predict_proba([text])[0]

        best_index = int(np.argmax(probabilities))

        return {
            "intent": str(pipeline.classes_[best_index]),
            "confidence": float(probabilities[best_index]),
            "model_version": MODEL_VERSION,
        }

    except Exception as exc:
        raise ModelUnavailableError(
            "Falha ao executar a classificação."
        ) from exc
