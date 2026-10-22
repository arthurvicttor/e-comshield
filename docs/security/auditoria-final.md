# Auditoria Final de Segurança — E-ComShield (TP3)

## 1. Objetivo

Este documento apresenta a consolidação dos controles de segurança implementados na API E-ComShield durante o primeiro trimestre do projeto, incluindo os testes automatizados, a integração contínua, a análise de vulnerabilidades com OWASP ZAP e a documentação OpenAPI.

O objetivo é avaliar o estado atual da segurança da aplicação e sua preparação para a etapa de pentest prevista no projeto.

## 2. Escopo da auditoria

A auditoria contempla o backend desenvolvido em Python com FastAPI, utilizando PostgreSQL para persistência de dados, SQLModel para modelagem e JWT para autenticação.

Os endpoints considerados são:

| Endpoint | Método | Finalidade |
|---|---|---|
| `/health` | GET | Verificação de disponibilidade |
| `/auth/token` | POST | Autenticação e emissão de JWT |
| `/predict` | POST | Processamento provisório de mensagens |
| `/orders/{order_id}` | GET | Consulta autorizada de pedidos |

A auditoria inclui testes automatizados de segurança e análise dinâmica passiva utilizando OWASP ZAP.

## 3. Checklist dos controles de segurança

| Controle | Implementação | Status |
|---|---|---|
| Autenticação JWT | Token obrigatório em rotas protegidas | Validado |
| Controle BOLA/IDOR | Verificação da propriedade do pedido | Validado no cenário testado |
| Validação de entradas | Pydantic com `extra="forbid"` | Validado |
| Rate limiting | Limite de 5 requisições/minuto no login | Validado |
| CORS | Restrição das origens autorizadas | Configurado |
| Security Headers | CSP, X-Frame-Options e X-Content-Type-Options | Configurados |
| HSTS | Enviado em requisições HTTPS | Configurado; validação HTTPS pendente |
| OWASP ZAP | Análise passiva após as correções | Executada |
| GitHub Actions | Execução automática dos testes | Validado |

## 4. Testes automatizados de segurança

A suíte de testes foi implementada utilizando Pytest e FastAPI TestClient.

Foram executados cinco casos:

1. Rejeição de acesso não autenticado aos pedidos.
2. Bloqueio de acesso a pedidos pertencentes a outros usuários (BOLA).
3. Rejeição de campos extras enviados ao endpoint `/predict`.
4. Rejeição de credenciais incorretas.
5. Retorno HTTP 429 após exceder o limite de autenticações.

**Comando utilizado:**

```bash
pytest tests/ -v
```

**Resultado:** 5 testes aprovados, sem falhas.

A implementação e os cenários de teste encontram-se em `backend/tests/test_security.py`.

Documentação complementar: [Testes de segurança](./testes-seguranca.md).

## 5. Integração contínua — GitHub Actions

Foi configurado um workflow de integração contínua para executar automaticamente a suíte de testes de segurança em eventos de push e pull request.

Arquivo de configuração:

`.github/workflows/security-tests.yml`

O pipeline realiza:

1. Preparação do ambiente Python.
2. Inicialização do PostgreSQL.
3. Instalação das dependências.
4. Execução das migrations Alembic.
5. Preparação dos usuários e pedidos de teste.
6. Execução da suíte Pytest.

Após os ajustes de preparação do banco, a execução automatizada foi validada com os cinco testes aprovados.

O workflow encerra com falha quando algum teste não passa. O bloqueio de merges depende da configuração adicional de regras de proteção da branch principal.

### Evidência

![Figura 8 - Execução automatizada dos testes de segurança no GitHub Actions](./Figura%208%20-%20Execução%20automatizada%20dos%20testes%20de%20segurança%20no%20GitHub%20Actions.png)

*Figura 8 — Execução automatizada dos testes de segurança.*

## 6. Auditoria OWASP ZAP

Durante o TP2, o OWASP ZAP identificou problemas relacionados à Content Security Policy e ao carregamento de recursos externos utilizados pelo Swagger UI.

As primeiras correções envolveram a definição explícita de diretivas CSP e a restrição da execução de scripts inline.

No TP3, foi realizada uma alteração adicional para hospedar localmente os recursos JavaScript e CSS do Swagger UI.

### 6.1. Comparação entre auditorias

