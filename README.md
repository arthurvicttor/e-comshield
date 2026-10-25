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
│   ├── agent.py          # lógica do agente (memória e tool calling) — próxima etapa
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
│   │   │
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

### Rate Limiting

O endpoint `/auth/token` possui limite de **5 requisições por minuto por endereço IP**, utilizando rate limiting para reduzir tentativas automatizadas de brute force contra a autenticação.

A documentação interativa da API está disponível em:
`http://127.0.0.1:8000/docs`

### Testes de segurança
- Para executar os testes automatizados:
`pytest tests/`
- A suíte contém testes para autenticação, autorização/BOLA e validação de campos adicionais.

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

### Backend & Application Security — Integrante B

- [x] **Critério 4 — Testes de segurança:**
  implementação de cinco testes Pytest cobrindo
  autenticação, BOLA/IDOR, validação de entradas
  e rate limiting.
  [Código dos testes](./backend/tests/test_security.py) |
  [Documentação](./docs/security/testes-seguranca.md)

- [x] **Critério 5 — GitHub Actions:**
  pipeline automatizado com PostgreSQL, migrations,
  seed de testes e execução do Pytest.
  [Workflow CI/CD](./.github/workflows/security-tests.yml) |
  [Seed de testes](./backend/app/db/seed_test.py)

- [x] **Critério 6 — Execução do Pytest:**
  cinco testes automatizados aprovados.
  [Código dos testes](./backend/tests/test_security.py) |
  [Auditoria final](./docs/security/auditoria-final.md)

- [x] **Critério 11 — Auditoria OWASP ZAP:**
  tratamento dos findings Medium/High identificados
  e realização de novo scan de segurança.
  [Análise dos findings](./docs/security/analise-zap.md) |
  [Auditoria final](./docs/security/auditoria-final.md) |
  [Relatório ZAP TP3](./docs/security/owasp-zap-report-tp3.html)

- [x] **Critério 12 — Documentação OpenAPI:**
  documentação dos endpoints, parâmetros, autenticação
  e schemas de entrada e saída.
  [Configuração FastAPI](./backend/app/main.py) |
  [Rotas da API](./backend/app/api/routes/) |
  [Schemas](./backend/app/schemas/) |
  [Auditoria final](./docs/security/auditoria-final.md)

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
