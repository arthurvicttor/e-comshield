# Testes de Segurança - E-ComShield

## 1. Objetivo

Foram implementados testes automatizados de segurança utilizando **Pytest**, com o objetivo de validar controles de autenticação, autorização e validação de entrada da API E-ComShield.

Os testes foram desenvolvidos para verificar três controles de segurança:

* proteção de recursos sem autenticação;
* controle de acesso baseado na propriedade do recurso (BOLA);
* rejeição de campos não permitidos nas requisições.

Os testes estão localizados em:

```text
backend/tests/test_security.py
```

---

## 2. Testes implementados

### 2.1 Acesso a recurso sem autenticação

O primeiro teste verifica se um usuário consegue acessar um pedido sem fornecer um token de autenticação.

Requisição utilizada:

```http
GET /orders/1
```

Sem o header:

```http
Authorization: Bearer <token>
```

O comportamento esperado é que a API rejeite a requisição.

**Resultado esperado:**

```text
HTTP 401 Unauthorized
```

Esse teste valida que o endpoint protegido não pode ser acessado sem autenticação.

**Status: Aprovado.**

---

### 2.2 Acesso a recurso pertencente a outro usuário

O segundo teste verifica o controle de autorização baseado na propriedade do recurso.

Primeiramente, o teste autentica o usuário `user1` e obtém um token JWT.

Em seguida, tenta acessar o pedido de outro usuário:

```http
GET /orders/1
```

O pedido pertence ao usuário `admin`, enquanto o token utilizado pertence ao `user1`.

O comportamento esperado é a rejeição da requisição.

**Resultado esperado:**

```text
HTTP 403 Forbidden
```

Esse teste valida a proteção contra **Broken Object Level Authorization (BOLA)**, garantindo que um usuário autenticado não consiga acessar recursos pertencentes a outro usuário apenas alterando o identificador do recurso.

**Status: Aprovado.**

---

### 2.3 Rejeição de campos adicionais na requisição

O terceiro teste verifica a validação dos dados recebidos pelo endpoint `/predict`.

A requisição contém o campo esperado:

```json
{
  "message": "Quero devolver meu pedido"
}
```

e também um campo adicional não definido pelo schema:

```json
{
  "message": "Quero devolver meu pedido",
  "is_admin": true
}
```

O schema `PredictRequest` utiliza:

```python
model_config = ConfigDict(extra="forbid")
```

Dessa forma, campos que não foram previamente definidos no modelo são rejeitados.

**Resultado esperado:**

```text
HTTP 422 Unprocessable Entity
```

Esse controle reduz o risco de entrada de parâmetros inesperados na API e garante que apenas os campos definidos pelo contrato sejam aceitos.

**Status: Aprovado.**

---

## 3. Execução da suíte

Os testes foram executados utilizando:

```bash
pytest tests/
```

Resultado obtido:

```text
collected 3 items

tests\test_security.py ... [100%]

3 passed, 2 warnings in 3.67s
```

Os três testes foram executados com sucesso.

Os dois avisos apresentados durante a execução são `DeprecationWarning` provenientes de dependências utilizadas pelo projeto (`pytest_asyncio` e `python-jose`) e não representam falhas nos testes de segurança implementados.

---

## 4. Resultado

| Teste                            | Controle validado    | Resultado |
| -------------------------------- | -------------------- | --------- |
| Acesso sem token                 | Autenticação         | Aprovado  |
| Acesso a pedido de outro usuário | BOLA / autorização   | Aprovado  |
| Campo adicional no `/predict`    | Validação de entrada | Aprovado  |

A suíte de testes confirma, no cenário avaliado, o funcionamento dos controles de autenticação, autorização e validação de entrada implementados na API.

## 5. Conclusão

Os testes automatizados demonstraram que os principais controles de segurança implementados para o escopo do TP2 estão funcionando conforme esperado.

A proteção contra acesso não autenticado foi validada com resposta `401`, o controle de propriedade dos recursos foi validado com resposta `403` e a política de rejeição de campos adicionais foi validada com resposta `422`.

A execução completa da suíte apresentou **3 testes aprovados**, sem falhas.
