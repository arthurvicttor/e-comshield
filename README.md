# EcomShield

Agente de IA para e-commerce que entende a intenção do cliente e automatiza atendimentos,
identificando se ele quer comprar, vender, devolver um produto, tirar dúvidas ou resolver algum
problema.

Desenvolvido como Projeto de Bloco da disciplina de Análise e Segurança de Agentes de IA (Prof.
Ricardo Mesquita). Ao final do bloco, o sistema também será alvo de um teste de segurança
(pentest) conduzido por outra dupla da turma.

## Domínio do projeto

**E-ComShield** — suporte de e-commerce e reembolsos. O agente de IA atende clientes lidando com
rastreamento de pedidos, trocas, devoluções, reembolsos e reclamações de produto defeituoso.

- **Desafio de IA:** identificar a intenção do usuário (rastreamento, troca, devolução, reembolso
  etc.) e analisar o tom/sentimento da mensagem.
- **Desafio de segurança:** evitar falhas de IDOR (Insecure Direct Object Reference), onde um
  usuário conseguiria acessar o histórico de compras de outro através das ferramentas do agente.

## Divisão de papéis

| Integrante | Papel | Responsabilidades |
|---|---|---|
| Integrante A (Sandy) | Engenheiro de Dados & IA | EDA, tratamento do dataset, treinamento do classificador de intenção, lógica do agente (memória e tool calling) |
| Integrante B (Arthur) | Engenheiro de Software & Application Security | API FastAPI, controles OWASP Top 10, JWT, rate limiting, OWASP ZAP, relatório de pentest |

## Estrutura do repositório

```
e-comshield/
├── agent/               # Parte de Dados & IA (Integrante A)
│   ├── 01_eda.ipynb
│   ├── 02_limpeza.py     # aplica as decisões de limpeza e gera data/processed/
│   ├── 03_regressao_linear.ipynb   # regressão linear múltipla + resíduos (TP3)
│   ├── 04_classificador_intencao.ipynb   # TF-IDF + SVM, GridSearchCV, métricas (TP4)
│   ├── models/            # pipeline treinado (intent_classifier.joblib) + metadados
│   ├── demo_classify_server.py   # servidor de demonstração do endpoint /classify (TP4)
│   ├── run_agent.py       # agente (OpenAI Agents SDK) que chama o /classify (TP4)
│   ├── conversa_demo.md   # evidência: conversa real de 3 turnos com o agente (TP4)
│   ├── requirements.txt   # dependências da parte de Dados & IA
│   ├── agent.py          # placeholder antigo; a lógica do agente está em run_agent.py
│   └── data/             # datasets brutos e tratados (não versionados, ver seção "Datasets")
├── backend/             # API/backend (Integrante B)
│   ├── app/
│   │   ├── main.py
│   │   ├── api/
│   │   │   ├── deps.py
│   │   │   └── routes/
│   │   │       ├── health.py
│   │   │       ├── auth.py
│   │   │       ├── predict.py
│   │   │       └── orders.py
|   |   |       └── classify.py
│   │   │
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   └── rate_limit.py
│   │   │
│   │   ├── db/
│   │   │   ├── base.py
│   │   │   ├── session.py
│   │   │   └── seed_test.py
│   │   │
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   └── order.py
│   │   │
│   │   ├── schemas/
│   │   │   ├── auth.py
│   │   │   ├── health.py
│   │   │   ├── predict.py
│   │   │   └── order.py
|   |   |   └── classify.py
|   |   |
│   │   ├── security/
│   │   │   ├── jwt.py
│   │   │   ├── password.py
│   │   │   └── dependencies.py
│   │   │
│   │   └── static/
│   │       └── swagger/
│   │           ├── swagger-ui.css
│   │           ├── swagger-ui-bundle.js
│   │           └── swagger-init.js
│   │
│   ├── tests/
│   │   ├── conftest.py
│   │   └── test_security.py
│   │
│   ├── alembic/
│   ├── alembic.ini
│   ├── .env.example
│   └── requirements.txt
│
├── docs/
│   ├── security/
│   │   ├── analise-zap.md
│   │   ├── auditoria-final.md
│   │   ├── testes-seguranca.md
│   │   ├── owasp-zap-report.html.html
│   │   ├── owasp-zap-report-tp3.html
│   │   ├── openapi-tp3.json
│   │   └── Figura 1 a Figura 9 (evidências PNG)
│   │
│   ├── escolha_dataset.md
│   ├── contrato_agente_backend.md
│   ├── dfd.md
│   ├── relatorio_eda.md   # relatório de EDA estruturado (TP2, Tarefa 7)
│   ├── pergunta-classificacao.md   # pergunta de classificação (TP3)
│   └── planejamento-t2.md          # plano do Trimestre 2 (TP3)
├── README.md
└── .gitignore
```

