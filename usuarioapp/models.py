# usuarioapp/models.py
from datetime import datetime
from mongoengine import Document, EmailField, StringField, DateTimeField, LongField, EmbeddedDocument, EmbeddedDocumentField

class Empresa(EmbeddedDocument):
    nombre = StringField(required=True)
    telefono = LongField()
    nit = StringField()
    meta = {
        'collection': 'empresas'
    }

class Perfil(EmbeddedDocument):
    avatar_url = StringField()
    idioma = StringField()
    timezone = StringField()
    meta = {
        'collection': 'perfiles'
    }

class Usuario(Document):
    nombre = StringField(required=True)
    email = EmailField(required=True, unique=True)
    clave_hash = StringField(required=True)
    fecha_registro = DateTimeField(default=datetime.now)
    empresa = EmbeddedDocumentField(Empresa)
    perfil = EmbeddedDocumentField(Perfil)
    
    meta = {
        'collection': 'usuarios'
    }


