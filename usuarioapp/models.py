# usuarioapp/models.py
from datetime import datetime
from mongoengine import Document, EmailField, StringField, DateTimeField, BooleanField, LongField, EmbeddedDocument, EmbeddedDocumentField

class Empresa(EmbeddedDocument):
    nombre = StringField(required=True)
    telefono = LongField()
    nit = StringField()

class Perfil(EmbeddedDocument):
    avatarurl = StringField()
    idioma = StringField()
    timezone = StringField()

class Usuario(Document):
    nombre = StringField(required=True)
    email = StringField(required=True, unique=True)
    clavehash = StringField(required=True)
    fecharegistro = DateTimeField(required=True)
    empresa = EmbeddedDocumentField(Empresa)
    perfil = EmbeddedDocumentField(Perfil)
    
    meta = {
        'collection': 'administrador'
    }