## Como rodar (parte de Dados/IA)

1. Criar e ativar um ambiente virtual Python (dentro da pasta `agent/`):
   ```
   python -m venv venv
   venv\Scripts\activate        # Windows (PowerShell/cmd)
   source venv/bin/activate     # Linux/macOS
   ```
2. Instalar as dependências:
   ```
   pip install pandas matplotlib seaborn scipy jupyterlab ipykernel
   ```
3. Baixar os datasets (ver seção "Datasets" abaixo) e colocar dentro de `agent/data/`.
4. (Opcional, mas recomendado) Rodar o script de limpeza para gerar as versões tratadas:
   ```
   python 02_limpeza.py
   ```
5. Abrir o notebook `agent/01_eda.ipynb` no JupyterLab (`jupyter lab`) e rodar as células em ordem.

## Como rodar (parte de Backend/API)

1. Entrar na pasta `backend/` e criar/ativar um ambiente virtual Python:
   ```
   cd backend
   python -m venv .venv
   .venv\Scripts\Activate.ps1 ou .venv\Scripts\activate       # Windows (PowerShell/cmd)
   source .venv/bin/activate     # Linux/macOS
   ```
2. Instalar as dependências:
   ```
   pip install -r requirements.txt
   ```
3. Criar o arquivo `.env` a partir do `.env.example` e preencher a `SECRET_KEY`, utilizada para assinar os tokens JWT.

   Uma nova chave pode ser gerada localmente com:

   ```
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```
   Copie o valor retornado e adicione ao arquivo .env
4. Configurar o PostgreSQL:
- Baixe e instale o PostgreSQL.
- Abra o pgAdmin e crie um banco chamado ecomshield.
- No arquivo backend/.env, configure:
- DATABASE_URL=postgresql://postgres:SUA_SENHA@localhost:5432/ecomshield
5. Aplicar as migrações:
   alembic upgrade head
6. Rodar a API:
   ```
   uvicorn app.main:app --reload
   ```
8. A API sobe por padrão em `http://127.0.0.1:8000`.

### Rotas disponíveis:
- `GET /health` — verifica a disponibilidade da API e não requer autenticação.
- `POST /auth/token` — autentica o usuário e retorna um token JWT.
- `POST /predict` — protegida por JWT; recebe a mensagem do usuário e retorna uma resposta placeholder enquanto o Agent não está integrado.
- `GET /orders/{order_id}` — consulta um pedido autenticado, verificando a propriedade do recurso (BOLA).
- `POST /classify` — protegida por JWT; classifica a intenção de uma mensagem utilizando o modelo treinado.

O endpoint `/classify` integra o classificador de intenções desenvolvido pela equipe de Dados e IA ao backend FastAPI. A requisição é autenticada por JWT e encaminhada ao pipeline de classificação treinado, baseado em TF-IDF e SVM Linear.
A implementação utiliza validação de entrada para impedir requisições com tipos incompatíveis, campos inesperados ou textos que não atendam ao contrato definido.
A documentação interativa da API pode ser acessada em `http://127.0.0.1:8000/docs`, após a inicialização local do backend.

### Rate Limiting

O endpoint `/auth/token` possui limite de **5 requisições por minuto por endereço IP**, utilizando rate limiting para reduzir tentativas automatizadas de brute force contra a autenticação.

A documentação interativa da API está disponível em:
`http://127.0.0.1:8000/docs`

### Testes automatizados e segurança da API

A segurança do E-ComShield foi implementada considerando princípios de autenticação, autorização, validação de entradas e proteção dos recursos expostos pela API.

**Controles implementados:**

