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

## 9. Conclusão

O scan do OWASP ZAP permitiu identificar configurações relacionadas principalmente à Content Security Policy e aos recursos externos utilizados pelo Swagger UI.

As configurações relacionadas à CSP foram corrigidas, incluindo a remoção de `unsafe-inline` das diretivas `script-src` e `style-src` e a inclusão explícita da diretiva `form-action`.

Os alertas relacionados ao carregamento de recursos externos pelo Swagger UI foram classificados como riscos residuais, pois estão restritos à interface de documentação da API e não à lógica dos endpoints de negócio.

As correções foram validadas por meio de novo scan e pela inspeção direta dos headers HTTP retornados pela aplicação.
