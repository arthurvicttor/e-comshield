"""Agente de atendimento do E-ComShield (TP4), construído com o OpenAI Agents SDK.

O agente recebe mensagens de um cliente e usa a ferramenta `classificar_intencao` para chamar o
endpoint `POST /classify` (servido por `demo_classify_server.py` nesta etapa — ver o docstring
daquele arquivo para a diferença entre esta demonstração e a API de produção em `backend/`).

O SDK é da OpenAI, mas o modelo usado nesta demonstração é servido pela **Groq** (gratuito, sem
cartão, compatível com a API da OpenAI), para não depender de uma chave paga. Basta trocar
`GROQ_API_KEY`/`GROQ_MODEL` por `OPENAI_API_KEY`/um modelo da OpenAI caso se prefira usá-la
diretamente — o resto do código (Agent, function_tool, Runner) não muda.

Pré-requisitos para rodar:
    1. Treinar o modelo: executar `04_classificador_intencao.ipynb` (gera `models/intent_classifier.joblib`).
    2. Subir o servidor de demonstração: `python -m uvicorn demo_classify_server:app --port 8001`
       (em outro terminal, dentro de `agent/`).
    3. Definir a variável de ambiente `GROQ_API_KEY` com uma chave grátis de https://console.groq.com/keys.
    4. `python run_agent.py`

O resultado (os 3+ turnos de conversa) é impresso no terminal e também salvo em
`conversa_demo.md`, usado como evidência no log do TP4.
"""

from __future__ import annotations

import asyncio
import os
import sys

import httpx
from agents import Agent, AsyncOpenAI, OpenAIChatCompletionsModel, Runner, function_tool

CLASSIFY_API_BASE = os.environ.get("CLASSIFY_API_BASE", "http://127.0.0.1:8001")
GROQ_MODEL = os.environ.get("GROQ_MODEL", "openai/gpt-oss-120b")

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

def _obter_token_demo() -> str:
    username = os.environ["ECOMSHIELD_USERNAME"]
    password = os.environ["ECOMSHIELD_PASSWORD"]

    resposta = httpx.post(
        f"{CLASSIFY_API_BASE}/auth/token",
        data={
            "username": username,
            "password": password,
        },
        timeout=15,
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

    try:
        if _TOKEN is None:
            _TOKEN = _obter_token_demo()

    except Exception as exc:
        print(
            f"[ERRO AUTH] {type(exc).__name__}: {exc}"
        )
        raise


    resposta = httpx.post(
        f"{CLASSIFY_API_BASE}/classify",
        headers={"Authorization": f"Bearer {_TOKEN}"},
        json={"text": texto_do_cliente},
        timeout=10,
    )
    print(
    f"[CLASSIFY] HTTP {resposta.status_code} | "
    f"Resposta: {resposta.text[:300]}"
    )
    if resposta.status_code == 401:
        # token expirado/ inválido: busca um novo e tenta de novo, uma única vez
        _TOKEN = _obter_token_demo()
        resposta = httpx.post(
            f"{CLASSIFY_API_BASE}/classify",
            headers={"Authorization": f"Bearer {_TOKEN}"},
            json={"text": texto_do_cliente},
            timeout=10,
        )
    resposta.raise_for_status()
    dados = resposta.json()
    print(
            f"[CLASSIFY] HTTP {resposta.status_code} | "
            f"intent={dados['intent']} | "
            f"confidence={dados['confidence']:.4f} | "
            f"model={dados['model_version']}"
        )
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
