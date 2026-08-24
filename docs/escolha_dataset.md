# Escolha dos Datasets — E-ComShield

Este projeto usa **dois datasets complementares**, seguindo a orientação de combinar múltiplos
datasets (um sintético/balanceado + um real) em vez de depender de uma única fonte.

---

# Dataset 1

## Nome
Bitext Retail eCommerce LLM Chatbot Training Dataset

## Fonte / Link
https://huggingface.co/datasets/bitext/Bitext-retail-ecommerce-llm-chatbot-training-dataset

## Licença
Community Data License Agreement – Sharing, versão 1.0 (CDLA-Sharing-1.0).
Permite uso, cópia e modificação, inclusive para fins comerciais/acadêmicos, desde que:
- seja mantida a atribuição à Bitext como fonte original;
- eventuais versões derivadas/redistribuídas do dataset sejam compartilhadas sob a mesma licença.

## Características gerais
- 44.884 amostras (pares instrução/resposta), acima do mínimo de 500 exigido no TP1.
- 4 colunas principais: `instruction` (mensagem do usuário — nossa coluna de **texto**),
  `response` (resposta esperada), `category` (grupo semântico) e `intent` (intenção específica —
  nossa coluna de **categoria/intenção**).
- Coluna extra `tags`, com marcadores de variação linguística (ex.: B=básico, I=interrogativo,
  P=polido, Q=coloquial, W=linguagem ofensiva, Z=erros/typos) — útil para testar robustez do
  classificador depois.
- 13 categorias e 46 intenções, com ~1.000 exemplos por intenção (bem balanceado).

## Categorias e intenções (mapa completo)
| Categoria | Intenções |
|---|---|
| CONTACT | customer_service, human_agent |
| ACCOUNT | change_account, close_account, open_account, order_history, recover_password |
| APP_WEBSITE | technical_issue, use_app |
| CART | add_product, remove_product |
| DELIVERY | damaged_delivery, delivery_issue, delivery_time, missing_item, shipping_costs, track_delivery, wrong_item |
| FEEDBACK | submit_feedback, submit_product_feedback, submit_product_idea |
| ORDER | cancel_order, change_order, request_invoice, track_order |
| PAYMENT | pay, payment_issue, payment_methods |
| PRODUCT | availability, availability_in_store, availability_online, exchange_product, exchange_product_in_store, product_information, product_issue |
| RETURNS | refund_policy, refund_status, request_refund, return_policy, return_product, return_product_in_store, return_product_online |
| SALES | sales_period |
| STORE | store_location, store_opening_hours |
| USER | request_right_to_rectification |

## Recorte para o escopo do E-ComShield
A proposta do E-ComShield foca em rastreamento de cargas, reclamações de produto defeituoso e
estorno/reembolso. Isso mapeia diretamente para as categorias:
- **ORDER** (track_order, cancel_order, change_order, request_invoice)
- **DELIVERY** (track_delivery, delivery_issue, damaged_delivery, wrong_item, missing_item, delivery_time)
- **RETURNS** (request_refund, refund_status, refund_policy, return_product e variações)
- **PRODUCT** (product_issue, exchange_product e variações)

As demais categorias (CONTACT, ACCOUNT, APP_WEBSITE, CART, FEEDBACK, PAYMENT, SALES, STORE, USER)
existem no dataset completo e podem ser mantidas na EDA geral, mas não são o foco do classificador
de intenções do agente — servem mais como contexto/comparação de distribuição.

## Justificativa da escolha
1. Já vem rotulado com texto + intenção/categoria, atendendo diretamente ao requisito do TP1 sem
   necessidade de rotulagem manual.
2. Volume (quase 45 mil amostras) e balanceamento (~1.000 exemplos/intenção) evitam o problema
   comum de classes desbalanceadas logo na primeira entrega.
