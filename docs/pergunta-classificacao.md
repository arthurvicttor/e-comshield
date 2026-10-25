# Pergunta de classificação — E-ComShield

## 1. Definição da tarefa

> **Dado o texto de uma mensagem de atendimento ao cliente de e-commerce, qual é a intenção do usuário?**

Formalmente: **f(texto) → intenção**, onde `intenção ∈ {46 classes}`.

- **Entrada:** uma mensagem de texto livre (`instruction` no Bitext; em média ~58 caracteres / ~12 palavras).
- **Saída:** **uma** intenção entre 46 possíveis (classificação **multiclasse**, um rótulo por mensagem). Exemplo:
  "I cannot pay, notify of payment problems" → `payment_issue`.
- **Uso no sistema:** o endpoint `POST /predict` recebe a mensagem e devolve a intenção prevista. Hoje ele devolve um
  *placeholder*; no Trimestre 2 passa a chamar o classificador. A intenção decide o que o agente faz (consultar
  pedido, abrir devolução, escalar para humano etc.).
- **Métricas de sucesso (T2):** F1 macro (todas as intenções pesam igual), precision e recall por classe, acurácia e
  matriz de confusão para ver quais intenções se confundem.

## 2. Classes (intenções): descrição e quantidade de amostras

O dataset Bitext Retail eCommerce tem **46 intenções** em **13 categorias**. O classificador vai prever a
**intenção** (nível fino); a categoria é um agrupamento útil para análise.
Total: 44.884 mensagens, sem ausentes e sem duplicatas em `instruction`.

| Categoria | Intenção | O cliente quer… | Amostras |
|---|---|---|---:|
| ACCOUNT | `change_account` | alterar dados da conta | 987 |
| ACCOUNT | `close_account` | encerrar/excluir a conta | 995 |
| ACCOUNT | `open_account` | criar uma conta | 987 |
| ACCOUNT | `order_history` | ver o histórico de compras | 988 |
| ACCOUNT | `recover_password` | recuperar a senha / conta | 993 |
| APP_WEBSITE | `technical_issue` | reportar erro no app ou site | 994 |
| APP_WEBSITE | `use_app` | ajuda para usar o app | 999 |
| CART | `add_product` | adicionar item ao carrinho | 957 |
| CART | `remove_product` | remover item do carrinho | 993 |
| CONTACT | `customer_service` | falar com o atendimento | 992 |
| CONTACT | `human_agent` | falar com uma pessoa | 994 |
| DELIVERY | `damaged_delivery` | reportar item danificado na entrega | 992 |
| DELIVERY | `delivery_issue` | reportar problema com o pacote | 996 |
| DELIVERY | `delivery_time` | saber a data/prazo de entrega | 920 |
| DELIVERY | `missing_item` | reportar item faltando na entrega | 721 |
| DELIVERY | `shipping_costs` | saber o custo de envio | 974 |
| DELIVERY | `track_delivery` | rastrear a remessa | 996 |
| DELIVERY | `wrong_item` | reportar item errado recebido | 996 |
| FEEDBACK | `submit_feedback` | enviar feedback sobre a loja | 991 |
| FEEDBACK | `submit_product_feedback` | enviar avaliação de um produto | 994 |
| FEEDBACK | `submit_product_idea` | sugerir um produto | 995 |
| ORDER | `cancel_order` | cancelar um pedido | 996 |
| ORDER | `change_order` | alterar um pedido | 961 |
| ORDER | `request_invoice` | baixar/pedir nota fiscal | 1000 |
| ORDER | `track_order` | saber o status de um pedido | 988 |
| PAYMENT | `pay` | fazer um pagamento | 990 |
| PAYMENT | `payment_issue` | reportar problema de pagamento | 996 |
| PAYMENT | `payment_methods` | conhecer as formas de pagamento | 995 |
| PRODUCT | `availability` | ver disponibilidade de um item | 972 |
| PRODUCT | `availability_in_store` | ver disponibilidade em loja física | 756 |
| PRODUCT | `availability_online` | ver disponibilidade online | 993 |
| PRODUCT | `exchange_product` | trocar um produto | 988 |
| PRODUCT | `exchange_product_in_store` | trocar um produto em loja física | 991 |
| PRODUCT | `product_information` | obter informações de produtos | 987 |
| PRODUCT | `product_issue` | reportar defeito em produto | 992 |
| RETURNS | `refund_policy` | conhecer a política de reembolso | 994 |
| RETURNS | `refund_status` | consultar o status de um reembolso | 999 |
| RETURNS | `request_refund` | pedir reembolso | 957 |
| RETURNS | `return_policy` | conhecer a política de devolução | 994 |
| RETURNS | `return_product` | devolver um produto (genérico) | 994 |
| RETURNS | `return_product_in_store` | devolver em loja física | 994 |
| RETURNS | `return_product_online` | devolver pela internet | 993 |
| SALES | `sales_period` | saber o período de promoções | 995 |
| STORE | `store_location` | achar lojas próximas | 924 |
| STORE | `store_opening_hours` | saber o horário de funcionamento | 992 |
| USER | `request_right_to_rectification` | corrigir dados pessoais incorretos | 989 |

