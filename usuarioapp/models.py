from mongoengine import Document, StringField, EmailField, DateTimeField
from datetime import datetime


class Usuario(Document):
    """
    Representa un usuario del sistema, que puede ser administrador o respondedor.
    """
    nombre = StringField(required=True, max_length=100)
    correo = EmailField(required=True, unique=True)
    tipo = StringField(required=True, choices=('administrador', 'respondedor'))
    password = StringField(required=True, min_length=6)
    fecha_registro = DateTimeField(default=datetime.utcnow)

    meta = {'collection': 'usuarios'}  # Nombre de la colección en MongoDB

    def __str__(self):
        return f"{self.nombre} ({self.tipo})"


# Create your models here.
