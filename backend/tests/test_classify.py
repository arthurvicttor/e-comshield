
from fastapi.testclient import TestClient

from app.main import app
from app.security.dependencies import get_current_user
from app.api.routes import classify as classify_routes


client = TestClient(app)


def fake_user():
    return "pentest_user_a"


def test_classify_requires_auth():
    response = client.post(
        "/classify",
        json={"text": "Where is my order?"},
    )

    assert response.status_code == 401


def test_classify_rejects_extra_fields():
    app.dependency_overrides[get_current_user] = fake_user

    try:
        response = client.post(
            "/classify",
            json={
                "text": "Where is my order?",
                "is_admin": True,
            },
        )

        assert response.status_code == 422
    finally:
        app.dependency_overrides.clear()


def test_classify_returns_prediction(monkeypatch):
    app.dependency_overrides[get_current_user] = fake_user

    def fake_prediction(text):
        return {
            "intent": "track_order",
            "confidence": 0.96,
            "model_version": "svm_linear",
        }

    monkeypatch.setattr(
        classify_routes,
        "predict_intent",
        fake_prediction,
    )

    try:
        response = client.post(
            "/classify",
            json={"text": "Where is my order?"},
        )

        assert response.status_code == 200
        assert response.json()["intent"] == "track_order"
        assert response.json()["confidence"] == 0.96
    finally:
        app.dependency_overrides.clear()

