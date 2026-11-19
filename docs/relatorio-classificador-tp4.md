# Relatório — Classificador de intenção e agente (TP4, parte de Dados & IA)

Este documento resume as tarefas 1 a 4 do TP4 (treinar o classificador, integrar a um endpoint de
classificação e construir o agente), que são a parte de Dados & IA (Integrante A). As tarefas 5 e 6
(ataques à API de outra dupla e log de pentest) são da parte de Backend & Application Security
(Integrante B) e não estão neste documento — ver a seção "O que não está aqui" no final.

## 1. Classificador de intenção

Notebook completo: [`agent/04_classificador_intencao.ipynb`](../agent/04_classificador_intencao.ipynb).

**Pipeline:** TF-IDF + modelo linear, dentro de um `Pipeline` do scikit-learn, seguindo a
arquitetura de `docs/planejamento-t2.md` (split 70/15/15 estratificado — treino / validação /
teste; o teste só é tocado uma vez, no final).

**Baseline trivial** (sempre prever a classe mais frequente, `DummyClassifier`): acurácia 2,23% e
F1 macro 0,0009 — o piso esperado com 46 classes quase balanceadas.

**GridSearchCV** na regressão logística, 5 dobras, otimizando F1 macro, 2 hiperparâmetros × 3
valores cada (9 combinações, 45 ajustes):
- `clf__C`: 0,1 / 1 / 10
- `tfidf__ngram_range`: (1,1) / (1,2) / (1,3)

Melhor combinação: `C=10`, `ngram_range=(1,2)` — F1 macro de validação cruzada 0,9875, um ganho de
+0,0009 sobre a configuração "de olho" usada como ponto de partida.

**Comparação dos dois modelos candidatos no teste** (conjunto nunca visto antes):

| Modelo | Acurácia | F1 macro | ROC-AUC (OvR, macro) |
|---|---:|---:|---:|
| Baseline (classe mais frequente) | 0,0223 | 0,0009 | — |
| Regressão logística (ajustada por GridSearchCV) | 0,9886 | 0,9887 | ≈1,0000 |
| **SVM linear (calibrado) — escolhido** | **0,9911** | **0,9912** | ≈1,0000 |

O SVM linear (`LinearSVC`, calibrado com `CalibratedClassifierCV` para ter probabilidade) venceu
por uma margem pequena e foi o modelo salvo. O ROC-AUC one-vs-rest fica muito perto de 1 para os
dois — esperado, dado o desempenho já alto do F1; ele complementa o F1 macro medindo a separação
das classes em diferentes limiares, não substitui olhar a matriz de confusão.

**Precision/recall/F1 por classe:** no `classification_report` completo (no notebook), quase
todas as 46 intenções ficam com F1 ≥ 0,95. As piores (ainda assim ≥ 0,94) são exatamente os pares
de intenções próximas já previstos em `docs/pergunta-classificacao.md`: `track_order` ↔
`track_delivery`, `change_account` ↔ `close_account`, e a família `return_product*`. A matriz de
confusão confirma: os erros mais frequentes são justamente entre esses pares, não erros
aleatórios — sinal de que o modelo aprendeu a distinção certa na maior parte dos casos e erra onde
o próprio texto é ambíguo.

**Por que o desempenho é tão alto (≈99%):** o Bitext é um dataset sintético, gerado por templates
por intenção (ver `docs/pergunta-classificacao.md`), então o vocabulário de cada intenção é bem
mais consistente do que em mensagens reais de clientes. Isso já estava sinalizado como risco desde
o TP3 — o número alto mede a tarefa "classificar texto gerado por template", não necessariamente
"entender clientes reais". Validar com o Shopzilla (dataset real) continua como próximo passo, não
feito nesta etapa por falta de rótulo de intenção nesse dataset (só categoria/subcategoria).

**Artefato salvo:** [`agent/models/intent_classifier.joblib`](../agent/models/intent_classifier.joblib)
(pipeline completo, TF-IDF + SVM calibrado) e
[`agent/models/intent_classifier_metadata.json`](../agent/models/intent_classifier_metadata.json)
(classes, métricas, hiperparâmetros, dataset e split usados). Carregado com `joblib.load(...)`.

## 2. Endpoint de classificação

O enunciado do TP4 pede `POST /classify`, recebendo um texto e devolvendo a intenção com
probabilidade, autenticado por JWT. Implementei isso em
[`agent/demo_classify_server.py`](../agent/demo_classify_server.py) — **um servidor de
demonstração separado da API de produção** (`backend/`), para eu poder exercitar o classificador e
o agente de ponta a ponta sem depender de o Integrante B já ter integrado o modelo ao backend real.

**Contrato implementado:**

```http
POST /classify
Authorization: Bearer <token>
Content-Type: application/json

{ "text": "I cannot pay, notify of payment problems" }
```
```json
{ "intent": "payment_issue", "confidence": 0.98, "model_version": "svm_linear" }
```