- **Autenticação JWT:** utilização de tokens para proteger endpoints que exigem identificação do usuário.
- **Autorização por propriedade:** verificação do vínculo entre usuário autenticado e pedido consultado, reduzindo riscos de BOLA/IDOR.
- **Rate limiting:** restrição de tentativas repetidas de autenticação no endpoint `/auth/token`, com limite configurado de cinco requisições por minuto por endereço IP.
- **Validação de entrada:** utilização de schemas Pydantic para validar tipos, campos obrigatórios e propriedades adicionais.
- **Segurança HTTP:** aplicação de políticas de CSP e configuração restritiva de CORS.
- **Persistência de dados:** PostgreSQL, com modelos relacionais e migrações gerenciadas pelo Alembic.

A implementação é acompanhada por testes automatizados com Pytest, utilizados para verificar autenticação obrigatória, acesso indevido a pedidos, credenciais incorretas, validação de payloads e limitação de requisições.

Para executar os testes localmente, a partir da pasta `backend/`:

```bash
pytest tests/ -v
```

O projeto também utiliza um workflow do GitHub Actions para executar os testes em ambiente automatizado, com PostgreSQL, preparação do banco de dados e instalação das dependências necessárias.

**Evidências da execução dos testes:**

![Figura 17 - Execução dos testes automatizados do TP4](./docs/security/Figura%2017%20-%20Execução%20dos%20testes%20automatizados%20do%20TP4%20no%20terminal..png)

![Figura 19 - Testes automatizados de segurança e classificação](./docs/security/Figura%2019%20-%20Execução%20dos%20testes%20automatizados%20de%20segurança%20e%20classificação%20do%20TP4..png)

A documentação técnica das verificações de segurança está disponível em [`docs/security/testes-seguranca.md`](./docs/security/testes-seguranca.md).

### Integração do classificador de intenções ao backend

Durante a evolução do E-ComShield, o backend passou a disponibilizar a classificação de intenções por meio de um endpoint protegido por JWT.

A integração utiliza o modelo treinado pela equipe de Dados e Inteligência Artificial, conectando o pipeline de classificação ao serviço FastAPI.

**Etapas documentadas da integração:**

1. **Validação inicial do endpoint:** identificação de uma resposta HTTP 503 durante a execução do classificador, registrada para diagnóstico.
2. **Validação do contrato de entrada:** rejeição de campos adicionais e textos vazios, com respostas HTTP 422.
3. **Classificação operacional:** execução do modelo treinado, retornando HTTP 200 e informações da intenção prevista.
4. **Verificação de diferentes mensagens:** avaliação de exemplos distintos de intenções no classificador SVM Linear.
5. **Integração com o agente:** comunicação autenticada entre o agente desenvolvido com OpenAI Agents SDK e o endpoint de classificação.

**Evidências da validação inicial e dos contratos:**

![Figura 14 - Validação inicial do classify com HTTP 503](./docs/security/Figura%2014%20-%20Validação%20do%20endpoint%20classify%20com%20JWT%20e%20retorno%20HTTP%20503..png)

![Figura 15 - Rejeição de campos extras](./docs/security/Figura%2015%20-%20Rejeição%20de%20campos%20extras%20no%20classify%20com%20HTTP%20422..png)

![Figura 16 - Rejeição de texto vazio](./docs/security/Figura%2016%20-%20Rejeição%20de%20texto%20vazio%20no%20classify%20com%20HTTP%20422..png)

**Evidências do classificador em funcionamento:**

![Figura 18 - Classificação autenticada com HTTP 200](./docs/security/Figura%2018%20-%20Classificação%20de%20intenção%20com%20modelo%20treinado%20e%20retorno%20HTTP%20200%20no%20Swagger%20UI..png)

![Figura 20 - Validação de diferentes intenções](./docs/security/Figura%2020%20-%20Validação%20de%20diferentes%20intenções%20pelo%20classificador%20SVM%20Linear..png)

**Evidência da integração entre agente e backend:**

![Figura 23 - Integração autenticada com JWT](./docs/security/Figura%2023%20-%20Integração%20do%20agente%20OpenAI%20Agents%20SDK%20com%20endpoint%20Classify%20autenticado%20por%20JWT.png)

A integração permite que o agente utilize as previsões produzidas pelo modelo treinado por meio de uma interface HTTP autenticada, mantendo a separação entre os componentes de IA e os controles de segurança da API.

## Datasets

Os datasets brutos não são versionados no repositório (arquivos grandes / licença a confirmar).
Documentação completa da escolha, fonte e licença de cada um está em `docs/escolha_dataset.md`.

