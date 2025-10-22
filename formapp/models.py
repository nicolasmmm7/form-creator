# formapp/models.py
from datetime import datetime
from mongoengine import Document, StringField, ReferenceField, DateTimeField, EmbeddedDocument, EmbeddedDocumentField, BooleanField, ListField, IntField

class Opcion(EmbeddedDocument):
    valor = StringField()
    texto = StringField()
    orden = IntField()
    meta = {
        'collection': 'opciones'
    }

class Validaciones(EmbeddedDocument):
    longitud_minima = IntField()
    longitud_maxima = IntField()
    valor_minimo = IntField()
    valor_maximo = IntField()
    meta = {
        'collection': 'validaciones'
    }

class Pregunta(EmbeddedDocument):
    id = IntField(required=True)
    tipo = StringField(required=True, choices=('texto_libre', 'opcion_multiple', 'escala_numerica', 'checkbox'))
    enunciado = StringField(required=True)
    obligatorio = BooleanField(default=False)
    opciones = ListField(EmbeddedDocumentField(Opcion))
    validaciones = EmbeddedDocumentField(Validaciones)
    posicion = IntField()
    meta = {
        'collection': 'preguntas'
    }

class ConfiguracionFormulario(EmbeddedDocument):
    privado = BooleanField(default=False)
    fecha_limite = DateTimeField()
    notificaciones_email = BooleanField(default=True)
    requerir_login = BooleanField(default=True)
    una_respuesta = BooleanField(default=False)
    permitir_edicion = BooleanField(default=False)
    meta = {
        'collection': 'configuracionFormularios'
    }

class Formulario(Document):
    titulo = StringField(required=True)
    descripcion = StringField()
    administrador = ReferenceField('Usuario', required=True)
    fecha_creacion = DateTimeField(default=datetime.utcnow)
    configuracion = EmbeddedDocumentField(ConfiguracionFormulario)
    preguntas = ListField(EmbeddedDocumentField(Pregunta))

    meta = {
        'collection': 'formularios'
    }
