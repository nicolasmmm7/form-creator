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
        "titulo": "Formulario completo de prueba",
        "descripcion": "Formulario con múltiples tipos de preguntas",
        "preguntas": [

            # 🔹 1. Opción múltiple (obligatoria)
            {
                "id": 1,
                "enunciado": "¿Te gusta la programación?",
                "tipo": "opcion_multiple",
                "opciones": [
                    {"texto": "Sí", "orden": 1},
                    {"texto": "No", "orden": 2}
                ],
                "obligatorio": True
            },

            # 🔹 2. Checkbox (no obligatoria)
            {
                "id": 2,
                "enunciado": "¿Qué lenguajes conoces?",
                "tipo": "checkbox",
                "opciones": [
                    {"texto": "Python"},
                    {"texto": "Java"},
                    {"texto": "C++"},
                    {"texto": "JavaScript"}
                ],
                "obligatorio": False
            },

            # 🔹 3. Texto libre (requiere validaciones)
            {
                "id": 3,
                "enunciado": "Describe tu experiencia programando",
                "tipo": "texto_libre",
                "obligatorio": True,
                "validaciones": {
                    "longitud_minima": 10,
                    "longitud_maxima": 200
                }
            },

            # 🔹 4. Escala numérica (requiere min y max)
            {
                "id": 4,
                "enunciado": "¿Qué tanto te gusta programar del 1 al 10?",
                "tipo": "escala_numerica",
                "obligatorio": True,
                "validaciones": {
                    "valor_minimo": 1,
                    "valor_maximo": 10
                }
            },

            # 🔹 5. Otra opción múltiple
            {
                "id": 5,
                "enunciado": "¿Prefieres frontend o backend?",
                "tipo": "opcion_multiple",
                "opciones": [
                    {"texto": "Frontend"},
                    {"texto": "Backend"},
                    {"texto": "Fullstack"}
                ],
                "obligatorio": False
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