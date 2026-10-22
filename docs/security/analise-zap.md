# Análise dos resultados do OWASP ZAP

## 1. Objetivo

Foi realizada uma análise de segurança da API E-ComShield utilizando o OWASP ZAP, com o objetivo de identificar vulnerabilidades e configurações de segurança inadequadas na aplicação.

O teste foi executado contra a interface de documentação da API em ambiente local:

```text
http://127.0.0.1:8000/docs
```

A análise foi realizada utilizando um **scan passivo**, sem exploração ativa dos endpoints.

Os alertas identificados foram analisados individualmente e classificados conforme o tratamento aplicado.

---

## 2. Resultados

| Alerta                                            | Severidade        | Tratamento                       |
| ------------------------------------------------- | ----------------- | -------------------------------- |
| CSP: Failure to Define Directive with No Fallback | Médio             | Corrigido                        |
| CSP: script-src unsafe-inline                     | Médio             | Corrigido                        |
| CSP: style-src unsafe-inline                      | Médio             | Corrigido                        |
| Sub Resource Integrity Attribute Missing          | Médio             | Risco residual aceito            |
| Cross-Domain JavaScript Source File Inclusion     | Médio             | Risco residual aceito            |
| Alertas de baixa severidade/informativos          | Baixa/Informativo | Fora do escopo obrigatório do TP |

---

## 3. CSP: Failure to Define Directive with No Fallback

### Detecção

O OWASP ZAP identificou uma diretiva de segurança da Content Security Policy que não possuía uma definição explícita.

O problema estava relacionado à ausência da diretiva `form-action`.

### Impacto

A diretiva `form-action` controla para quais destinos os formulários HTML podem enviar seus dados.

Quando não definida explicitamente, o comportamento pode depender de outras diretivas da política, reduzindo a granularidade das restrições aplicadas.

### Correção

Foi adicionada a seguinte diretiva à Content Security Policy:

```text
form-action 'self';
```

Com isso, os formulários ficam restritos à própria origem da aplicação.

### Resultado

Após a alteração, o scan foi executado novamente e o alerta deixou de ser identificado pelo OWASP ZAP.

**Status: Corrigido.**

---

## 4. CSP: script-src unsafe-inline

### Detecção

O OWASP ZAP identificou a utilização de:

```text
script-src ... 'unsafe-inline'
```

na Content Security Policy.

A utilização de `unsafe-inline` permite a execução de scripts JavaScript inseridos diretamente no documento, reduzindo a efetividade da proteção contra determinadas formas de Cross-Site Scripting (XSS).

### Impacto

Caso exista uma vulnerabilidade de injeção de código na aplicação, uma política contendo `unsafe-inline` pode permitir a execução de determinados scripts que seriam bloqueados por uma política mais restritiva.

### Correção

Inicialmente, o `unsafe-inline` estava sendo utilizado para permitir o funcionamento da interface Swagger.

Foi realizada uma alteração para utilizar um hash criptográfico específico para o script inline autorizado:

```text
'sha256-QOOQu4W1oxGqd2nbXbxiA1Di6OHQOLQD+o+G9oWL8YY='
```

A diretiva passou a utilizar:

```text
script-src 'self' https://cdn.jsdelivr.net 'sha256-QOOQu4W1oxGqd2nbXbxiA1Di6OHQOLQD+o+G9oWL8YY=';
```

Dessa forma, o script inline específico pode ser executado sem liberar genericamente todos os scripts inline.

### Validação

O endpoint `/docs` continuou funcionando após a alteração.

A política também foi validada diretamente no header HTTP da aplicação.

**Status: Corrigido.**

---

## 5. CSP: style-src unsafe-inline

### Detecção

O OWASP ZAP identificou a utilização de:

```text
style-src ... 'unsafe-inline'
```

na Content Security Policy.

Essa configuração permite estilos inline, reduzindo a restrição aplicada pelo CSP.

### Impacto

Uma política que permite estilos inline possui uma superfície de controle menor do que uma política que restringe as fontes de estilos explicitamente.

### Correção

O `unsafe-inline` foi removido da diretiva `style-src`.

A política passou a utilizar:

```text
style-src 'self' https://cdn.jsdelivr.net;
```

### Validação

A interface Swagger continuou funcionando normalmente após a alteração.

O header HTTP retornado pela API foi validado e confirmou a remoção de `unsafe-inline` da diretiva `style-src`.

O novo scan do OWASP ZAP deixou de identificar o alerta.

**Status: Corrigido.**

---

## 6. Sub Resource Integrity Attribute Missing

### Detecção

O OWASP ZAP identificou um recurso externo carregado pelo Swagger UI sem o atributo `integrity`.

O recurso identificado foi:

```html
<link type="text/css"
      rel="stylesheet"
      href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css">
```

### Impacto

O Subresource Integrity (SRI) permite que o navegador verifique se o conteúdo de um recurso externo corresponde ao conteúdo esperado.