| Finding | Tratamento TP2 | Situação TP3 |
|---|---|---|
| CSP sem diretiva `form-action` | Corrigido | Correção mantida |
| `script-src unsafe-inline` | Corrigido com hash | Scripts migrados para arquivos locais |
| `style-src unsafe-inline` | Corrigido | Permissão reintroduzida por compatibilidade; requer acompanhamento |
| Sub Resource Integrity Attribute Missing | Risco aceito | Alerta não identificado após hospedagem local |
| Cross-Domain JavaScript Source File Inclusion | Risco aceito | Alerta não identificado após hospedagem local |

### 6.2. Resultados do novo scan

De acordo com o novo scan realizado no TP3, os alertas identificados foram:

| Alerta | Severidade | Tratamento |
|---|---|---|
| Modern Web Application | Informativo | Nenhuma correção necessária |
| Timestamp Disclosure — Unix | Baixa | Análise para aceitação documentada |

Não foram relatados findings Medium ou High no novo scan passivo.

### Evidência

![Figura 5 - Resultado final do scan de segurança realizado com o OWASP ZAP](./Figura%205%20-%20Resultado%20final%20do%20scan%20de%20segurança%20realizado%20com%20o%20OWASP%20ZAP.png)

*Figura 5 — Resultado da reavaliação da API com OWASP ZAP.*

A descrição detalhada das vulnerabilidades, dos impactos e das medidas adotadas encontra-se em [Análise dos resultados do OWASP ZAP](./analise-zap.md).

A ausência de findings Medium/High no scan passivo não garante a inexistência de outras vulnerabilidades.

## 7. Documentação OpenAPI

A documentação OpenAPI foi atualizada para apresentar informações sobre os endpoints disponíveis, seus parâmetros e schemas de entrada e saída.

Foram implementados schemas explícitos de resposta para autenticação, disponibilidade e processamento de mensagens, além do schema já utilizado na consulta de pedidos.

A documentação interativa é disponibilizada em:

```text
http://127.0.0.1:8000/docs
```

A especificação OpenAPI pode ser consultada em:

```text
http://127.0.0.1:8000/openapi.json
```

### Evidência

![Figura 9 - Documentação OpenAPI da API E-ComShield acessível pelo Swagger UI](./Figura%209%20-%20Documentação%20OpenAPI%20da%20API%20E-ComShield%20acessível%20pelo%20Swagger%20UI.png)

*Figura 9 — Interface Swagger UI da API E-ComShield.*

## 8. Preparação para pentest

A aplicação foi preparada para a próxima etapa de avaliação de segurança, na qual poderá ser submetida a testes por outra dupla.

### Checklist de prontidão

| Item | Status |
|---|---|
| API FastAPI inicia corretamente | A confirmar no ambiente do pentest |
| Autenticação JWT funcional | Validado |
| Controle de autorização BOLA | Validado no cenário automatizado |
| Validação de campos extras | Validado |
| Rate limiting | Validado |
| Banco de testes inicializado no CI | Validado |
| Documentação OpenAPI implementada | Concluído |
| Testes de segurança automatizados | Validado |
| Auditoria passiva do ZAP realizada | Concluído |
| URL acessível à dupla adversária | Pendente de definição |

O ambiente de pentest deverá utilizar dados fictícios, credenciais de teste e infraestrutura isolada, evitando acesso a informações reais.

## 9. Limitações da auditoria

A avaliação realizada apresenta algumas limitações:

- O OWASP ZAP foi utilizado em análise passiva, sem exploração ativa abrangente dos endpoints.
- A suíte automatizada possui cinco casos e não cobre todos os cenários possíveis de autenticação e autorização.
- O rate limiting foi validado funcionalmente, mas não por testes completos de carga.
- A documentação e os controles foram avaliados predominantemente em ambiente local e no CI.
- A análise não substitui um pentest conduzido por uma equipe adversária.
- A configuração de estilos inline do Swagger UI permanece como ponto de acompanhamento.

## 10. Conclusão

A auditoria final do E-ComShield consolida os controles de segurança desenvolvidos durante o primeiro trimestre.

Foram implementados e validados mecanismos de autenticação JWT, autorização de recursos, validação de entradas e limitação de requisições.

A suíte de cinco testes automatizados foi executada com sucesso tanto no ambiente local quanto no pipeline de integração contínua do GitHub Actions.

A análise com OWASP ZAP permitiu identificar configurações que foram corrigidas progressivamente, especialmente relacionadas à Content Security Policy e ao carregamento de recursos externos pela interface Swagger.

No novo scan passivo relatado para o TP3, não foram identificados findings Medium ou High.

Dessa forma, o sistema apresenta uma base de segurança consolidada para avançar à próxima etapa de avaliações, permanecendo necessária a validação adversária e o tratamento de eventuais vulnerabilidades adicionais identificadas durante o pentest.
