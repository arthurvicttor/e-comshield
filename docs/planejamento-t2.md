# Planejamento Técnico — Trimestre 2 (T2)

## 1. Objetivo

Este documento apresenta o planejamento técnico para a próxima etapa do E-ComShield, contemplando o desenvolvimento de um modelo supervisionado de classificação de intenções e a preparação para a avaliação adversária de segurança.

## 2. Modelo candidato

O modelo inicialmente escolhido é a **Regressão Logística**, aplicada à classificação multiclasse de mensagens de atendimento.

O objetivo é prever a intenção do cliente a partir do texto fornecido, como solicitações de rastreamento, troca, devolução, reembolso e problemas com produtos.

A escolha da Regressão Logística se justifica por sua eficiência em problemas de classificação de texto, compatibilidade com representações vetoriais esparsas e capacidade de estabelecer uma baseline interpretável.

Como alternativa experimental, poderá ser avaliado o modelo LinearSVC.

## 3. Estratégia de feature engineering

As mensagens serão transformadas em características numéricas por meio de TF-IDF (Term Frequency–Inverse Document Frequency).

O pipeline previsto contempla:

1. Tratamento de textos vazios e normalização textual.
2. Separação estratificada entre treino e teste.
3. Vetorização TF-IDF, ajustada exclusivamente no conjunto de treinamento.
4. Treinamento da Regressão Logística.
5. Avaliação no conjunto de teste não utilizado no treinamento.

A abordagem permite preservar informações relevantes sobre os termos utilizados pelos clientes, reduzindo a influência de palavras muito frequentes.

## 4. Dataset

Será utilizado inicialmente o dataset Bitext Retail eCommerce LLM Chatbot Training Dataset, que contém mensagens rotuladas por intenção.

O dataset Shopzilla será utilizado como referência para análise de distribuição das categorias reais e para avaliar possibilidades de generalização, desde que exista um mapeamento adequado entre suas categorias e as intenções do Bitext.

## 5. Estratégia de avaliação

O conjunto de dados será dividido em 80% para treinamento e 20% para teste, preservando a distribuição das classes.

As métricas previstas são:

- Accuracy.
- Precision.
- Recall.
- F1-score macro.
- Matriz de confusão.

O F1-macro será especialmente relevante para avaliar o desempenho entre diferentes classes, sem privilegiar apenas as mais frequentes.

## 6. Planejamento da avaliação adversária

No Trimestre 2, a equipe também realizará uma avaliação de segurança da API de outra dupla, conforme a organização da disciplina.

**Colega ou dupla adversária:** Pendente de identificação.

**Projeto adversário:** Pendente de identificação.

**URL/IP da API alvo:** Pendente de disponibilização.

**Escopo previsto:** Testes de segurança exclusivamente no ambiente autorizado para o exercício acadêmico.

Os testes deverão considerar autenticação, autorização, validação de entradas e exposição indevida de recursos, respeitando as restrições estabelecidas pelo professor.

## 7. Próximos passos

O trabalho do T2 seguirá com o treinamento e avaliação do classificador de intenções, sua posterior integração ao backend e a execução da avaliação adversária no ambiente disponibilizado pela dupla correspondente.