Sem essa validação, uma alteração maliciosa no recurso disponibilizado pelo servidor externo poderia ser carregada pela aplicação.

### Tratamento

O recurso identificado pertence à interface de documentação Swagger disponibilizada pela rota:

```text
/docs
```

Não faz parte da lógica dos endpoints de negócio da API.

A correção exigiria customizar a implementação da documentação Swagger para fixar uma versão do recurso e fornecer seu respectivo hash de integridade.

Para o escopo deste projeto, o alerta foi tratado como **risco residual aceito**, considerando que está restrito à interface de documentação utilizada no ambiente de desenvolvimento.

Além disso, a aplicação utiliza uma Content Security Policy que restringe explicitamente as origens permitidas.

**Status: Risco residual aceito.**

---

## 7. Cross-Domain JavaScript Source File Inclusion

### Detecção

O OWASP ZAP identificou um arquivo JavaScript carregado de um domínio externo:

```html
<script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
```

### Impacto

A utilização de JavaScript hospedado em domínio externo introduz uma dependência na disponibilidade e integridade desse recurso.

Caso o conteúdo disponibilizado pela origem externa fosse alterado de forma maliciosa, o código poderia ser executado na interface que o carrega.

### Tratamento

O recurso pertence à interface Swagger da rota:

```text
/docs
```

e não aos endpoints de negócio da API.

A aplicação restringe as origens permitidas por meio da Content Security Policy:

```text
script-src 'self' https://cdn.jsdelivr.net 'sha256-QOOQu4W1oxGqd2nbXbxiA1Di6OHQOLQD+o+G9oWL8YY=';
```

A remoção completa da dependência exigiria hospedar e controlar localmente os arquivos do Swagger UI ou realizar uma customização equivalente.

Para o escopo do projeto, o alerta foi tratado como **risco residual aceito**, limitado à interface de documentação.

**Status: Risco residual aceito.**

---

## 8. Content Security Policy final

Após as correções, a aplicação passou a utilizar a seguinte política:

```text
default-src 'self';
script-src 'self' https://cdn.jsdelivr.net 'sha256-QOOQu4W1oxGqd2nbXbxiA1Di6OHQOLQD+o+G9oWL8YY=';
style-src 'self' https://cdn.jsdelivr.net;
img-src 'self' data: https://fastapi.tiangolo.com;
connect-src 'self' https://cdn.jsdelivr.net;
form-action 'self';
frame-ancestors 'none'
```

A política foi validada diretamente no header HTTP da aplicação.

---

## 9. Conclusão do TP2

O scan do OWASP ZAP permitiu identificar configurações relacionadas principalmente à Content Security Policy e aos recursos externos utilizados pelo Swagger UI.

As configurações relacionadas à CSP foram corrigidas, incluindo a remoção de `unsafe-inline` das diretivas `script-src` e `style-src` e a inclusão explícita da diretiva `form-action`.

Os alertas relacionados ao carregamento de recursos externos pelo Swagger UI foram classificados como riscos residuais, pois estão restritos à interface de documentação da API e não à lógica dos endpoints de negócio.

As correções foram validadas por meio de novo scan e pela inspeção direta dos headers HTTP retornados pela aplicação.

---

## 10. Reavaliação de segurança — TP3

### 10.1. Objetivo

Durante o TP3, foi realizada uma nova etapa de auditoria de segurança da API E-ComShield, com o objetivo de reavaliar os findings identificados no TP2 e verificar a eficácia das medidas corretivas implementadas.

A principal mudança consistiu na substituição do carregamento externo dos recursos da interface Swagger UI por arquivos estáticos hospedados localmente no backend FastAPI.

Essa alteração teve como objetivo reduzir a dependência de recursos de terceiros e tratar os alertas relacionados à integridade de sub-recursos e à inclusão de JavaScript externo.

### 10.2. Alterações implementadas

A documentação Swagger UI passou a utilizar recursos locais disponibilizados pela aplicação:

- `/static/swagger/swagger-ui.css`
- `/static/swagger/swagger-ui-bundle.js`
- `/static/swagger/swagger-init.js`

A rota `/docs` foi personalizada para utilizar esses arquivos, mantendo o acesso à documentação interativa da API.

A Content Security Policy também foi modificada para restringir o carregamento de scripts à própria origem da aplicação:

```text
script-src 'self';
```

Para preservar a compatibilidade da interface Swagger, a diretiva de estilos ficou configurada como:

```text
style-src 'self' 'unsafe-inline';
```

Essa permissão residual deve continuar sendo monitorada e avaliada em futuras melhorias de segurança.

### 10.3. Reavaliação do finding Sub Resource Integrity Attribute Missing

**Severidade anterior:** Média

**Situação no TP2:** Risco residual aceito.

**Medida adotada no TP3:** Hospedagem local dos recursos Swagger UI.

Anteriormente, a interface `/docs` carregava arquivos CSS e JavaScript a partir do CDN jsDelivr, sem fornecer atributos de integridade SRI.

