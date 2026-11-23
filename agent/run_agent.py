
"""Agente E-ComShield com OpenAI Agents SDK e Google Gemini.

Utiliza o endpoint /classify do backend FastAPI, protegido por JWT,
para classificar intenções de mensagens de clientes.
"""

from __future__ import annotations

from agents import ModelSettings

import asyncio
import os
import sys

import httpx
from agents import (
    Agent,
    AsyncOpenAI,
    OpenAIChatCompletionsModel,
    Runner,
    function_tool,
    set_tracing_disabled,
)

CLASSIFY_API_BASE = os.environ.get(
    "CLASSIFY_API_BASE", "http://127.0.0.1:8000"
).rstrip("/")

GEMINI_MODEL = os.environ.get(
    "GEMINI_MODEL",
    "gemini-3.5-flash-lite",
)

SYSTEM_PROMPT = """
Você é o assistente de atendimento ao cliente da E-ComShield.

Para cada nova mensagem do cliente, chame a ferramenta
`classificar_intencao` antes de responder.

Use a intenção e a confiança retornadas para orientar sua resposta.

Se a intenção for `human_agent`, informe que encaminhará o
atendimento para uma pessoa.

Responda de forma objetiva e educada, confirmando a solicitação
e pedindo informações adicionais somente quando necessário.

Nunca invente status de pedidos, valores ou prazos.
Você não possui acesso direto ao banco de pedidos.

Responda sempre em inglês, pois o classificador foi treinado
com mensagens em inglês.

Mantenha suas respostas entre duas e quatro frases.
"""

set_tracing_disabled(disabled=True)


def obter_token() -> str:
    resposta = httpx.post(
        f"{CLASSIFY_API_BASE}/auth/token",
        data={
            "username": os.environ["ECOMSHIELD_USERNAME"],
            "password": os.environ["ECOMSHIELD_PASSWORD"],
        },
        timeout=15,
    )
    resposta.raise_for_status()
    return resposta.json()["access_token"]


_token: str | None = None


@function_tool
def classificar_intencao(texto_do_cliente: str) -> str:
    """Classifica a intenção de uma mensagem usando a API E-ComShield.

    Args:
        texto_do_cliente: Mensagem original enviada pelo cliente.
    """
    global _token

    if _token is None:
        try:
            _token = obter_token()
            print("[AUTH] JWT obtido com sucesso")
        except Exception as exc:
            print(f"[ERRO AUTH] {type(exc).__name__}: {exc}")
            raise

    try:
        resposta = httpx.post(
            f"{CLASSIFY_API_BASE}/classify",
            headers={"Authorization": f"Bearer {_token}"},
            json={"text": texto_do_cliente},
            timeout=httpx.Timeout(60.0, connect=10.0),
        )
        print(f"[CLASSIFY] HTTP {resposta.status_code}")
    except Exception as exc:
        print(f"[ERRO CLASSIFY] {type(exc).__name__}: {exc}")
        raise

    if resposta.status_code == 401:
        _token = obter_token()
        resposta = httpx.post(
            f"{CLASSIFY_API_BASE}/classify",
            headers={"Authorization": f"Bearer {_token}"},
            json={"text": texto_do_cliente},
            timeout=10,
        )

    resposta.raise_for_status()
    dados = resposta.json()

    intent = dados["intent"]
    confidence = float(dados["confidence"])
    model_version = dados.get("model_version", "nao_informada")

    print(
        f"[CLASSIFY] HTTP {resposta.status_code} | "
        f"intent={intent} | confidence={confidence:.4f} | "
        f"model={model_version}"
    )

    return (
        f"intent={intent} confidence={confidence} "
        f"model_version={model_version}"
    )


gemini_client = AsyncOpenAI(
    api_key=os.environ.get("GEMINI_API_KEY") or "NOT_CONFIGURED",
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

atendente = Agent(
    name="Atendente E-ComShield",
    instructions=SYSTEM_PROMPT,
    tools=[classificar_intencao],
    model=OpenAIChatCompletionsModel(
        model=GEMINI_MODEL,
        openai_client=gemini_client,
    ),
    model_settings=ModelSettings(
        tool_choice="required",
    ),
)

CONVERSA_DEMO = [
    "Hi, my order hasn't arrived yet, where is it?",
    "Actually this product arrived damaged, I want my money back.",
    "yes that's right",
]


async def rodar_demo() -> str:
    linhas = ["# Demonstração do agente — 3 turnos\n"]
    historico = None

    for turno, mensagem in enumerate(CONVERSA_DEMO, start=1):
        entrada = (
            mensagem
            if historico is None
            else historico.to_input_list()
            + [{"role": "user", "content": mensagem}]
        )

        resultado = await Runner.run(atendente, entrada)
        historico = resultado

        print(f"\n[DEBUG] Turno {turno}")
        print("Tool choice:", atendente.model_settings.tool_choice)

        for item in resultado.new_items:
            print("Item:", item.type)

            if item.type == "tool_call_item":
                print("Ferramenta solicitada pelo modelo")

            elif item.type == "tool_call_output_item":
                print("Resultado da ferramenta:", str(item.output)[:200])

        linhas.extend([
            f"## Turno {turno}\n",
            f"**Cliente:** {mensagem}\n",
            f"**Agente:** {resultado.final_output}\n",
        ])

    texto = "\n".join(linhas)
    print(texto)
    return texto


if __name__ == "__main__":
    variaveis = [
        "GEMINI_API_KEY",
        "ECOMSHIELD_USERNAME",
        "ECOMSHIELD_PASSWORD",
    ]

    ausentes = [nome for nome in variaveis if not os.environ.get(nome)]

    if ausentes:
        print(
            f"Variáveis não configuradas: {', '.join(ausentes)}",
            file=sys.stderr,
        )
        sys.exit(1)

    transcricao = asyncio.run(rodar_demo())

    with open("conversa_demo.md", "w", encoding="utf-8") as arquivo:
        arquivo.write(transcricao)

    print("\nTranscrição salva em conversa_demo.md")
