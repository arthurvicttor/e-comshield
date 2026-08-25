# DFD — E-ComShield

## Diagrama

```mermaid
---
config:
  layout: elk
---
sequenceDiagram
    participant User as Usuário / Bot
    participant API as API FastAPI
    participant Agent as Agent / IA
    participant Dataset as Dataset (treino/EDA)

    User->>API: POST /auth/token<br/>username + password
    Note over API: TRUST BOUNDARY 1<br/>Autenticação / JWT
    API-->>User: Access Token (JWT)

    User->>API: POST /predict<br/>Bearer Token + mensagem
    API->>API: Validar JWT

    alt Token inválido ou ausente
        API-->>User: 401 Unauthorized
    else Token válido
        Note over Agent,Dataset: TRUST BOUNDARY 2<br/>Integração futura
        API-.->>Agent: Mensagem do usuário (futuro)
        Agent-.->>Dataset: Consulta base de intenções<br/>(classificação treinada no EDA)
        Dataset-.->>Agent: Padrões de intenção/categoria
        Agent-.->>API: Intenção classificada + resposta
        API-->>User: Resposta processada pelo Agent
    end

    User->>API: GET /health
    API-->>User: 200 OK
```

## Análise CIA

| Componente | Confidencialidade | Integridade | Disponibilidade |
|---|---|---|---|
| Usuário / Bot | Credenciais, tokens e mensagens devem ser protegidos | Mensagens não devem ser alteradas durante o transporte | Deve conseguir enviar requisições |
| FastAPI | Tokens e dados recebidos devem ser protegidos | Autenticação e requisições devem ser validadas | API deve permanecer disponível |
| Agent *(integração futura)* | Mensagens e contexto podem conter dados sensíveis | Respostas não devem ser manipuladas | Deve estar disponível para processar solicitações |
| Dataset | Dados de clientes (mesmo sintéticos/anonimizados) não devem vazar; atenção a campos gerados via Faker que simulam PII | Dataset não deve ser alterado indevidamente após a limpeza (`agent/02_limpeza.py`), sob risco de enviesar a classificação de intenção | Deve estar disponível para o Agent consultar durante a inferência, não só durante o treino/EDA |