Pontos cobertos, conforme `docs/planejamento-t2.md` seção 5: modelo carregado uma vez na subida do
serviço (nunca por requisição), validação de entrada (1–1000 caracteres, `extra="forbid"`),
autenticação Bearer obrigatória, logging sem o texto completo da mensagem (só tamanho, intenção e
confiança), e um limiar de confiança (0,30): abaixo dele, a resposta devolve `human_agent` em vez
de uma intenção arriscada.

**Pendência explícita para o Integrante B:** este endpoint usa um JWT e uma chave só de
demonstração (`DEMO_SECRET_KEY`, documentada no próprio arquivo), sem usuários reais nem Postgres.
Integrar de verdade ao `backend/` (reusar a autenticação, o banco e o padrão de rotas já
existentes) é trabalho de backend e não foi feito aqui para não mexer nesse código. O artefato
(`agent/models/intent_classifier.joblib`) e o contrato acima estão prontos para isso.

## 3. GridSearchCV

Coberto na seção 1 (notebook, seção 4): 2 hiperparâmetros (`clf__C`, `tfidf__ngram_range`), 3
valores cada, 5 dobras de validação cruzada, métrica F1 macro. Melhores parâmetros e ganho de
desempenho documentados ali e resumidos acima.

## 4. Agente com OpenAI Agents SDK

Código: [`agent/run_agent.py`](../agent/run_agent.py). Transcrição de uma conversa real de 3
turnos: [`agent/conversa_demo.md`](../agent/conversa_demo.md).

- **Agent:** `Atendente E-ComShield`, com um *system prompt* para atendimento ao cliente de
  e-commerce (instrui a sempre classificar a intenção antes de responder, nunca inventar status de
  pedido, e escalar para humano quando a confiança for baixa).
- **`@function_tool`:** `classificar_intencao(texto_do_cliente)` chama `POST /classify` via HTTP
  (`httpx`), obtendo um token de demonstração e reautenticando uma vez se o token expirar.
- **`Runner.run`:** usado em loop para manter o histórico entre os 3 turnos (`resultado.to_input_list()`).
- **Modelo usado:** o SDK é da OpenAI, mas o modelo de linguagem que o agente usa é servido pela
  **Groq** (`openai/gpt-oss-120b`, gratuito, sem cartão, endpoint compatível com a API da OpenAI),
  para não depender de uma chave paga. Basta trocar o cliente e a variável de ambiente para usar a
  OpenAI diretamente — o resto do código (`Agent`, `function_tool`, `Runner`) não muda.

**Resultado real da conversa de demonstração** (texto completo em `agent/conversa_demo.md`):

| Turno | Cliente diz | `/classify` devolveu | Resposta do agente |
|---|---|---|---|
| 1 | "Hi, my order hasn't arrived yet, where is it?" | `track_order`, confiança 0,842 | Pede o número do pedido para verificar o status |
| 2 | "Actually this product arrived damaged, I want my money back." | `damaged_delivery`, confiança 0,666 | Pede desculpas, pede número do pedido e nome do item para iniciar o reembolso |
| 3 | "yes that's right" | (não chamou a ferramenta — mensagem sem conteúdo novo a classificar) | Confirma e repete o pedido de número do pedido |

O agente decidiu sozinho não chamar `classificar_intencao` no 3º turno, por ele não descrever um
pedido/problema novo — comportamento correto, conforme o *system prompt* ("para CADA mensagem nova
que descreva um pedido, problema ou dúvida").

**Limitação encontrada e corrigida durante o teste:** a primeira tentativa de demonstração foi
escrita em português, e as duas primeiras mensagens caíram em `human_agent` com confiança muito
baixa (0,064 e 0,119). O classificador foi treinado só com o dataset Bitext, que é **inteiro em
inglês** — ele não generaliza para outros idiomas. Reescrevi a conversa de demonstração em inglês
(mesmo idioma do treino) e documentei essa limitação no *system prompt* do agente e aqui. Para um
sistema em produção com clientes em português, seria necessário treinar (ou traduzir a entrada)
com dados em português antes de integrar.

## O que não está aqui

As tarefas 5 e 6 do TP4 — ataques (`jwt_tool`, Kiterunner, Nmap, Gobuster, Burp, Wfuzz) contra a
API de outra dupla e o log parcial de pentest — são da parte de Backend & Application Security
(Integrante B) e não foram feitas neste trabalho. Além da divisão de papéis do projeto, atacar um
sistema de terceiros sem autorização por escrito é antiético e ilegal, e eu não tenho evidência
dessa autorização nem do endereço da API alvo.

## Uso de IA

Este relatório, o notebook do classificador e o código do agente foram escritos com apoio de IA
(Claude). A execução, as métricas e a conversa de demonstração foram rodadas por mim; a escolha de
usar a Groq como provedor gratuito do modelo de linguagem do agente foi uma sugestão da IA, que eu
confirmei antes de seguir.
