from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)

# Testes de segurança
def test_pedido_exige_autenticacao():
    response = client.get("/orders/1")

    assert response.status_code == 401

# Teste para verificar se um usuário não pode acessar pedidos de outro usuário
def test_usuario_nao_pode_acessar_pedido_de_outro_usuario():
    login_response = client.post(
        "/auth/token",
        data={
            "username": "user1",
            "password": "user123",
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    response = client.get(
        "/orders/1",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 403

# Teste para verificar se a rota de previsão rejeita campos extras
def test_predict_rejeita_campo_extra():
    login_response = client.post(
        "/auth/token",
        data={
            "username": "user1",
            "password": "user123",
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

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