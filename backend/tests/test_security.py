
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def obter_token():
    """Autentica o usuário de teste e retorna seu JWT."""
    response = client.post(
        "/auth/token",
        data={
            "username": "user1",
            "password": "user123",
        },
    )

    assert response.status_code == 200
    return response.json()["access_token"]


# Autenticação obrigatória
def test_pedido_exige_autenticacao():
    response = client.get("/orders/1")

    assert response.status_code == 401


# Proteção contra BOLA/IDOR
def test_usuario_nao_pode_acessar_pedido_de_outro_usuario():
    token = obter_token()

    response = client.get(
        "/orders/1",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 403


# Validação de campos extras
def test_predict_rejeita_campo_extra():
    token = obter_token()

    response = client.post(
        "/predict",
        headers={
            "Authorization": f"Bearer {token}",
        },
        json={
            "message": "Quero devolver meu pedido",
            "is_admin": True,
        },
    )

    assert response.status_code == 422


# Rejeição de credenciais inválidas
def test_login_rejeita_senha_incorreta():
    response = client.post(
        "/auth/token",
        data={
            "username": "user1",
            "password": "senha_incorreta",
        },
    )

    assert response.status_code == 401


# Rate limiting no endpoint de autenticação
def test_login_aplica_rate_limiting():
    responses = []

    for _ in range(7):
        response = client.post(
            "/auth/token",
            data={
                "username": "user1",
                "password": "senha_incorreta",
            },
        )

        responses.append(response.status_code)

    assert 429 in responses
