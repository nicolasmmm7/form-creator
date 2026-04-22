import pytest
import uuid
from rest_framework.test import APIClient
from unittest.mock import patch
from usuarioapp.models import Usuario


@pytest.mark.django_db
@patch("firebase_admin.auth.verify_id_token")
def test_obtener_formulario_por_id(mock_verify):
    client = APIClient()

    # 🔥 Email único para evitar duplicados
    email = f"test_{uuid.uuid4()}@correo.com"

    # 👤 Crear usuario REAL en MongoDB
    usuario = Usuario(
        email=email,
        nombre="Usuario Test",
        clave_hash="fake_hash_123"
    )
    usuario.save()

    # 🔥 Mock Firebase
    mock_verify.return_value = {
        "uid": str(usuario.id),
        "email": email,
        "name": "Usuario Test"
    }

    token = "fake-token"

    # 📦 Crear formulario
    data = {
        "titulo": "Formulario GET",
        "descripcion": "Prueba de obtener formulario",
        "preguntas": [
            {
                "id": 1,
                "enunciado": "¿Te gusta Django?",
                "tipo": "opcion_multiple",
                "opciones": [
                    {"texto": "Sí"},
                    {"texto": "No"}
                ],
                "obligatoria": True
            }
        ]
    }

    create_response = client.post(
        "/api/formularios/",
        data,
        format="json",
        HTTP_AUTHORIZATION=f"Bearer {token}"
    )

    assert create_response.status_code == 201

    form_id = create_response.data["id"]

    # 🔍 Obtener formulario
    get_response = client.get(
        f"/api/formularios/{form_id}/",
        HTTP_AUTHORIZATION=f"Bearer {token}"
    )

    print("GET RESPONSE:", get_response.status_code, get_response.data)

    # ✅ Validaciones
    assert get_response.status_code == 200
    assert get_response.data["titulo"] == "Formulario GET"
    assert len(get_response.data["preguntas"]) == 1