### 1. Bitext Retail eCommerce LLM Chatbot Training Dataset
- Sintético, gerado pela Bitext.
- Fonte: https://huggingface.co/datasets/bitext/Bitext-retail-ecommerce-llm-chatbot-training-dataset
- Licença: CDLA-Sharing-1.0 (uso e modificação permitidos, com atribuição e mesma licença em derivados).
- 44.884 linhas, 5 colunas: `instruction`, `intent`, `category`, `tags`, `response`.
- 13 categorias, 46 intenções, ~1.000 exemplos por intenção (bem balanceado).
- Sem valores ausentes, sem duplicatas.
- Papel no projeto: fonte principal de treinamento do classificador de intenção (texto e rótulo
  bem alinhados, balanceados).

### 2. Customer_support_data.csv ("Shopzilla") — eCommerce Customer Service Satisfaction
- Real (dados de uma plataforma de e-commerce real, pseudônimo "Shopzilla"), com campos de
  identificação (agente, supervisor, manager, cidade do cliente) ofuscados via biblioteca Faker
  por privacidade — o conteúdo das interações (categoria, subcategoria, CSAT) é preservado.
- Fonte: https://www.kaggle.com/datasets/ddosad/ecommerce-customer-service-satisfaction
- Licença: "Other (specified in description)" — sem termos explícitos de restrição localizados na
  descrição pública; usado para fins educacionais/não comerciais no âmbito deste Projeto de Bloco.
- 85.907 linhas, 20 colunas.
- 12 categorias (Returns 51%, Order Related 27%, Refund Related, Product Queries, entre outras),
  55 subcategorias.
- Papel no projeto: dado real para EDA, validação da distribuição real de intenções, análise de
  CSAT, e teste de generalização do classificador treinado com o Bitext.

## Principais achados da EDA

- **Distribuição de categorias real vs. sintética:** no Bitext (sintético) as categorias ficam
  relativamente equilibradas entre si; no Shopzilla (real), Returns sozinha responde por mais da
  metade dos chamados. Dataset sintético balanceado não reproduz a concentração real de intenções
  de um domínio de e-commerce.
- **Satisfação (CSAT) não segue a intuição de "categoria com atrito = nota baixa":** Returns tem
  CSAT médio alto (4,35), enquanto Cancellation (3,99) e Others (3,43, amostra pequena de 99
  registros) têm os piores resultados. Sugere que o processo de devolução é bem resolvido, e que
  falta de caminho de resolução claro (cancelamento, casos fora do fluxo padrão) é o que mais
  frustra o cliente. **Validado estatisticamente no TP2** com teste de Mann-Whitney U
  (p ≈ 1,7×10⁻¹⁰⁷) — a diferença é significativa e na direção oposta à intuição inicial (ver
  `docs/relatorio_eda.md`).
- **Pedidos de maior valor concentram reclamação de atraso, não de fraude:** entre os 5% de
  pedidos mais caros, a subcategoria `Delayed` salta de 8,6% (geral) para 26,5%, e `Order status
  enquiry` de 8,1% para 18,1%. `Priority delivery` quase não muda. Valor do pedido está mais
  associado à ansiedade do cliente com entrega/rastreamento do que a tratamento
  prioritário/suspeita de fraude.
- **Correlação fraca entre valor do pedido, CSAT e tempo de resposta (TP2):** o heatmap de
  correlação e os scatter plots não mostraram relação relevante entre essas três variáveis — a
  satisfação do cliente provavelmente depende mais do desfecho do atendimento do que do valor
  pago ou da velocidade da resposta. Análise completa em `docs/relatorio_eda.md`.

## Decisões de limpeza de dados

**Shopzilla:**
- `Customer Remarks` vazio em 66,5% das linhas (57.165 de 85.907) — usar subconjunto filtrado
  (`dropna`) para qualquer tarefa dependente de texto; manter dataset completo para análises que
  não dependem de texto.
- `connected_handling_time` preenchido em apenas 0,3% das linhas — coluna descartada.
- `Order_id`, `order_date_time`, `Customer_City`, `Product_category`, `Item_price` com 21%–80% de
  ausência — usar apenas nas análises específicas com dado suficiente, sem preenchimento
  artificial.
- Colunas de data lidas como texto — converter com `pd.to_datetime` se necessário calcular tempo
  de resposta.
- `Agent_name`, `Supervisor`, `Manager`, `Customer_City` gerados via Faker — não analíticos,
  ignorar em qualquer inferência real.
