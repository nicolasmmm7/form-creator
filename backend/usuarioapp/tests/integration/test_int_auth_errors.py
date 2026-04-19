import pytest
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_firebase_auth_sin_token():
    client = APIClient()

    response = client.post("/api/auth/firebase/", {}, format="json")

    print("SIN TOKEN:", response.status_code, response.data)

    assert response.status_code == 401
    assert "error" in response.data


@pytest.mark.django_db
def test_firebase_auth_token_invalido():
    client = APIClient()

    response = client.post(
        "/api/auth/firebase/",
        {},
        format="json",
        HTTP_AUTHORIZATION="Bearer token-falso"
    )

    print("TOKEN INVALIDO:", response.status_code, response.data)

    assert response.status_code in [401, 403]