# ============================================
# ARCHIVO CORREGIDO: core/firebase_config.py
# ============================================

import os
import json
import firebase_admin
from firebase_admin import credentials
from django.conf import settings


def initialize_firebase():
    """
    Inicializa Firebase Admin SDK UNA SOLA VEZ
    
    ¿Por qué esta función?
    - Evita inicializaciones duplicadas
    - Maneja errores si el archivo JSON no existe
    - Se llama desde settings.py en el startup de Django
    """
    
    # Verificar si Firebase ya está inicializado
    if firebase_admin._apps:
        print("⚠️  Firebase ya estaba inicializado, saltando...")
        return
    
    # INTENTO 1: Cargar desde variable de entorno (Producción / Railway)
    firebase_creds_json = os.environ.get('FIREBASE_CREDENTIALS_JSON')
    
    if firebase_creds_json:
        try:
            # Parsear el JSON string a un diccionario
            cred_dict = json.loads(firebase_creds_json)
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred)
            print("✅ Firebase Admin SDK inicializado desde VARIABLE DE ENTORNO")
            return
        except json.JSONDecodeError as e:
            print(f"❌ Error al parsear FIREBASE_CREDENTIALS_JSON: {e}")
            # No retornamos, dejamos que intente el fallback o falle
        except Exception as e:
            print(f"❌ Error al inicializar Firebase desde env var: {e}")
            # No retornamos, dejamos que intente el fallback o falle

    # INTENTO 2: Cargar desde archivo (Desarrollo Local)
    # Construir ruta al archivo de credenciales
    cred_path = os.path.join(
        settings.BASE_DIR,
        "secure",
        "formcreator-87594-firebase-adminsdk-fbsvc-088b0a3684.json"
    )
    
    # Verificar que el archivo existe
    if not os.path.exists(cred_path):
        # Si no hay env var Y no hay archivo, entonces sí es un error fatal
        raise FileNotFoundError(
            f"❌ No se encontró credenciales de Firebase.\n"
            f"1. No existe la variable de entorno 'FIREBASE_CREDENTIALS_JSON'\n"
            f"2. No se encontró el archivo en: {cred_path}"
        )
    
    try:
        # Inicializar Firebase Admin SDK con archivo
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
        print("✅ Firebase Admin SDK inicializado desde ARCHIVO LOCAL")
    except Exception as e:
        raise Exception(f"❌ Error al inicializar Firebase: {str(e)}")


# NO ejecutar código aquí, solo definir la función
# La función se llamará desde settings.py
```