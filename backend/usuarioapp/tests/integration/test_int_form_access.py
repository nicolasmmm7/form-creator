import pytest
from rest_framework.test import APIClient
from unittest.mock import patch
from usuarioapp.models import Usuario
import uuid


@pytest.mark.django_db
@patch("firebase_admin.auth.verify_id_token")
def test_acceso_formulario_privado(mock_verify):
    client = APIClient()

    # =====================================
    # 👤 USUARIO AUTORIZADO
    # =====================================
    email_autorizado = f"user_{uuid.uuid4()}@correo.com"

    usuario_aut = Usuario(
        email=email_autorizado,
        nombre="Usuario Autorizado",
        clave_hash="hash123"
    )
    usuario_aut.save()

    # =====================================
    # 👤 USUARIO NO AUTORIZADO
    # =====================================
    email_no_aut = f"user_{uuid.uuid4()}@correo.com"

    usuario_no_aut = Usuario(
        email=email_no_aut,
        nombre="Usuario No Autorizado",
        clave_hash="hash123"
    )
    usuario_no_aut.save()

    token = "fake-token"

    # =====================================
    # 🔥 MOCK DINÁMICO (cambia según usuario)
    # =====================================
    def mock_firebase(uid, email):
        return {
            "uid": str(uid),
            "email": email,
            "name": "Test User"
        }

    # =====================================
    # 📦 CREAR FORMULARIO PRIVADO
    # =====================================
    mock_verify.return_value = mock_firebase(usuario_aut.id, email_autorizado)

    data_create = {
        "titulo": "Formulario Privado",
        "descripcion": "Solo algunos pueden ver",
        "administrador": str(usuario_aut.id),
        "configuracion": {
            "es_publico": False,
            "requerir_login": True,
            "usuarios_autorizados": [email_autorizado]
        },
        "preguntas": [
            {
                "id": 1,
                "tipo": "opcion_multiple",
                "enunciado": "¿Acceso?",
                "opciones": [{"texto": "Sí"}, {"texto": "No"}],
                "obligatorio": True
            }
        ]
    }

    create_response = client.post(
        "/api/formularios/",
        data_create,
        format="json",
        HTTP_AUTHORIZATION=f"Bearer {token}"
    )

    assert create_response.status_code == 201
    form_id = create_response.data["id"]

    # =====================================
    # ✅ CASO 1: USUARIO AUTORIZADO
    # =====================================
    mock_verify.return_value = mock_firebase(usuario_aut.id, email_autorizado)

    response_ok = client.get(
        f"/api/formularios/{form_id}/",
        HTTP_AUTHORIZATION=f"Bearer {token}"
    )

    print("AUTORIZADO:", response_ok.status_code, response_ok.data)

    assert response_ok.status_code == 200

    # =====================================
    # ❌ CASO 2: USUARIO NO AUTORIZADO
    # =====================================
    mock_verify.return_value = mock_firebase(usuario_no_aut.id, email_no_aut)

    response_fail = client.get(
        f"/api/formularios/{form_id}/",
        HTTP_AUTHORIZATION=f"Bearer {token}"
    )

    print("NO AUTORIZADO:", response_fail.status_code, response_fail.data)

    # 🔥 AQUÍ ESTÁ LA CLAVE DEL TEST
    assert response_fail.status_code in [403, 401]