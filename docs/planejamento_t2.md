# Planejamento T2 — Classificador de intenção e pentest

Este documento planeja o Trimestre 2: treinar o classificador de intenção (Integrante A) e atacar a API de outra
equipe (pentest, TP4/TP5). Detalhes da pergunta de classificação e das classes estão em
`docs/pergunta_classificacao.md`.

## 1. Pergunta de classificação e classes

**f(texto) → intenção.** Dado o texto de um atendimento ao cliente, qual é a intenção do usuário?

- Dataset: Bitext Retail eCommerce, 44.884 mensagens, **46 intenções** em 13 categorias, ~1.000 exemplos por
  intenção (mínimo 721 em `missing_item`, máximo 1.000 em `request_invoice`). Bem balanceado.
- Ambiguidades principais (a vigiar na matriz de confusão): `return_product*`, `exchange_product*`,
  `availability*`, `request_refund` / `refund_status` / `refund_policy`, `track_order` / `track_delivery` e o grupo
  `delivery_issue` / `damaged_delivery` / `missing_item` / `wrong_item`.
- Regressão linear não serve (alvo categórico nominal, saída contínua, sem probabilidade): ver
  `agent/03_regressao_linear.ipynb` e a seção 5 de `docs/pergunta_classificacao.md`.

## 2. Modelo candidato

**Baseline: TF-IDF + regressão logística multinomial** (`LogisticRegression`, regularização L2).
**Modelo alternativo: SVM linear** (`LinearSVC`), comparado depois do baseline. Se eu precisar de probabilidades com o
SVM, uso `CalibratedClassifierCV`.

Por que esses dois:
- São o padrão forte para texto esparso de alta dimensão e treinam em segundos com 45 mil mensagens.
- A regressão logística já devolve **probabilidade por intenção**, necessária para o limiar de confiança que decide
  quando escalar a um humano (contrato do agente).
- São **interpretáveis**: dá para listar os termos de maior peso por intenção, útil para explicar erros e para
  discutir ataques de evasão no pentest.
- Um sanity check informal (TF-IDF + logística/SVM, split 80/20 estratificado) deu ~98–99% no Bitext. Em T2 o
  trabalho real é validar direito e testar fora do Bitext.

Ajuste de hiperparâmetros (`GridSearchCV`, F1 macro, só no conjunto de treino): `C`, `ngram_range`, `min_df` e
`class_weight`.
- `class_weight="balanced"`: o Bitext é quase balanceado, então testo `None` vs `balanced` e comparo; não parto do
  princípio de que ajuda, e ele não substitui a análise dos resultados (por classe e no Shopzilla, que é
  desbalanceado).
- `min_df=2` é só o valor inicial; se o vocabulário de erros de digitação ficar cortado demais, testo `min_df=1`.

Não vou usar modelos de linguagem grandes em T2 (fora do escopo e difíceis de auditar).

## 3. Estratégia de feature engineering para texto

1. **Limpeza mínima:** minúsculas e normalização de espaços. Não removo pontuação nem *stopwords* de saída: no
   Bitext, "?" e palavras como "not"/"how" podem diferenciar intenções parecidas (hipótese a testar).
2. **TF-IDF de palavras** (`TfidfVectorizer`) com `ngram_range=(1,2)`, `sublinear_tf=True`, `min_df=2`. Unigramas
   pegam a palavra de domínio ("refund", "invoice"); bigramas pegam construções ("return online", "in store").
3. **TF-IDF de caracteres** (`analyzer="char_wb"`, n-gramas 3–5), concatenado ao de palavras (`FeatureUnion`). O
   Bitext tem erros de digitação e gírias, e n-gramas de caracteres são mais robustos a isso.
4. **Ablação com `CountVectorizer`** (contagem simples) para ver se o ponderamento IDF ajuda.
5. **Tudo dentro de um `Pipeline`** (vetorizador + classificador), ajustado **só nos dados de treino**, para evitar
   vazamento do vocabulário/IDF para validação e teste.

## 4. Arquitetura prevista

```
Dataset rotulado (texto + intenção)
   → separação treino / validação / teste (estratificada, semente fixa)
   → Pipeline: pré-processamento + TF-IDF (ajustado só no treino)
   → Regressão logística (baseline)  |  LinearSVC (alternativo)
   → Avaliação e seleção (macro-F1, precision, recall, matriz de confusão)
   → Pipeline final salvo (joblib) e versionado
   → API FastAPI /predict: validação → inferência → resposta estruturada
```

