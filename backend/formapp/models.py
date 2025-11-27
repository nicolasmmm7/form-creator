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
    # Campo para controlar la visibilidad del formulario (solo aplica si requerir_login=True)
    es_publico = BooleanField(default=True)  # True = público, False = privado
    
    # Lista de correos electrónicos autorizados (solo aplica si es_publico=False y requerir_login=True)
    usuarios_autorizados = ListField(StringField())  # Lista de emails con acceso
    
    # Campos existentes
    privado = BooleanField(default=False)
    fecha_limite = DateTimeField()
    notificaciones_email = BooleanField(default=True)
    requerir_login = BooleanField(default=True)
    una_respuesta = BooleanField(default=False)
    permitir_edicion = BooleanField(default=False)
    
    meta = {
        'collection': 'configuracionFormularios'
    }
    
    def tiene_acceso(self, email):
        """
        Verifica si un usuario tiene acceso al formulario.
        Esta validación solo aplica cuando requerir_login=True.
        
        Args:
            email (str): Correo electrónico del usuario
            
        Returns:
            bool: True si tiene acceso, False en caso contrario
        """
        # Si no requiere login, no aplica la restricción de visibilidad
        if not self.requerir_login:
            return True
        
        # Si requiere login pero el formulario es público, todos los usuarios logueados tienen acceso
        if self.es_publico:
            return True
        
        # Si es privado y requiere login, verificar si el email está en la lista
        if email and self.usuarios_autorizados:
            return email.lower() in [u.lower() for u in self.usuarios_autorizados]
        
        # Si no hay email o la lista está vacía, denegar acceso
        return False

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
    
    def usuario_puede_responder(self, email=None):
        """
        Verifica si un usuario puede responder el formulario.
        
        Args:
            email (str, optional): Correo electrónico del usuario. 
                                   Solo necesario si el formulario requiere login y es privado.
            
        Returns:
            bool: True si puede responder, False en caso contrario
        """
        if not self.configuracion:
            # Si no hay configuración, por defecto es público
            return True
        
        return self.configuracion.tiene_acceso(email)