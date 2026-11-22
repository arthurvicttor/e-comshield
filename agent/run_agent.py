"""Agente de atendimento do E-ComShield (TP4), construído com o OpenAI Agents SDK.

O agente recebe mensagens de um cliente e usa a ferramenta `classificar_intencao` para chamar o
endpoint `POST /classify` da API **de produção** (`backend/app/api/routes/classify.py`, integrada
pelo Integrante B), autenticando de verdade via `POST /auth/token`. O servidor de demonstração
(`demo_classify_server.py`) foi usado só enquanto esse endpoint ainda não existia; ele continua no
repositório como referência, mas o agente já aponta para a API real por padrão.

O SDK é da OpenAI, mas o modelo usado nesta demonstração é servido pela **Groq** (gratuito, sem
cartão, compatível com a API da OpenAI), para não depender de uma chave paga. Basta trocar
`GROQ_API_KEY`/`GROQ_MODEL` por `OPENAI_API_KEY`/um modelo da OpenAI caso se prefira usá-la
diretamente — o resto do código (Agent, function_tool, Runner) não muda.

Pré-requisitos para rodar:
    1. Ter o modelo treinado e commitado em `backend/app/models_ml/intent-v1.joblib` (gerado por
       `04_classificador_intencao.ipynb`).
    2. Subir a API real, dentro de `backend/`: `uvicorn app.main:app --port 8000` (com `.env`
       configurado e as migrations do Alembic já aplicadas — ver `backend/README.md`).
    3. Ter um usuário de teste no banco (ex.: `user1` / `user123`, criado por
       `python -m app.db.seed_test` em CI, ou qualquer usuário seu).
    4. Definir `GROQ_API_KEY` (grátis em https://console.groq.com/keys) e, se o usuário de teste
       não for `user1`/`user123`, também `ECOMSHIELD_USERNAME`/`ECOMSHIELD_PASSWORD`.
    5. `python run_agent.py`

O resultado (os 3+ turnos de conversa) é impresso no terminal e também salvo em
`conversa_demo.md`, usado como evidência no log do TP4.
"""

from __future__ import annotations

import asyncio
import os
import sys

import httpx
from agents import Agent, AsyncOpenAI, OpenAIChatCompletionsModel, Runner, function_tool

# Aponta, por padrão, para a API real (backend/), não mais para o servidor de demonstração.
CLASSIFY_API_BASE = os.environ.get("CLASSIFY_API_BASE", "http://127.0.0.1:8000")
GROQ_MODEL = os.environ.get("GROQ_MODEL", "openai/gpt-oss-120b")

# Credenciais de um usuário de teste já existente no banco da API (nunca uma conta real).
ECOMSHIELD_USERNAME = os.environ.get("ECOMSHIELD_USERNAME", "user1")
ECOMSHIELD_PASSWORD = os.environ.get("ECOMSHIELD_PASSWORD", "user123")

SYSTEM_PROMPT = """\
Você é o assistente de atendimento ao cliente da E-ComShield, uma loja de e-commerce.

Para CADA mensagem nova do cliente que descreva um pedido, problema ou dúvida, chame a ferramenta
`classificar_intencao` passando o texto do cliente, antes de responder. Use a intenção e a
confiança devolvidas para guiar sua resposta:

- Se a intenção for `human_agent` (a ferramenta devolve isso quando a confiança do classificador
  é baixa), diga que vai transferir para um atendente humano e não tente adivinhar a intenção.
- Para as demais intenções, responda de forma objetiva e educada, confirmando o que entendeu
  antes de pedir mais informações (por exemplo, número do pedido) quando precisar.
- Nunca invente status de pedido, valores ou prazos — você não tem acesso ao sistema de pedidos
  nesta etapa, só à intenção do cliente. Se precisar de um dado que não tem, diga isso e peça ao
  cliente ou diga que vai encaminhar.
- Responda sempre em inglês, porque o classificador de intenção foi treinado só com mensagens em
  inglês (dataset Bitext) e não reconhece bem outros idiomas — ver limitação documentada em
  `04_classificador_intencao.ipynb`.
- Seja breve: 2 a 4 frases por resposta.
"""


