import pytest
from rest_framework.test import APIClient
from unittest.mock import patch

@pytest.mark.django_db
@patch("firebase_admin.auth.verify_id_token")
def test_crear_formulario(mock_verify):
    client = APIClient()

    # 🔥 Simulamos usuario autenticado
    mock_verify.return_value = {
        "uid": "user123",
        "email": "test@correo.com",
        "name": "Usuario Test"
    }

    token = "fake-token"

    data = {
        "titulo": "Formulario de prueba",
        "descripcion": "Este es un formulario de integración",
        "administrador": "user123",
        "preguntas": [
            {
                "id": 1,  # ✅ CAMBIO CLAVE (entero)
                "enunciado": "¿Te gusta la programación?",
                "tipo": "opcion_multiple",
                "opciones": [
                    {"texto": "Sí"},
                    {"texto": "No"}
                ],
                "obligatoria": True
            }
        ]
    }

    response = client.post(
        "/api/formularios/",
        data,
        format="json",
        HTTP_AUTHORIZATION=f"Bearer {token}"
    )

    print("RESPONSE:", response.status_code, response.data)

    assert response.status_code in [200, 201]