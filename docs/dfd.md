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

    User->>API: POST /auth/token<br/>username + password
    Note over API: TRUST BOUNDARY 1<br/>Autenticação / JWT
    API-->>User: Access Token (JWT)

    User->>API: POST /predict<br/>Bearer Token + mensagem
    API->>API: Validar JWT

    alt Token inválido ou ausente
        API-->>User: 401 Unauthorized
    else Token válido
        API-->>User: Resposta placeholder
    end

    Note over Agent: TRUST BOUNDARY 2<br/>Integração futura
    API-.->>Agent: Mensagem (futuro)
    Agent-.->>API: Resposta (futuro)

    User->>API: GET /health
    API-->>User: 200 OK
```

## Análise CIA

| Componente | Confidencialidade | Integridade | Disponibilidade |
|---|---|---|---|
| Usuário / Bot | Credenciais, tokens e mensagens devem ser protegidos | Mensagens não devem ser alteradas durante o transporte | Deve conseguir enviar requisições |
| FastAPI | Tokens e dados recebidos devem ser protegidos | Autenticação e requisições devem ser validadas | API deve permanecer disponível |
| Agent *(integração futura)* | Mensagens e contexto podem conter dados sensíveis | Respostas não devem ser manipuladas | Deve estar disponível para processar solicitações |
| Dataset | Dados devem ser protegidos conforme sua sensibilidade | Dataset não deve ser alterado indevidamente | Deve estar disponível para EDA e treinamento |
