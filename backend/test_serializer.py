import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "formCreatorApp.settings")
django.setup()

from usuarioapp.serializers import UsuarioSerializer

data = {
    "nombre": "Juan Perez",
    "email": "juan@test.com",
    "clave_hash": "123456",
    "empresa": {
        "nombre": "sin_empresa",
        "telefono": "3001234567"
    }
}

ser = UsuarioSerializer(data=data)
print("Is valid:", ser.is_valid())
if ser.is_valid():
    print("Validated data:", ser.validated_data)
else:
    print("Errors:", ser.errors)