**Separação dos dados:** 70% treino / 15% validação / 15% teste, estratificada por intenção. A validação serve para
escolher hiperparâmetros e modelo (com validação cruzada estratificada de 5 dobras dentro do treino, se couber); o
**teste só é usado uma vez, no fim**. Antes de separar, confiro duplicatas e quase-duplicatas (o Bitext é gerado por templates e pode ter
variações da mesma frase-base) e, se existirem, mantenho as variações da mesma base no mesmo conjunto, para o teste
não ficar artificialmente fácil.

**Métricas de avaliação:** F1 macro (principal), precision e recall por classe, acurácia, matriz de confusão e
relatório de erros dos pares ambíguos da seção 1.

**Validação externa:** mapear Shopzilla → intenções Bitext (já apontado em "Decisões de limpeza" do README) e medir
o modelo em `Customer Remarks`, com as ressalvas de que 66,5% estão vazias e o texto é mais avaliação do que pedido. Se
a queda for grande, esse é o resultado principal a reportar.

## 5. Integração com a API (`POST /predict`)

Contrato proposto (o formato exato ainda será alinhado com o Arthur):

```json
// Requisição
{ "message": "I cannot pay, notify of payment problems" }

// Resposta
{ "intent": "payment_issue", "category": "PAYMENT", "confidence": 0.93, "model_version": "intent-v1" }
```

Pontos técnicos a planejar:
- **Carregamento do modelo:** o pipeline é treinado **antes**, salvo em arquivo e carregado **uma vez** na subida do
  serviço. Nunca é treinado a cada requisição.
- **Validação do texto:** já existe limite de 1–1000 caracteres e `extra="forbid"` no schema; a entrada vazia ou
  inválida retorna 422.
- **Autenticação:** a rota continua protegida por JWT.
- **Tratamento de erros:** se o modelo não carregar, responder 503 com mensagem genérica, sem expor detalhes internos.
- **Baixa confiança:** abaixo de um limiar (a definir com a distribuição de confiança na validação), devolver
  escalonamento para humano em vez de uma intenção incerta.
- **Versionamento:** o nome/versão do modelo vai na resposta e no nome do arquivo salvo.
- **Logging seguro:** registrar tamanho da mensagem, intenção, confiança e versão, **não** o texto completo, pois a
  mensagem pode conter dado pessoal.
- **Limites de entrada:** tamanho máximo do texto e rate limiting, que já existem na API.
- **Segurança do artefato:** o arquivo do modelo (joblib/pickle) só é carregado de um caminho confiável do próprio
  projeto, porque desserializar um arquivo malicioso executa código.

## 6. Colega adversário

> **A PREENCHER por Sandy/Arthur:** nome da equipe adversária e GitHub.

| Campo | Valor |
|---|---|
| Equipe/colega adversário | _(nome e GitHub)_ |
| Quem na minha dupla ataca | _(Sandy / Arthur / ambos)_ |
| Quem ataca a nossa API | _(equipe que nos foi atribuída)_ |

## 7. URL ou IP da API adversária (alvo do TP4/TP5)

> **A PREENCHER:** URL/IP e porta da API do colega, a confirmar com ele.

| Campo | Valor |
|---|---|
| URL/IP base | _(ex.: http://IP:8000)_ |
| Documentação OpenAPI | _(base)/docs e _(base)/openapi.json_ |
| Contas de teste fornecidas | _(duas contas sintéticas, cada uma com um recurso, para testar BOLA)_ |
| Endpoints liberados | _(a combinar)_ |
| Fora do escopo | negação de serviço, operações destrutivas, credenciais ou dados pessoais reais |
| Período combinado | _(datas/horários)_ |

Plano de ataque inicial (a refinar quando eu ler a documentação deles):
1. Autenticação: enumeração de usuários (mensagens de erro diferentes), JWT forjado/`alg=none`/expirado.
2. Autorização: BOLA/IDOR trocando IDs de recursos entre as duas contas de teste.
3. Validação: campos extras, tipos errados, strings enormes, injeção.
4. Rate limiting: checar se existe e se dá para contornar (ex.: `X-Forwarded-For`), sem fazer DoS.
5. Cabeçalhos/CORS/CSP com scan passivo do OWASP ZAP (lembrando que CORS não é autenticação).
6. Se o endpoint de classificação estiver ativo: exemplos adversariais contra o modelo (evasão por typos/sinônimos).

## Cronograma sugerido

| Etapa | Entrega |
|---|---|
| T2 início | Baseline TF-IDF + logística em notebook, com split estratificado |
| T2 meio | LinearSVC, ablação de features, validação contra Shopzilla, integração em `/predict` |
| TP4/TP5 | Pentest da API adversária e relatório de achados |

## Uso de IA

Planejamento redigido com apoio de IA (Claude). As escolhas de modelo, features e arquitetura são propostas que ainda
preciso validar experimentalmente em T2; os campos das seções 6 e 7 dependem de informação que só eu e meu colega
temos.