As descrições são minhas, a partir do nome da intenção e de exemplos lidos no dataset.
Intenções do escopo central do E-ComShield (rastreamento, troca, devolução, reembolso, reclamação): `track_order`,
`track_delivery`, `exchange_product`, `return_product`, `request_refund`, `refund_status`, `delivery_issue`,
`damaged_delivery`, `wrong_item`, `product_issue`. O mapeamento com o contrato do agente está em
`docs/contrato_agente_backend.md`.

## 3. Distribuição das classes

**Por intenção (46 classes):** mínimo **721** exemplos (`missing_item`), máximo **1.000** (`request_invoice`);
razão máx/mín = **1,39**. Só duas intenções ficam abaixo de 800 (`missing_item` 721 e `availability_in_store` 756);
as outras 44 ficam entre 920 e 1.000. O conjunto é **bem balanceado**; ainda assim uso F1 macro e `stratify` no split.

**Por categoria (13):**

| Categoria | Mensagens | % |
|---|---:|---:|
| RETURNS | 6.925 | 15,4 |
| PRODUCT | 6.679 | 14,9 |
| DELIVERY | 6.595 | 14,7 |
| ACCOUNT | 4.950 | 11,0 |
| ORDER | 3.945 | 8,8 |
| PAYMENT | 2.981 | 6,6 |
| FEEDBACK | 2.980 | 6,6 |
| APP_WEBSITE | 1.993 | 4,4 |
| CONTACT | 1.986 | 4,4 |
| CART | 1.950 | 4,3 |
| STORE | 1.916 | 4,3 |
| SALES | 995 | 2,2 |
| USER | 989 | 2,2 |

A diferença entre categorias vem só de quantas intenções cada uma contém (~1.000 exemplos por intenção).

**Atenção — balanceamento artificial.** No dataset real (Shopzilla) a distribuição é muito concentrada: `Returns`
tem 44.097 dos 85.907 registros (~51%) e `Others`, `App/website` e `Onboarding related` têm menos de 100 cada. O
Bitext é sintético, gerado por templates; um modelo treinado só nele pode ir muito bem no teste e pior com mensagens
reais. Por isso o plano de T2 prevê checar o modelo contra o Shopzilla (ver `docs/planejamento-t2.md`).

## 4. Ambiguidades entre classes

Várias intenções têm significado próximo e a diferença está em um detalhe da frase. São os pares em que espero mais
confusão e que vou olhar primeiro na matriz de confusão:

| Grupo | Intenções próximas | Por que se confundem |
|---|---|---|
| Devolução | `return_product`, `return_product_online`, `return_product_in_store` | Mesma ação; só muda o canal (online / loja). Mensagens sem "online" ou "store" podem ser confundidas com o genérico |
| Troca | `exchange_product`, `exchange_product_in_store` | Mesmo caso: depende de "in store" aparecer ou não |
| Reembolso | `request_refund`, `refund_status`, `refund_policy` | Mesmo vocabulário ("refund"); muda se é pedir, acompanhar ou conhecer a regra |
| Disponibilidade | `availability`, `availability_online`, `availability_in_store` | Mesmo canal de distinção |
| Rastreio | `track_order`, `track_delivery` | "onde está meu pedido" vs. "onde está a remessa" |
| Problema na entrega | `delivery_issue`, `damaged_delivery`, `missing_item`, `wrong_item` | Todas são "recebi algo errado" em graus diferentes |
| Feedback | `submit_feedback`, `submit_product_feedback`, `submit_product_idea` | Todas são "quero enviar uma opinião" |
| Contato | `customer_service`, `human_agent` | Ambas pedem uma pessoa |
| Política vs. ação | `return_policy` / `return_product`, `refund_policy` / `request_refund` | Perguntar a regra é diferente de executar a ação |

Possível ruído de rótulo: ao ler um exemplo de `return_product_in_store`, a mensagem era
"could you give me information about an fucking item in store?", que a leitura direta associaria a informação de
produto. Foi um exemplo isolado que vi, não uma medida; em T2 vou olhar os erros do modelo para ver se isso se repete.

## 5. Por que regressão linear não serve para este problema

No notebook `agent/03_regressao_linear.ipynb` a regressão linear foi aplicada a um alvo **numérico** (nº de palavras):
R² ≈ 0,56 no teste. Isso mostra o que ela faz bem, mas o problema do E-ComShield é outro:

1. **O alvo é categórico nominal, não ordinal.** "refund_status" não é maior nem menor que "track_order". Codificar as
   46 intenções como 1…46 impõe uma ordem e uma distância que não existem.
2. **A saída não é uma classe.** A regressão devolve um número contínuo e ilimitado (pode prever 47,3 ou −2), sem
   regra natural para converter em uma das 46 intenções.
3. **Não produz probabilidades.** O agente precisa de uma confiança por intenção (para decidir quando escalar a um
   humano — `human_agent`). Regressão logística e SVM calibrado dão isso; OLS não.
4. **Pressupostos do OLS não valem.** Erros com variância constante e distribuição normal não fazem sentido para um
   rótulo discreto; a perda quadrática não é a adequada à classificação.
5. **Texto é alta dimensionalidade e esparso.** O vocabulário vira milhares de colunas TF-IDF; logística e SVM linear
   com perda de classificação e regularização lidam bem com isso.

## 6. Por que aprendizado supervisionado

- Existem **rótulos confiáveis** (a coluna `intent`), ~1.000 exemplos por classe: é o cenário típico de aprendizado
  supervisionado.
- Regras manuais ou estatística descritiva (palavras-chave, contagens) quebrariam com variações linguísticas que o
  próprio dataset documenta (colóquio, ofensas, erros de digitação, coordenação). No dataset aparecem
  "assixtance", "prodcut", "haev", "ur" e palavrões no meio da frase; um modelo treinado aprende essas variações
  a partir dos dados.
- As ambiguidades da seção 4 dependem de combinações de palavras ("return" + "online" vs. "in store"), o que um
  classificador com n-gramas captura e regras simples não.
- Um sanity check informal que rodei (TF-IDF 1–2-gramas + regressão logística / SVM linear, split 80/20 estratificado)
  deu cerca de 98,6% / 99,1% de acurácia e F1 macro semelhante no Bitext. Isso **não** é o resultado de T2 (sem
  validação cruzada nem ajuste); serve só para mostrar que a tarefa é aprendível com esses dados — e, justamente
  pelo valor tão alto, reforça o alerta de que o dataset sintético é fácil demais e precisa de validação externa.

## Uso de IA

Documento redigido com apoio de IA (Claude). As contagens e a distribuição foram calculadas a partir dos CSVs do
projeto e conferidas por mim; o sanity check de acurácia foi executado localmente. As descrições das classes e a
tabela de ambiguidades são interpretações minhas a partir dos nomes e dos exemplos do dataset.
