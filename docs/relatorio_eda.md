# Relatório de EDA — E-ComShield

Esse documento reúne, de forma estruturada, a análise exploratória que eu fiz nos dois datasets do
projeto ao longo do TP1 e do TP2. O código completo, com todas as células executadas, está em
`agent/01_eda.ipynb`; aqui eu organizo os resultados em formato de relatório, focando no que interpretei
a partir dos dados.

## Problema

O E-ComShield é um agente de IA que vai receber mensagens de clientes de e-commerce e precisa entender
a intenção por trás de cada mensagem (por exemplo: rastrear um pedido, pedir reembolso, reclamar de um
produto danificado) para poder encaminhar o atendimento corretamente. Antes de treinar ou desenhar
qualquer lógica de classificação, eu precisava entender dois pontos: (1) como são as mensagens e
intenções que esse agente vai precisar reconhecer, e (2) como se comporta, na prática, o atendimento de
e-commerce real — que tipo de problema aparece com mais frequência, e se existe alguma relação entre o
tipo de problema, o valor do pedido e a satisfação do cliente. Essas duas perguntas guiaram a escolha
dos dois datasets e toda a análise.

## Dados

Usei dois datasets complementares, documentados em detalhe em `docs/escolha_dataset.md`:

**Bitext Retail eCommerce LLM Chatbot Training Dataset** — sintético, gerado pela Bitext
(licença CDLA-Sharing-1.0), com 44.884 linhas e 5 colunas (`instruction`, `intent`, `category`, `tags`,
`response`). Tem 13 categorias e 46 intenções, bem balanceado (cerca de 1.000 exemplos por intenção),
sem valores ausentes nem duplicatas. Esse dataset é a base de referência para o vocabulário de intenções
que o agente vai precisar reconhecer.

**Customer_support_data.csv ("Shopzilla")** — um dataset real de atendimento de e-commerce, com 85.907
linhas e 19 colunas (após a limpeza), incluindo categoria e subcategoria do chamado, valor do pedido
(`Item_price`), nota de satisfação (`CSAT Score` de 1 a 5) e timestamps de abertura/resposta do chamado.
Esse dataset é o que me deu uma visão realista de como o atendimento de e-commerce se comporta na
prática, algo que o Bitext (sendo sintético) não conseguiria oferecer.

As decisões de limpeza aplicadas ao Shopzilla (conversão de datas, remoção de coluna vazia, sinalização
de campos gerados via Faker) estão documentadas e automatizadas em `agent/02_limpeza.py`.

## Análise

A análise seguiu, resumidamente, esses passos:

1. **Perfil geral** — shape, tipos de dado, valores ausentes e duplicatas dos dois datasets.
2. **Distribuição de categorias e intenções** — como os chamados/mensagens se distribuem entre os
   diferentes tipos de problema, em ambos os datasets.
3. **Visualizações exploratórias** — histograma do CSAT, boxplot do valor dos pedidos, gráficos de
   barra das categorias mais frequentes.
4. **Aprofundamento estatístico (TP2)** — heatmap de correlação entre valor do pedido, CSAT e tempo de
   resposta do atendimento; scatter plots dessas mesmas relações; e um teste de hipótese formal
   (Mann-Whitney U, via SciPy) para validar estatisticamente uma das hipóteses formuladas no TP1.