A nova implementação elimina essa dependência externa específica, utilizando arquivos estáticos servidos pelo próprio backend.

No novo scan informado, o alerta não voltou a ser identificado.

**Status: Corrigido na configuração analisada, sujeito à confirmação pelo relatório exportado.**

### 10.4. Reavaliação do finding Cross-Domain JavaScript Source File Inclusion

**Situação no TP2:** Risco residual aceito.

**Medida adotada no TP3:** Remoção do carregamento externo do JavaScript utilizado pelo Swagger UI.

A nova configuração utiliza o seguinte recurso local:

```text
/static/swagger/swagger-ui-bundle.js
```

Essa modificação elimina a dependência do JavaScript hospedado externamente pelo jsDelivr na interface `/docs`.

O alerta não foi identificado no novo scan informado.

**Status: Corrigido na configuração analisada, sujeito à confirmação pelo relatório exportado.**

---

## 11. Resultados do novo scan OWASP ZAP

Após as alterações, foi realizada uma nova análise passiva no ambiente local.

De acordo com os resultados observados, permaneceram os seguintes alertas:

| Alerta | Severidade | Tratamento |
|---|---|---|
| Modern Web Application | Informativo | Nenhuma correção necessária |
| Timestamp Disclosure — Unix | Baixa | Aceitação condicionada à análise da evidência |

Não foram relatados findings de severidade Medium ou High no novo scan.

### 11.1. Evidência da auditoria final

![Figura 5 - Resultado final do scan de segurança realizado com o OWASP ZAP](./Figura%205%20-%20Resultado%20final%20do%20scan%20de%20segurança%20realizado%20com%20o%20OWASP%20ZAP.png)

**Figura 5 —** Resultado da nova análise de segurança realizada com o OWASP ZAP durante o TP3.

### 11.2. Modern Web Application

O OWASP ZAP identificou que a aplicação utiliza características de uma interface web moderna.

Esse alerta possui caráter informativo e não representa, isoladamente, uma vulnerabilidade de segurança.

![Figura 6 - Alerta informativo Modern Web Application identificado pelo OWASP ZAP](./Figura%206%20-%20Alerta%20informativo%20Modern%20Web%20Application%20identificado%20pelo%20OWASP%20ZAP.png)

**Status: Informativo — nenhuma correção necessária.**

### 11.3. Timestamp Disclosure — Unix

O OWASP ZAP identificou um valor numérico interpretado como timestamp Unix.

**Recurso identificado:**

```text
/static/swagger/swagger-ui-bundle.js
```

**Evidência:**

```text
1518500249
```

A ocorrência foi identificada dentro de um arquivo JavaScript estático pertencente à biblioteca Swagger UI.

A presença desse valor não demonstra, por si só, exposição de dados internos ou informações sensíveis do E-ComShield.

Como se trata de uma dependência de terceiros, não é recomendável alterar diretamente o arquivo distribuído apenas para eliminar o número identificado.

A aceitação do risco depende de confirmar que o valor não representa informação sensível da aplicação.

![Figura 7 - Alerta de divulgação de timestamp Unix em recurso estático do Swagger UI](./Figura%207%20-%20Alerta%20de%20divulgação%20de%20timestamp%20Unix%20em%20recurso%20estático%20do%20Swagger%20UI.png)

**Status: Baixo risco — análise para aceitação documentada.**

---

## 12. Comparação entre TP2 e TP3

A evolução da auditoria evidencia a adoção de medidas de segurança adicionais na interface de documentação da API.

No TP2, as principais ações envolveram a configuração da Content Security Policy, a correção de diretivas ausentes e a restrição da execução de scripts inline.

No TP3, o foco foi a eliminação da dependência de recursos externos utilizados pela documentação Swagger UI.

Essa mudança permitiu tratar os findings anteriormente aceitos relacionados a recursos externos.

Os resultados relatados da nova análise indicam ausência de alertas Medium e High no escopo inspecionado.

A ausência de alertas no scan passivo não constitui garantia de inexistência de vulnerabilidades, sendo necessária a continuidade das validações por testes automatizados e pelo pentest previsto para o projeto.

---

## 13. Conclusão da reavaliação

A auditoria realizada durante o TP3 demonstra uma evolução na postura de segurança do E-ComShield.

A substituição dos recursos externos do Swagger UI por arquivos locais reduziu a dependência de serviços de terceiros e tratou os alertas anteriormente identificados relativos à integridade e inclusão de recursos externos.

Os alertas residuais relatados possuem severidade baixa ou caráter informativo, não tendo sido identificados novos findings Medium ou High no escopo do scan realizado.

O relatório atualizado do OWASP ZAP deverá ser mantido no repositório como evidência dessa etapa de validação.

A verificação completa da prontidão para pentest, incluindo autenticação, autorização, testes automatizados, documentação OpenAPI e dados de teste, será registrada separadamente em `docs/security/auditoria-final.md`.