- Categoria `Others` (99 registros) — qualquer estatística sobre ela deve ser tratada com ressalva
  de amostra pequena.

**Bitext:** nenhuma limpeza necessária (0 ausentes, 0 duplicatas).

**Entre os dois:** taxonomias de categoria/intenção diferentes entre os datasets — necessário criar
mapeamento explícito (Shopzilla `category`/`Sub-category` → Bitext `category`/`intent`) antes de
combinar os dois para treinar ou validar o classificador.

## Contrato Agente ↔ Backend

Interface definida entre a parte de Dados/IA (agente) e a parte de Backend/API, documentada em
`docs/contrato_agente_backend.md`. Resumo:

- **Input do agente:** `session_id`, `user_id`, `mensagem` do usuário (`historico` de conversa
  opcional na v1).
- **Categorias/intenções do agente** (focadas no escopo do E-ComShield): `ORDER` (track_order,
  cancel_order, change_order, request_invoice), `DELIVERY` (track_delivery, delivery_issue,
  damaged_delivery, wrong_item, missing_item, delivery_time, shipping_costs), `RETURNS`
  (request_refund, refund_status, refund_policy, return_product e variações), `PRODUCT`
  (product_issue, exchange_product e variações), e `outro` para o que não se encaixa.
- **Entidades extraídas:** `numero_pedido`, `produto`, `motivo`, `sentimento`.
- **Resposta do agente:** `category`, `intent`, `confidence`, `entidades`, `resposta_texto`,
  `requer_acao_backend`, `acao_sugerida`.
- **Segurança:** o agente nunca deve devolver dado de pedido/usuário que não veio na mensagem
  atual — mitigação central contra IDOR.
- **Pontos em aberto:** formato de `category`+`intent` (separados vs. combinado), mapeamento de
  `acao_sugerida` por intenção, threshold de `confidence` para escalonar a humano.


## Status do TP3

O TP3 consolida as implementações do primeiro trimestre
e prepara a transição para a fase de classificação
supervisionada e avaliação adversária de segurança.

### Dados & Inteligência Artificial — Integrante A

- [x] **Critério 1 — Regressão linear e múltipla:**
  pipeline de pré-processamento, treinamento e avaliação.
  [Notebook de regressão](./agent/03_regressao_linear.ipynb)

- [x] **Critério 2 — Avaliação da regressão:**
  métricas R² e RMSE, residual plot e Q-Q plot.
  [Notebook de regressão](./agent/03_regressao_linear.ipynb)

- [x] **Critério 3 — Limitações da regressão:**
  análise técnica das limitações para classificação
  de intenções.
  [Notebook de regressão](./agent/03_regressao_linear.ipynb)

- [x] **Critério 7 — Pergunta de classificação:**
  definição das classes e distribuição no dataset.
  [Pergunta de classificação](./docs/pergunta-classificacao.md)

- [x] **Critério 8 — ML supervisionado:**
  justificativa técnica da abordagem preditiva.
  [Pergunta de classificação](./docs/pergunta-classificacao.md) |
  [Planejamento T2](./docs/planejamento-t2.md)

### TP4 — Classificador e agente (Dados & IA — Integrante A)

- [x] **Treinamento do classificador:** TF-IDF + SVM linear (calibrado), com baseline, matriz de
  confusão, precision/recall/F1 por classe e ROC-AUC.
  [Notebook do classificador](./agent/04_classificador_intencao.ipynb) |
  [Relatório TP4](./docs/relatorio-classificador-tp4.md)

- [x] **GridSearchCV:** 2 hiperparâmetros × 3 valores, melhores parâmetros e ganho documentados.
  [Notebook do classificador](./agent/04_classificador_intencao.ipynb)

- [x] **Endpoint `/classify`:** contrato implementado e testado em
  [`agent/demo_classify_server.py`](./agent/demo_classify_server.py) (servidor de demonstração;
  integração ao backend real é do Integrante B — ver pendência no relatório).
  [Relatório TP4](./docs/relatorio-classificador-tp4.md)

- [x] **Agente (OpenAI Agents SDK):** `Agent` + `@function_tool` + `Runner.run`, conversa real de
  3 turnos.
  [Código do agente](./agent/run_agent.py) |
  [Conversa de demonstração](./agent/conversa_demo.md)

### Backend & Application Security — Integrante B

