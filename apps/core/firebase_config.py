# ============================================
# ARCHIVO CORREGIDO: core/firebase_config.py
# ============================================

import os
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
    
    # Construir ruta al archivo de credenciales
    cred_path = os.path.join(
        settings.BASE_DIR,
        "secure",
        "formcreator-87594-firebase-adminsdk-fbsvc-088b0a3684.json"
    )
    
    # Verificar que el archivo existe
    if not os.path.exists(cred_path):
        raise FileNotFoundError(
            f"❌ No se encontró el archivo de credenciales de Firebase en: {cred_path}\n"
            f"Asegúrate de que el archivo JSON está en la carpeta 'secure/'"
        )
    
    try:
        # Inicializar Firebase Admin SDK
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
        print("✅ Firebase Admin SDK inicializado correctamente")
    except Exception as e:
        raise Exception(f"❌ Error al inicializar Firebase: {str(e)}")


# NO ejecutar código aquí, solo definir la función
# La función se llamará desde settings.py