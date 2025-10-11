# usuarioapp/models.py
from datetime import datetime
from mongoengine import Document, EmailField, StringField, DateTimeField, BooleanField

class Usuario(Document):
    email = EmailField(required=True, unique=True)  # Correo único por usuario (RB-12)
    password = StringField(required=True, min_length=8)  # Contraseña cifrada
    rol = StringField(required=True, choices=('administrador', 'respondiente'))
    fecha_creacion = DateTimeField(default=datetime.utcnow)

    meta = {
        'collection': 'usuario'
    }