def _obter_token() -> str:
    """Autentica no endpoint real da API (`POST /auth/token`, formulário OAuth2 — não JSON)."""
    resposta = httpx.post(
        f"{CLASSIFY_API_BASE}/auth/token",
        data={"username": ECOMSHIELD_USERNAME, "password": ECOMSHIELD_PASSWORD},
    )
    resposta.raise_for_status()
    return resposta.json()["access_token"]


_TOKEN = None


@function_tool
def classificar_intencao(texto_do_cliente: str) -> str:
    """Classifica a intenção de uma mensagem de atendimento ao cliente, chamando o endpoint
    POST /classify da API do E-ComShield.

    Args:
        texto_do_cliente: a mensagem do cliente, no idioma original, sem alterações.

    Returns:
        Uma string com a intenção prevista, a confiança do modelo e a versão do modelo, por
        exemplo: "intent=track_order confidence=0.91 model_version=svm_linear".
    """
    global _TOKEN
    if _TOKEN is None:
        _TOKEN = _obter_token()

    resposta = httpx.post(
        f"{CLASSIFY_API_BASE}/classify",
        headers={"Authorization": f"Bearer {_TOKEN}"},
        json={"text": texto_do_cliente},
        timeout=10,
    )
    if resposta.status_code == 401:
        # token expirado/ inválido: busca um novo e tenta de novo, uma única vez
        _TOKEN = _obter_token()
        resposta = httpx.post(
            f"{CLASSIFY_API_BASE}/classify",
            headers={"Authorization": f"Bearer {_TOKEN}"},
            json={"text": texto_do_cliente},
            timeout=10,
        )
    resposta.raise_for_status()
    dados = resposta.json()
    return (
        f"intent={dados['intent']} confidence={dados['confidence']} "
        f"model_version={dados['model_version']}"
    )


_groq_client = AsyncOpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.environ.get("GROQ_API_KEY", ""),
)

atendente = Agent(
    name="Atendente E-ComShield",
    instructions=SYSTEM_PROMPT,
    tools=[classificar_intencao],
    model=OpenAIChatCompletionsModel(model=GROQ_MODEL, openai_client=_groq_client),
)


# Conversa de demonstração com 3 turnos do cliente, em inglês (o classificador foi treinado só
# com o dataset Bitext, em inglês — ver limitação no notebook 04). Cobre: uma intenção clara
# (rastreio), uma segunda intenção clara mas diferente (reembolso por produto danificado) e uma
# mensagem curta/vaga de confirmação, para checar o comportamento de baixa confiança.
CONVERSA_DEMO = [
    "Hi, my order hasn't arrived yet, where is it?",
    "Actually this product arrived damaged, I want my money back.",
    "yes that's right",
]


async def rodar_demo() -> str:
    linhas: list[str] = ["# Demonstração do agente — 3 turnos\n"]
    historico = None
    for turno, mensagem_cliente in enumerate(CONVERSA_DEMO, start=1):
        entrada = mensagem_cliente if historico is None else historico.to_input_list() + [
            {"role": "user", "content": mensagem_cliente}
        ]
        resultado = await Runner.run(atendente, entrada)
        historico = resultado

        linhas.append(f"## Turno {turno}\n")
        linhas.append(f"**Cliente:** {mensagem_cliente}\n")
        linhas.append(f"**Agente:** {resultado.final_output}\n")

    texto = "\n".join(linhas)
    print(texto)
    return texto


if __name__ == "__main__":
    if not os.environ.get("GROQ_API_KEY"):
        print(
            "Defina a variável de ambiente GROQ_API_KEY antes de rodar "
            "(ex.: no PowerShell: $env:GROQ_API_KEY = 'gsk_...'). Chave grátis em "
            "https://console.groq.com/keys.",
            file=sys.stderr,
        )
        sys.exit(1)

    transcricao = asyncio.run(rodar_demo())
    with open("conversa_demo.md", "w", encoding="utf-8") as f:
        f.write(transcricao)
    print("\nTranscrição salva em agent/conversa_demo.md")
