# formapp/models.py
from datetime import datetime
from mongoengine import Document, StringField, ReferenceField, DateTimeField, EmbeddedDocument, EmbeddedDocumentField, BooleanField, ListField, IntField, LongField

class Opcion(EmbeddedDocument):
    valor = StringField()
    texto = StringField()
    orden = IntField()

class Validaciones(EmbeddedDocument):
    longitudminima = IntField()
    longitudmaxima = IntField()
    valorminimo = IntField()
    valormaximo = IntField()

class Pregunta(EmbeddedDocument):
    id = IntField(required=True)
    tipo = StringField(required=True, choices=('texto_libre', 'opcion_multiple', 'escala_numerica'))
    enunciado = StringField(required=True)
    obligatorio = BooleanField(default=False)
    opciones = ListField(EmbeddedDocumentField(Opcion))
    validaciones = EmbeddedDocumentField(Validaciones)
    posicion = IntField()

class ConfiguracionFormulario(EmbeddedDocument):
    privado = BooleanField(default=False)
    fechalimite = DateTimeField()
    notificacionesemail = BooleanField(default=True)
    requerirlogin = BooleanField(default=True)
    unarespuesta = BooleanField(default=False)
    permitiredicion = BooleanField(default=False)

class Formulario(Document):
    titulo = StringField(required=True)
    descripcion = StringField()
    administrador = ReferenceField('Usuario', required=True)
    fechacreacion = DateTimeField(required=True)
    configuracion = EmbeddedDocumentField(ConfiguracionFormulario)
    preguntas = ListField(EmbeddedDocumentField(Pregunta), required=True)

    meta = {
        'collection': 'formularios'
    }