O Integrante B foi responsável pelo desenvolvimento e pela evolução da API FastAPI do E-ComShield, incluindo persistência de dados, autenticação, autorização, validação de entradas, controles de segurança, testes automatizados, integração do classificador de intenções e avaliação adversarial de segurança.

As entregas estão organizadas por critério da rubrica, implementação técnica e evidências, permitindo rastrear cada funcionalidade até o código e os registros de execução.

### Integração do classificador de intenções à API

- [x] **Critério 1 — Integração do classificador ao FastAPI:**  
  integração do modelo TF-IDF + SVM Linear ao backend E-ComShield, permitindo classificar mensagens e retornar a intenção prevista e sua confiança.  
  [Código do backend](./backend/app/) |  
  [Rotas da API](./backend/app/api/routes/) |  
  [Modelo treinado](./agent/models/) |  
  [Notebook de treinamento](./agent/04_classificador_intencao.ipynb)

- [x] **Critério 2 — Autenticação JWT no endpoint `/classify`:**  
  proteção do endpoint de classificação, exigindo token JWT válido antes do processamento das requisições.  
  [Código de autenticação](./backend/app/security/) |  
  [Dependências da API](./backend/app/api/deps.py) |  
  [Rotas](./backend/app/api/routes/)

- [x] **Critério 3 — Diagnóstico de indisponibilidade:**  
  identificação e registro de retorno HTTP 503 durante a integração inicial do classificador, preservando a evidência do diagnóstico.  
  Evidência: Figura 14.

- [x] **Critério 4 — Validação de entradas:**  
  verificação da rejeição de campos inesperados e textos vazios, com respostas HTTP 422 conforme o contrato da API.  
  [Schemas](./backend/app/schemas/) |  
  [Rotas](./backend/app/api/routes/) |  
  Evidências: Figuras 15 e 16.

- [x] **Critério 5 — Execução autenticada do classificador:**  
  validação do endpoint `/classify` no Swagger UI, com respostas HTTP 200 e previsões para diferentes intenções.  
  [Rotas](./backend/app/api/routes/) |  
  [Modelo treinado](./agent/models/) |  
  Evidências: Figuras 18 e 20.

- [x] **Critério 6 — Testes automatizados:**  
  execução da suíte Pytest após a integração, verificando controles de segurança e funcionalidades de classificação.  
  [Código dos testes](./backend/tests/) |  
  Evidências: Figuras 17 e 19.

### Integração entre o agente de IA e o backend autenticado

- [x] **Critério 7 — Comunicação autenticada entre agente e API:**  
  integração do agente desenvolvido com OpenAI Agents SDK ao backend FastAPI, utilizando `/auth/token` para obtenção de JWT e `/classify` para classificação autenticada.  
  [Código do agente](./agent/run_agent.py) |  
  [Autenticação](./backend/app/api/routes/auth.py) |  
  [Rotas](./backend/app/api/routes/) |  
  [Contrato de integração](./docs/contrato_agente_backend.md) |  
  Evidência: Figura 23.

- [x] **Critério 8 — Validação do fluxo integrado:**  
  demonstração da comunicação entre agente e classificador em três turnos de conversa, utilizando diferentes mensagens de atendimento.  
  [Código do agente](./agent/run_agent.py) |  
  [Registro da conversa](./agent/conversa_demo.md) |  
  Evidências: Figuras 21 e 22.

### Avaliação adversarial de segurança da FintechGuard

- [x] **Critério 9 — Reconhecimento da superfície de ataque:**  
  identificação de serviços, caminhos e endpoints utilizando Nmap, Gobuster e Kiterunner, com registro da cobertura parcial do reconhecimento.  
  [Evidências de reconhecimento](./pentest/evidencias/reconhecimento/)

- [x] **Critério 10 — Análise passiva OWASP ZAP:**  
  inspeção das respostas HTTP e documentação Swagger UI, avaliando alertas de CSP, recursos externos e Subresource Integrity sem presumir vulnerabilidades confirmadas.  
  [Evidências ZAP](./pentest/evidencias/zap/)

- [x] **Critério 11 — Testes BOLA/IDOR:**  
  verificação de autorização entre dois usuários Customer, com HTTP 200 para recursos próprios e HTTP 404 nas tentativas de acesso cruzado.  
  [Evidências BOLA](./pentest/evidencias/bola/)

