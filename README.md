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
| Integrante B | Engenheiro de Software & Application Security | API FastAPI, controles OWASP Top 10, JWT, rate limiting, OWASP ZAP, relatório de pentest |

## Estrutura do repositório

```
e-comshield/
├── agent/               # Parte de Dados & IA (Integrante A)
│   ├── 01_eda.ipynb
│   ├── 02_limpeza.py     # aplica as decisões de limpeza e gera data/processed/
│   ├── agent.py          # lógica do agente (memória e tool calling) — próxima etapa
│   └── data/             # datasets brutos e tratados (não versionados, ver seção "Datasets")
├── backend/                       # API/backend (Integrante B)
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   │
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── routes/
│   │   │       ├── __init__.py
│   │   │       ├── health.py
│   │   │       ├── auth.py
│   │   │       └── predict.py
│   │   │
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   └── config.py
│   │   │
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   └── predict.py
│   │   │
│   │   └── security/
│   │       ├── __init__.py
│   │       ├── jwt.py
│   │       ├── password.py
│   │       └── dependencies.py
│   │
│   ├── .env.example
│   ├── requirements.txt
│   └── ...
├── docs/
│   ├── escolha_dataset.md
│   └── contrato_agente_backend.md
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
   pip install pandas matplotlib seaborn jupyterlab ipykernel
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
4. Rodar a API:
   ```
   uvicorn app.main:app --reload
   ```
5. A API sobe por padrão em `http://127.0.0.1:8000`.

Rotas disponíveis:
- `GET /health` — verifica a disponibilidade da API e não requer autenticação.
- `POST /auth/token` — autentica o usuário e retorna um token JWT.
- `POST /predict` — protegida por JWT; recebe a mensagem do usuário e retorna uma resposta placeholder enquanto o Agent não está integrado.

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
  frustra o cliente.
- **Pedidos de maior valor concentram reclamação de atraso, não de fraude:** entre os 5% de
  pedidos mais caros, a subcategoria `Delayed` salta de 8,6% (geral) para 26,5%, e `Order status
  enquiry` de 8,1% para 18,1%. `Priority delivery` quase não muda. Valor do pedido está mais
  associado à ansiedade do cliente com entrega/rastreamento do que a tratamento
  prioritário/suspeita de fraude.

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

## Status do TP1 (entrega 26/08/2026)

- [x] Escolha e documentação dos datasets (Tarefa 1)
- [x] EDA inicial: shape, dtypes, valores ausentes, duplicatas, distribuição de categorias (Tarefa 2)
- [x] Visualizações e hipóteses (Tarefa 3)
- [x] Decisões de limpeza aplicadas (`agent/02_limpeza.py`) e datasets tratados salvos em `agent/data/processed/`
- [x] Estrutura FastAPI + JWT + 3 rotas (Tarefa 4 — Integrante B): `GET /health`, `POST /auth/token`,
      `POST /predict` (protegida por JWT) implementadas em `backend/app/`
- [ ] DFD + tríade CIA (Tarefa 5 — conjunto)
- [ ] Publicação no Git com README completo (Tarefa 6 — em andamento)

## Próximos passos

1. Sincronizar o contrato agente↔backend com o mapeamento real de categorias definido na limpeza.
2. Testar manualmente o comportamento de autenticação (`/predict` deve retornar 401 sem token e
   200 com token válido) antes da entrega.
3. Montar o DFD com trust boundaries e análise CIA em conjunto.
4. Fechar o README com instruções de execução também da API, assim que ela existir.
5. Criar o repositório Git e publicar (Tarefa 6).

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

Todas as decisões finais — escolha do dataset, interpretação dos resultados, validação das
hipóteses com os dados reais — foram revisadas e conferidas manualmente antes de serem
incorporadas ao trabalho, em linha com a responsabilidade do aluno de garantir a precisão das
informações usadas a partir de IA.

## Observações do professor relevantes ao TP1

- Preferir dataset real ou híbrido a puramente sintético; combinar múltiplos datasets é esperado
  e recomendado ("Frankenstein" de datasets).
- Manter o dataset em inglês é aceitável — tradução é etapa de fases futuras do curso.
- Hipóteses de distribuição de intenção (Tarefa 3) não exigem justificativa estatística rigorosa
  nesta fase do curso.
- Dataset não deve carregar dados administrativos irrelevantes à tarefa de IA (ex.: matrícula,
  nota, endereço) — apenas o necessário para intenção/sentimento/urgência.
- Nesta etapa, o DFD é só mapeamento (entrada, saída, trust boundaries, CIA) — nenhuma
  implementação de defesa de segurança é esperada ainda.
