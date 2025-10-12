# formapp/models.py
from datetime import datetime
from mongoengine import Document, StringField, DateTimeField, ListField, EmbeddedDocument, EmbeddedDocumentField, ReferenceField, BooleanField

class Pregunta(EmbeddedDocument):
    texto = StringField(required=True)  # Enunciado de la pregunta
    tipo = StringField(required=True, choices=('texto_libre', 'opcion_multiple', 'escala_numerica'))
    opciones = ListField(StringField(), default=list)  # Opciones válidas (si aplica)
    obligatorio = BooleanField(default=False)

class Formulario(Document):
    titulo = StringField(required=True)
    descripcion = StringField()
    preguntas = ListField(EmbeddedDocumentField(Pregunta), required=True)  # Lista de preguntas personalizables:contentReference[oaicite:6]{index=6}
    propietario = ReferenceField('Usuario', required=True)  # Autor del formulario
    publicado = BooleanField(default=False)  # Estado para respuestas
    una_respuesta_por_usuario = BooleanField(default=False)  # RB-6: limitar a 1 respuesta por usuario:contentReference[oaicite:7]{index=7}
    permitir_edicion_respuestas = BooleanField(default=False)
    fecha_creacion = DateTimeField(default=datetime.utcnow)  # RB-10: registrar fecha/hora de creación:contentReference[oaicite:8]{index=8}
    fecha_publicacion = DateTimeField()

    meta = {
        'collection': 'formulario'
    }
