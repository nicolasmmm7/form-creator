# responseapp/models.py
from datetime import datetime
from mongoengine import Document, ReferenceField, DateTimeField, ListField, EmbeddedDocument, EmbeddedDocumentField, StringField, IntField, LongField

class RespuestaPregunta(EmbeddedDocument):
    preguntaid = IntField(required=True)
    tipo = StringField(required=True, choices=('texto_libre', 'opcion_multiple', 'escala_numerica'))
    valor = ListField(StringField())  # Puede contener textos u opciones

class Respondedor(Document):
    ipaddress = StringField(required=True)
    googleid = LongField()
    email = StringField()
    nombre = StringField()
    fotoperfil = StringField()
    fecharegistro = DateTimeField()
    ultimologin = DateTimeField()
    
    meta = {
        'collection': 'respondedor'
    }

class RespuestaFormulario(Document):
    formulario = ReferenceField('Formulario', required=True)
    respondedor = ReferenceField('Respondedor', required=True)
    fechaenvio = DateTimeField(required=True)
    tiempocompletacion = LongField()
    respuestas = ListField(EmbeddedDocumentField(RespuestaPregunta), required=True)

    meta = {
        'collection': 'respuestasFormularios'
    }