- [x] **Critério 12 — Testes BFLA:**  
  avaliação da separação de privilégios entre Customer e Admin, com HTTP 401 para acessos administrativos não autorizados e autenticação administrativa por sessão.  
  [Evidências BFLA](./pentest/evidencias/bfla/)

- [x] **Critério 13 — Segurança de tokens JWT:**  
  testes de manipulação de algoritmos JWT e avaliação offline de possíveis segredos HS256, com rejeição dos tokens manipulados por HTTP 401 e ausência de correspondências no dicionário limitado.  
  [Evidências JWT](./pentest/evidencias/jwt/)

- [x] **Critério 14 — Fuzzing de entradas:**  
  execução de testes com Wfuzz no endpoint `/classify/`, verificando autenticação e validação de payloads, com retornos HTTP 401, 200 e 422 conforme os cenários.  
  [Evidências de fuzzing](./pentest/evidencias/fuzzing/)

- [x] **Critério 15 — Enumeração controlada com Burp Intruder:**  
  execução de cinco requisições para identificadores de tickets, verificando HTTP 200 para recursos próprios e HTTP 404 para os demais identificadores testados.  
  [Evidências IDOR](./pentest/evidencias/idor/)

- [x] **Critério 16 — Documentação da avaliação adversarial:**  
  consolidação do escopo autorizado, ferramentas, procedimentos, respostas HTTP, limitações, evidências e recomendações em relatório técnico da FintechGuard.  
  [Evidências do pentest](./pentest/evidencias/) |  
  [Aplicação avaliada](https://fintechguard.onrender.com)

  **Observação:** os testes adversariais foram executados contra a FintechGuard, não contra o E-ComShield. Seus resultados não representam validação de segurança do backend E-ComShield.

### Planejamento do Trimestre 2 — Ambos os integrantes

- [x] **Critério 9 — Planejamento do classificador:**
  definição do modelo candidato, estratégia de
  feature engineering e justificativa técnica.
  Evidência: planejamento T2.

- [x] **Critério 10 — Avaliação adversária:**
  identificação da dupla adversária e registro
  da URL/IP da API alvo.
  Situação: adiado para o TP4 por orientação do professor; não é exigido no TP3.
  [Planejamento T2, seção 6](./docs/planejamento-t2.md)

### Documentação complementar

- [Relatório de EDA](./docs/relatorio_eda.md)
- [Contrato entre agente e backend](./docs/contrato_agente_backend.md)
- [Diagrama de fluxo de dados](./docs/dfd.md)
- [Análise OWASP ZAP — TP2 e TP3](./docs/security/analise-zap.md)
- [Auditoria final de segurança — TP3](./docs/security/auditoria-final.md)

## Uso de IA

Conforme a política "Sinal Verde 🟢" do enunciado, este projeto foi desenvolvido com apoio de
ferramentas de IA (Claude, da Anthropic), sendo obrigatório citar seu uso. A IA foi utilizada para:

- Orientar a estrutura da análise exploratória (EDA) e sugerir a sequência de tarefas do TP1.
- Auxiliar na pesquisa e comparação de datasets candidatos (Bitext, Shopzilla e outras opções
  descartadas), incluindo verificação de licença e estrutura de colunas.
- Redigir o script de limpeza (`agent/02_limpeza.py`) a partir das decisões de limpeza definidas
  em conjunto durante a EDA.
- Redigir e revisar a documentação do projeto (este README, `docs/escolha_dataset.md`,
  `docs/contrato_agente_backend.md`).
- Auxiliar na formulação e verificação estatística das 3 hipóteses da Tarefa 3 (incluindo revisão
  de hipóteses que não se confirmaram nos dados, como a relação inicial suposta entre categoria de
  atrito e CSAT baixo).
- No TP3, auxiliar no notebook de regressão linear e na redação dos documentos de classificação e de
  planejamento do T2.
- No TP2, auxiliar na escolha do teste estatístico adequado (Mann-Whitney U, após verificação de
  normalidade com Shapiro-Wilk), na construção do heatmap de correlação e dos scatter plots, e na
  redação do relatório de EDA estruturado (`docs/relatorio_eda.md`).

Todas as decisões finais — escolha do dataset, interpretação dos resultados, validação das
hipóteses com os dados reais — foram revisadas e conferidas manualmente antes de serem
incorporadas ao trabalho, em linha com a responsabilidade do aluno de garantir a precisão das
informações usadas a partir de IA.