Para o teste de hipótese, retomei a **Hipótese 2** do TP1 ("a satisfação não segue a lógica óbvia de
categoria com mais atrito = nota mais baixa"), comparando a distribuição de CSAT Score da categoria
`Returns` (a de maior volume) contra a das demais categorias juntas. Antes de escolher o teste, rodei um
teste de Shapiro-Wilk para checar normalidade — o resultado (p ≈ 1,5×10⁻⁷⁶) confirmou que a distribuição
não é normal, o que já era esperado por se tratar de uma nota discreta e concentrada nos extremos. Por
isso usei o Mann-Whitney U, que não exige essa premissa.

## Insights principais

- **`Returns` domina o volume de chamados**, mas isso não se traduz em pior satisfação — pelo contrário.
- O teste de Mann-Whitney U deu um p-valor extremamente baixo (p ≈ 1,7×10⁻¹⁰⁷), ou seja, a diferença de
  CSAT entre `Returns` (média 4,35) e as demais categorias (média 4,13) é estatisticamente significativa
  — só que na direção **contrária** à intuição inicial: `Returns` tem satisfação **maior**, não menor.
  Isso reforça a leitura do TP1: volume de chamados não é um bom preditor de insatisfação nesse dataset.
- **Nem valor do pedido, nem tempo de resposta correlacionam de forma relevante com a nota de CSAT** — o
  heatmap de correlação mostrou valores próximos de zero entre as três variáveis numéricas disponíveis
  (`Item_price`, `CSAT Score`, `response_time_hours`), e os scatter plots confirmam visualmente essa
  ausência de padrão. Isso sugere que o que mais pesa na satisfação do cliente provavelmente é o
  desfecho do atendimento (se o problema foi resolvido ou não), e não quanto o cliente pagou ou quanto
  tempo esperou — algo que esse dataset não tem como capturar diretamente.
- Os pedidos de maior valor (top 5%) concentram proporcionalmente mais reclamações relacionadas a
  atraso/status do pedido do que o restante da base (Hipótese 3 do TP1), reforçando que pedidos caros
  tendem a gerar mais ansiedade/acompanhamento por parte do cliente.

## Limitações

- A coluna de tempo de resposta (`response_time_hours`) só pôde ser calculada para cerca de 37% das
  linhas do Shopzilla (31.633 de 85.907), já que boa parte dos registros não tem as duas datas de
  abertura/resposta preenchidas de forma válida. Os resultados envolvendo essa variável devem ser lidos
  com essa ressalva.
- O dataset Shopzilla tem campos claramente gerados via Faker (`Agent_name`, `Supervisor`, `Manager`,
  `Customer_City`), o que é esperado por questão de anonimização, mas significa que qualquer análise
  que envolvesse esses campos não teria valor real (por isso eu não os usei em nenhuma correlação).
- Com uma amostra tão grande (85 mil+ linhas), testes de hipótese tendem a apontar significância
  estatística mesmo para diferenças pequenas — por isso dei atenção tanto ao p-valor quanto ao tamanho e
  à direção da diferença entre os grupos, não só ao "p < 0,05" isoladamente.
- O Bitext e o Shopzilla não compartilham a mesma taxonomia de categorias, então as intenções mapeadas a
  partir do Bitext (documentadas em `docs/contrato_agente_backend.md`) ainda não foram validadas contra
  dados reais de mensagens de clientes — só contra os metadados de categoria/subcategoria do Shopzilla.

## Próximos passos

- Integrar o classificador de intenção (treinado com o Bitext) ao endpoint `/predict` do backend.
- Validar, com uma amostra de mensagens reais (se disponível), se a taxonomia de intenções definida no
  contrato agente↔backend cobre bem os casos reais de atendimento.
- Investigar outras variáveis que possam explicar a satisfação do cliente além das disponíveis nesse
  dataset (por exemplo, se o problema foi de fato resolvido no primeiro contato).
- Definir o threshold de confiança do classificador para decidir quando escalar o atendimento para um
  humano, com base na distribuição de confiança observada durante o treinamento.

## Uso de IA

Conforme a política "Sinal Verde 🟢" do enunciado, este relatório foi escrito com apoio de ferramentas de
IA (Claude, da Anthropic), a partir dos resultados já obtidos e interpretados no notebook `agent/01_eda.ipynb`.
A IA auxiliou na estruturação do texto nas seções exigidas pela Tarefa 7, na escolha do teste estatístico
adequado (Mann-Whitney U, após verificação de normalidade com Shapiro-Wilk) e na redação das
interpretações, a partir das decisões e leituras feitas por mim durante a análise.
