"""Servidor de demonstração do classificador de intenção (TP4).

Este arquivo NÃO é a API de produção do E-ComShield (essa fica em `backend/`, com Postgres,
usuários reais e as rotas `/auth/token`, `/predict`, `/orders/{id}` do Integrante B). Ele existe
só para eu poder demonstrar o agente de ponta a ponta nesta etapa, chamando um endpoint
`POST /classify` de verdade, sem depender de o Integrante B já ter integrado o modelo ao backend.

Autenticação: é um JWT próprio, assinado com uma chave só desta demonstração (`DEMO_SECRET_KEY`,
nunca usada em produção), emitido por `POST /demo-token` com qualquer usuário/senha — não há banco
de usuários aqui. Isso é suficiente para exercitar o fluxo "autentica via JWT" pedido no TP4, sem
reimplementar nem tocar no sistema de autenticação real do backend.

Contrato de `/classify` (alinhado com `docs/planejamento-t2.md`, seção 5, mas com o nome de rota e
o payload pedidos no enunciado do TP4):

    POST /classify
    Authorization: Bearer <token>
    { "text": "I cannot pay, notify of payment problems" }

    200 OK
    { "intent": "payment_issue", "confidence": 0.98, "model_version": "svm_linear" }

Como rodar:

    cd agent
    python -m uvicorn demo_classify_server:app --port 8001

O caminho do modelo é lido de `models/intent_classifier.joblib` e `models/intent_classifier_metadata.json`,
gerados pelo notebook `04_classificador_intencao.ipynb`.
"""

from __future__ import annotations

import json
import pathlib
from datetime import datetime, timedelta, timezone

import joblib
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pydantic import BaseModel, ConfigDict, Field

DEMO_SECRET_KEY = "demo-only-nao-usar-em-producao-tp4"  # noqa: S105 — chave só desta demonstração
ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 30
CONFIDENCE_LIMIAR_HUMANO = 0.30  # abaixo disso, melhor escalar para um humano do que confiar na previsão

MODELS_DIR = pathlib.Path(__file__).resolve().parent / "models"

app = FastAPI(
    title="E-ComShield — Demo do classificador de intenção (TP4)",
    description="Servidor local de demonstração, não é a API de produção. Ver docstring do módulo.",
)
bearer_scheme = HTTPBearer()


@app.on_event("startup")
def carregar_modelo() -> None:
    pipeline_path = MODELS_DIR / "intent_classifier.joblib"
    metadata_path = MODELS_DIR / "intent_classifier_metadata.json"
    if not pipeline_path.exists():
        raise RuntimeError(
            f"Modelo não encontrado em {pipeline_path}. Rode o notebook "
            "04_classificador_intencao.ipynb primeiro."
        )
    app.state.pipeline = joblib.load(pipeline_path)
    app.state.metadata = json.loads(metadata_path.read_text(encoding="utf-8"))


class DemoTokenRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    username: str = Field(..., min_length=1, max_length=50)


class DemoTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ClassifyRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    text: str = Field(..., min_length=1, max_length=1000, description="Mensagem do cliente")


class ClassifyResponse(BaseModel):
    intent: str
    confidence: float
    model_version: str


def _criar_token(username: str) -> str:
    expira = datetime.now(timezone.utc) + timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    return jwt.encode({"sub": username, "exp": expira}, DEMO_SECRET_KEY, algorithm=ALGORITHM)


def exigir_usuario_autenticado(
    credenciais: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> str:
    try:
        payload = jwt.decode(credenciais.credentials, DEMO_SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    username = payload.get("sub")
    if not username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")
    return username


@app.post("/demo-token", response_model=DemoTokenResponse)
async def emitir_token_demo(body: DemoTokenRequest) -> DemoTokenResponse:
    """Emite um JWT de demonstração para qualquer `username`. Não há senha nem banco de usuários:
    isso só existe para o agente ter um token Bearer para chamar `/classify`, como pede o TP4."""
    return DemoTokenResponse(access_token=_criar_token(body.username))


@app.post("/classify", response_model=ClassifyResponse)
async def classificar(
    body: ClassifyRequest,
    usuario: str = Depends(exigir_usuario_autenticado),
) -> ClassifyResponse:
    pipeline = app.state.pipeline
    metadata = app.state.metadata

    probas = pipeline.predict_proba([body.text])[0]
    classes = pipeline.classes_
    idx = probas.argmax()
    intent, confidence = classes[idx], float(probas[idx])

    if confidence < CONFIDENCE_LIMIAR_HUMANO:
        intent = "human_agent"

    # Logging seguro (planejamento-t2.md, seção 5): nunca o texto completo, só metadados.
    print(f"[/classify] usuario={usuario} len_texto={len(body.text)} intent={intent} confidence={confidence:.3f}")

    return ClassifyResponse(intent=intent, confidence=round(confidence, 4), model_version=metadata["modelo"])


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "modelo_carregado": hasattr(app.state, "pipeline")}
