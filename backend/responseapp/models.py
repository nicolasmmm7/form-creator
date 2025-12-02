# responseapp/models.py
from datetime import datetime
from mongoengine import Document, ReferenceField, DateTimeField, ListField, EmbeddedDocument, EmbeddedDocumentField, StringField, IntField, LongField

class RespuestaPregunta(EmbeddedDocument):
    pregunta_id = IntField(required=True)
    tipo = StringField(required=True, choices=('texto_libre', 'opcion_multiple', 'escala_numerica', 'checkbox'))
    valor = ListField(StringField())
    meta = {
        'collection': 'respuestaPreguntas'
    }

class Respondedor(Document):
    ip_address = StringField(required=True)
    google_id = LongField()
    email = StringField()
    nombre = StringField()
    foto_perfil = StringField()
    # ⚠️ DEPRECADO: Estos campos ya no se usan, se guardan en RespuestaFormulario
    navegador = StringField()  
    dispositivo = StringField()
    fecha_registro = DateTimeField(default=datetime.utcnow)
    ultimo_login = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'respondedores'
    }

class RespuestaFormulario(Document):
    formulario = ReferenceField('Formulario', required=True)
    respondedor = ReferenceField('Respondedor', required=True)
    fecha_envio = DateTimeField(default=datetime.utcnow)
    tiempo_completacion = LongField(default=0)
    
    # ✅ CAMPOS ACTUALIZADOS: Ahora a nivel de respuesta
    navegador = StringField(default="Desconocido")     # ✅ Chrome, Firefox, Safari, Edge, etc.
    dispositivo = StringField(default="Desconocido")   # ✅ Desktop, Móvil, Tablet
    
    respuestas = ListField(EmbeddedDocumentField(RespuestaPregunta))
    
    meta = {
        'collection': 'respuestaFormularios'
    }