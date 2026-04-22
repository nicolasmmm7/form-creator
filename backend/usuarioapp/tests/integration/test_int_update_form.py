import pytest
from rest_framework.test import APIClient
from unittest.mock import patch
from usuarioapp.models import Usuario
import uuid


@pytest.mark.django_db
@patch("firebase_admin.auth.verify_id_token")
def test_actualizar_formulario_completo(mock_verify):
    client = APIClient()

    # 🔥 Email único
    email = f"test_{uuid.uuid4()}@correo.com"

    # 👤 Usuario
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

    # =====================================
    # 📦 CREAR FORMULARIO INICIAL
    # =====================================
    data_create = {
        "titulo": "Formulario Inicial",
        "descripcion": "Descripción inicial",
        "administrador": str(usuario.id),
        "preguntas": [
            {
                "id": 1,
                "tipo": "opcion_multiple",
                "enunciado": "¿Te gusta Python?",
                "opciones": [
                    {"texto": "Sí"},
                    {"texto": "No"}
                ],
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
    # 🔄 UPDATE ROBUSTO
    # =====================================
    data_update = {
        "titulo": "Formulario COMPLETAMENTE actualizado",
        "descripcion": "Nueva descripción avanzada",

        "configuracion": {
            "es_publico": False,
            "requerir_login": True,
            "usuarios_autorizados": [email],
            "permitir_edicion": True
        },

        "preguntas": [
            # 🔹 TEXTO LIBRE
            {
                "id": 1,
                "tipo": "texto_libre",
                "enunciado": "Explique su experiencia",
                "obligatorio": True,
                "validaciones": {
                    "longitud_minima": 10,
                    "longitud_maxima": 200
                }
            },

            # 🔹 OPCIÓN MÚLTIPLE
            {
                "id": 2,
                "tipo": "opcion_multiple",
                "enunciado": "Lenguaje favorito",
                "opciones": [
                    {"texto": "Python"},
                    {"texto": "Java"},
                    {"texto": "C++"}
                ],
                "obligatorio": True
            },

            # 🔹 ESCALA NUMÉRICA
            {
                "id": 3,
                "tipo": "escala_numerica",
                "enunciado": "Nivel de satisfacción",
                "validaciones": {
                    "valor_minimo": 1,
                    "valor_maximo": 5
                },
                "obligatorio": True
            }
        ]
    }

    update_response = client.put(
        f"/api/formularios/{form_id}/",
        data_update,
        format="json",
        HTTP_AUTHORIZATION=f"Bearer {token}"
    )

    print("UPDATE RESPONSE:", update_response.status_code, update_response.data)

    assert update_response.status_code in [200, 204]

    # =====================================
    # 🔍 VALIDAR TODO
    # =====================================
    get_response = client.get(
        f"/api/formularios/{form_id}/",
        HTTP_AUTHORIZATION=f"Bearer {token}"
    )

    print("GET RESPONSE:", get_response.data)

    assert get_response.status_code == 200

    data = get_response.data

    # 🔹 Validar campos básicos
    assert data["titulo"] == "Formulario COMPLETAMENTE actualizado"
    assert data["descripcion"] == "Nueva descripción avanzada"

    # 🔹 Validar configuración
    assert data["configuracion"]["es_publico"] is False
    assert data["configuracion"]["permitir_edicion"] is True
    assert email in data["configuracion"]["usuarios_autorizados"]

    # 🔹 Validar preguntas
    assert len(data["preguntas"]) == 3

    tipos = [p["tipo"] for p in data["preguntas"]]
    assert "texto_libre" in tipos
    assert "opcion_multiple" in tipos
    assert "escala_numerica" in tipos