3. O domínio (varejo/e-commerce) é o mesmo da proposta escolhida (E-ComShield), então as intenções
   reais do dataset já se aproximam das intenções que planejamos no contrato agente↔backend
   (rastreamento, troca, devolução, reembolso), evitando retrabalho de mapeamento depois.
4. Licença CDLA-Sharing-1.0 é compatível com uso acadêmico, desde que a atribuição à Bitext seja
   mantida no README do projeto.
5. A coluna `tags` (variações linguísticas, erros de digitação, tom) dá margem para hipóteses de
   EDA sobre sentimento/urgência, que também aparecem no contrato definido com o colega.

---

# Dataset 2

## Nome
Customer_support_data.csv — "eCommerce Customer Service Satisfaction" (pseudônimo interno do
dataset: "Shopzilla")

## Fonte / Link
https://www.kaggle.com/datasets/ddosad/ecommerce-customer-service-satisfaction

## Licença
"Other (specified in description)" — o selo de licença do Kaggle indica que os termos estariam na
descrição do dataset, mas a descrição pública não contém termos explícitos de uso/restrição (não
menciona uso comercial, atribuição obrigatória, ou proibições específicas). Diante dessa
ambiguidade, o dataset é usado aqui estritamente para fins educacionais/não comerciais, no âmbito
do Projeto de Bloco, com a fonte citada e linkada nesta documentação.

## Características gerais
- 85.907 linhas, 20 colunas — muito acima do mínimo de 500 exigido no TP1.
- Colunas principais: `Customer Remarks` (texto — comentário do cliente, preenchido em 33,5% das
  linhas), `category` e `Sub-category` (nossas colunas de **categoria/intenção**), além de
  `CSAT Score`, `Item_price`, timestamps de abertura/resposta do chamado, e campos de agente
  (nome, supervisor, manager).
- **Nota de anonimização:** a descrição do dataset no Kaggle informa que a informação genuína foi
  ofuscada e o dataset foi parcialmente gerado com a biblioteca Faker para ocultar detalhes reais
  de identificação (nome de agente, supervisor, manager, cidade do cliente). O conteúdo das
  interações em si (categoria, subcategoria, `Customer Remarks`, `CSAT Score`) é preservado como
  dado real de uma plataforma de e-commerce (pseudônimo "Shopzilla").
- 12 categorias (`Returns` 51%, `Order Related` 27%, `Refund Related`, `Product Queries`,
  `Shopzilla Related`, `Payments related`, `Feedback`, `Cancellation`, `Offers & Cashback`,
  `Others`, `App/website`, `Onboarding related`) e 55 subcategorias.
- Dataset real, não balanceado — reflete a distribuição de chamados de uma operação real de
  e-commerce, ao contrário do Dataset 1 (sintético e balanceado por construção).

## Justificativa da escolha
1. É o complemento real ao Dataset 1: enquanto o Bitext é sintético e uniformemente balanceado, o
   Shopzilla traz ruído, valores ausentes e desbalanceamento real de categorias — exatamente o
   tipo de textura que só aparece em dado de operação real, valorizado na orientação do professor
   sobre preferir dado real/híbrido a puramente sintético.
2. O domínio (e-commerce, categorias de `Returns`, `Order Related`, `Refund Related`) é o mesmo da
   proposta escolhida (E-ComShield), permitindo validar a distribuição real de intenções e o
   comportamento de satisfação do cliente (CSAT) por categoria.
3. Apesar de real, os campos de identificação pessoal foram ofuscados (Faker), reduzindo
   preocupações de privacidade para uso educacional.
4. Serve tanto para a EDA quanto, futuramente, como base de teste de generalização do classificador
   de intenção treinado com o Dataset 1.

## Ressalva de licença
Diferente do Dataset 1 (licença CDLA-Sharing-1.0, clara e permissiva), a licença deste dataset não
está totalmente especificada pela fonte. Documentamos essa limitação explicitamente aqui por
transparência acadêmica, e o uso se restringe ao contexto educacional deste Projeto de Bloco.
