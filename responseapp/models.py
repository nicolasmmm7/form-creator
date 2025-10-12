# responseapp/models.py
from datetime import datetime
from mongoengine import Document, ReferenceField, DateTimeField, ListField, EmbeddedDocument, EmbeddedDocumentField, StringField, IntField

class RespuestaPregunta(EmbeddedDocument):
    texto_pregunta = StringField(required=True)  # Enunciado original de la pregunta
    tipo = StringField(required=True, choices=('texto_libre', 'opcion_multiple', 'escala_numerica'))
    respuesta_texto = StringField()       # Respuesta para tipo texto
    opcion_seleccionada = StringField()   # Opción elegida para tipo opción múltiple
    respuesta_numerica = IntField()       # Valor numérico para tipo escala

class RespuestaFormulario(Document):
    formulario = ReferenceField('Formulario', required=True)
    respondiente = ReferenceField('Usuario', required=True)
    respuestas = ListField(EmbeddedDocumentField(RespuestaPregunta), required=True)
    fecha_envio = DateTimeField(default=datetime.utcnow)

    meta = {
        'collection': 'respuesta'
    }
