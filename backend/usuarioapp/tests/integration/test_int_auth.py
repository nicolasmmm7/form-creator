import pytest
from rest_framework.test import APIClient
from unittest.mock import patch

@pytest.mark.django_db
@patch("firebase_admin.auth.verify_id_token")
def test_sync_firebase_user(mock_verify):
    client = APIClient()

    mock_verify.return_value = {
        "uid": "123456",
        "email": "test@correo.com",
        "name": "Usuario Test"
    }

    response = client.post(
        "/api/auth/firebase/",
        {},
        format="json",
        HTTP_AUTHORIZATION="Bearer fake-token"
    )

    print("Response:", response.status_code, response.data)

    assert response.status_code in [200, 201]