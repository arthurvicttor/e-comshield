# Contrato Agente ↔ Backend — E-ComShield (v1, baseado no dataset real)

**Projeto de Bloco — Análise e Segurança de Agentes de IA**
Proposta: E-ComShield (Suporte de E-commerce e Reembolsos)
Dataset base: [Bitext Retail eCommerce LLM Chatbot Training Dataset](https://huggingface.co/datasets/bitext/Bitext-retail-ecommerce-llm-chatbot-training-dataset) (CDLA-Sharing-1.0)

Este documento define a interface entre a parte de Dados/IA (agente) e a parte de Backend/API,
para que os dois lados possam ser desenvolvidos em paralelo sem quebrar a integração depois.
Esta versão substitui o rascunho inicial (v0) pelas categorias e intenções reais do dataset escolhido.

---

## 1. O que o agente recebe (input do backend → agente)

```json
{
  "session_id": "string (uuid)",
  "user_id": "string",
  "mensagem": "string (texto do usuário)",
  "historico": [
    { "role": "user | agent", "texto": "string" }
  ]
}
```

- `historico` é opcional na v1 (podemos começar sem memória de conversa e adicionar depois).
- `user_id` é usado só para o backend validar permissões — o agente **não** deve usar isso para
  buscar dados de outro usuário nem repetir esse dado na resposta (evita abrir brecha de IDOR).

## 2. Categorias e intenções que o agente pode identificar

O dataset já vem rotulado com `category` (grupo) e `intent` (intenção específica). Para o escopo do
E-ComShield, vamos focar em 4 categorias — as demais existem no dataset mas ficam fora do classificador
do agente por enquanto (podem virar `outro`/`duvida_geral`).

| Categoria | Intenções |
|---|---|
| `ORDER` | `track_order`, `cancel_order`, `change_order`, `request_invoice` |
| `DELIVERY` | `track_delivery`, `delivery_issue`, `damaged_delivery`, `wrong_item`, `missing_item`, `delivery_time`, `shipping_costs` |
| `RETURNS` | `request_refund`, `refund_status`, `refund_policy`, `return_product`, `return_product_online`, `return_product_in_store`, `return_policy` |
| `PRODUCT` | `product_issue`, `exchange_product`, `exchange_product_in_store` |
| — | `outro` (mensagem fora do escopo das categorias acima) |

Isso muda o campo `intent` da resposta: em vez de um rótulo genérico em português, o agente retorna
`category` + `intent` no formato do dataset (em inglês, snake_case), que é o que o classificador
realmente vai aprender a prever.

## 3. Entidades que o agente extrai da mensagem

- `numero_pedido` (se mencionado)
- `produto` (nome/descrição, se mencionado)
- `motivo` (motivo da troca/reembolso/reclamação, texto livre)
- `sentimento` (`positivo` | `neutro` | `negativo` — inferido a partir do texto; o dataset tem
  marcadores de tom/erro na coluna `tags`, então isso ainda pode ser ajustado depois da EDA)

## 4. Formato de resposta do agente → backend

```json
{
  "category": "RETURNS",
  "intent": "request_refund",
  "confidence": 0.92,
  "entidades": {
    "numero_pedido": "12345",
    "produto": "fone de ouvido bluetooth",
    "motivo": "veio com defeito",
    "sentimento": "negativo"
  },
  "resposta_texto": "string (mensagem já pronta para mostrar ao usuário)",
  "requer_acao_backend": true,
  "acao_sugerida": "iniciar_reembolso | consultar_pedido | escalar_humano | nenhuma"
}
```

- `category` e `intent`: seguem exatamente os valores do dataset (em inglês), para não ter que
  remapear rótulos depois de treinar o classificador.
- `confidence`: score de 0 a 1 da classificação de intenção.
- `requer_acao_backend`: indica se o backend precisa chamar alguma rota/serviço além de exibir a resposta.
- `acao_sugerida`: string fechada (enum) para o backend decidir se aciona alguma ferramenta/endpoint.
- O agente **nunca** deve incluir dados de outro pedido/usuário na resposta — só o que veio no request
  ou o que ele mesmo extraiu da mensagem atual.

## 5. Pontos em aberto para alinhar

1. Confirmar se o backend prefere receber `category`+`intent` separados (como acima) ou um único
   campo combinado (ex.: `"RETURNS.request_refund"`).
2. Definir o mapeamento de `acao_sugerida` por intenção (ex.: `request_refund` → `iniciar_reembolso`,
   `track_order`/`track_delivery` → `consultar_pedido`) — posso levar essa tabela pronta depois da EDA.
3. Definir se `historico` entra já na Parte 1 ou só depois.
4. Definir o threshold de `confidence` que o backend vai considerar "confiável" vs "escalar para humano".
5. Alinhar prazos: TP1 — 26/08/2026, TP2 — 23/09/2026.

---
*Dataset já escolhido e documentado (fonte, licença e justificativa). Depois de validar isso com meu
colega, a ideia é gerar o OpenAPI/Swagger real e criar os repositórios no GitHub.*
