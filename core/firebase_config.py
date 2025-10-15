import os
import firebase_admin
from firebase_admin import credentials, auth
from django.conf import settings

# Evitar inicialización duplicada
if not firebase_admin._apps:
    cred_path = os.path.join(
        settings.BASE_DIR,
        "secure",
        "formcreator-87594-firebase-adminsdk-fbsvc-088b0a3684.json"
    )

    if not os.path.exists(cred_path):
        raise FileNotFoundError(f"No se encontró el archivo JSON en: {cred_path}")

    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)
    print("✅ Firebase Admin SDK inicializado correctamente (core/firebase_config.py)")

# Exporta el objeto auth para otros módulos
firebase_auth = auth
