# tests/test_db_formulario.py
"""
═══════════════════════════════════════════════════════════════
PRUEBAS DE BASE DE DATOS - MODELO FORMULARIO
═══════════════════════════════════════════════════════════════

Pruebas que verifican operaciones CRUD y lógica de negocio del
modelo Formulario, incluyendo:
- Creación con preguntas embebidas
- Configuración de visibilidad y acceso
- Referencias al modelo Usuario (administrador)
- Consultas y filtros

CP-DB-07: Creación de formulario
CP-DB-08: Preguntas embebidas
CP-DB-09: Configuración y acceso
CP-DB-10: Consultas y filtros
CP-DB-11: Eliminación de formulario
"""
import pytest
from datetime import datetime
from mongoengine.errors import ValidationError

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from formapp.models import (
    Formulario, Pregunta, Opcion, Validaciones,
    ConfiguracionFormulario
)
from usuarioapp.models import Usuario


def _crear_admin():
    """Helper: crea un usuario administrador para asociar a formularios."""
    admin = Usuario(
        nombre="Admin Test",
        email=f"admin_{datetime.utcnow().timestamp()}@test.com",
        clave_hash="admin_hash"
    )
    admin.save()
    return admin


# ═══════════════════════════════════════════════════════════
# CP-DB-07: CREACIÓN DE FORMULARIO
# ═══════════════════════════════════════════════════════════

class TestFormularioCreacion:
    """Pruebas de inserción de formularios en MongoDB."""

    def test_crear_formulario_basico(self):
        """
        CP-DB-07a: Un formulario con título y administrador debe
        guardarse exitosamente y recibir un ID.
        """
        admin = _crear_admin()
        form = Formulario(
            titulo="Encuesta de Satisfacción",
            descripcion="Evalúa nuestro servicio",
            administrador=admin
        )
        form.save()

        assert form.id is not None
        assert form.titulo == "Encuesta de Satisfacción"

    def test_formulario_tiene_fecha_creacion(self):
        """
        CP-DB-07b: El formulario debe tener fecha_creacion
        asignada automáticamente.
        """
        admin = _crear_admin()
        form = Formulario(titulo="Test Fecha", administrador=admin)
        form.save()

        assert form.fecha_creacion is not None
        assert isinstance(form.fecha_creacion, datetime)

    def test_formulario_sin_titulo_falla(self):
        """
        CP-DB-07c: Un formulario sin título (required=True) debe
        ser rechazado por MongoEngine.
        """
        admin = _crear_admin()
        form = Formulario(administrador=admin)

        with pytest.raises(ValidationError):
            form.save()

    def test_formulario_sin_administrador_falla(self):
        """
        CP-DB-07d: Un formulario sin administrador (required=True)
        debe ser rechazado.
        """
        form = Formulario(titulo="Sin Admin")

        with pytest.raises(ValidationError):
            form.save()

    def test_referencia_administrador_es_correcta(self):
        """
        CP-DB-07e: El campo administrador debe ser una referencia
        válida al documento Usuario en MongoDB.
        """
        admin = _crear_admin()
        form = Formulario(titulo="Test Ref", administrador=admin)
        form.save()

        # Recuperar y verificar la referencia
        form_db = Formulario.objects.get(id=form.id)
        assert str(form_db.administrador.id) == str(admin.id)
        assert form_db.administrador.nombre == "Admin Test"


# ═══════════════════════════════════════════════════════════
# CP-DB-08: PREGUNTAS EMBEBIDAS
# ═══════════════════════════════════════════════════════════

class TestFormularioPreguntas:
    """Pruebas de documentos embebidos (Pregunta, Opcion, Validaciones)."""

    def test_crear_formulario_con_pregunta_texto_libre(self):
        """
        CP-DB-08a: Un formulario con pregunta tipo texto_libre y
        validaciones de longitud debe persistir correctamente.
        """
        admin = _crear_admin()
        pregunta = Pregunta(
            id=1,
            tipo="texto_libre",
            enunciado="¿Cuál es tu nombre?",
            obligatorio=True,
            validaciones=Validaciones(longitud_minima=3, longitud_maxima=100)
        )

        form = Formulario(
            titulo="Form con Texto",
            administrador=admin,
            preguntas=[pregunta]
        )
        form.save()

        form_db = Formulario.objects.get(id=form.id)
        assert len(form_db.preguntas) == 1
        assert form_db.preguntas[0].tipo == "texto_libre"
        assert form_db.preguntas[0].validaciones.longitud_minima == 3

    def test_crear_formulario_con_opcion_multiple(self):
        """
        CP-DB-08b: Una pregunta de opción múltiple con varias opciones
        debe almacenar todas las opciones embebidas.
        """
        admin = _crear_admin()
        opciones = [
            Opcion(valor="m", texto="Masculino", orden=1),
            Opcion(valor="f", texto="Femenino", orden=2),
            Opcion(valor="o", texto="Otro", orden=3),
        ]
        pregunta = Pregunta(
            id=1,
            tipo="opcion_multiple",
            enunciado="¿Cuál es tu género?",
            opciones=opciones
        )

        form = Formulario(
            titulo="Form con Opciones",
            administrador=admin,
            preguntas=[pregunta]
        )
        form.save()

        form_db = Formulario.objects.get(id=form.id)
        assert len(form_db.preguntas[0].opciones) == 3
        assert form_db.preguntas[0].opciones[0].texto == "Masculino"
        assert form_db.preguntas[0].opciones[2].texto == "Otro"

    def test_crear_formulario_con_escala_numerica(self):
        """
        CP-DB-08c: Una pregunta de escala numérica con rango
        definido debe persistir los valores min/max.
        """
        admin = _crear_admin()
        pregunta = Pregunta(
            id=1,
            tipo="escala_numerica",
            enunciado="Califica del 1 al 10",
            validaciones=Validaciones(valor_minimo=1, valor_maximo=10)
        )

        form = Formulario(
            titulo="Form con Escala",
            administrador=admin,
            preguntas=[pregunta]
        )
        form.save()

        form_db = Formulario.objects.get(id=form.id)
        assert form_db.preguntas[0].validaciones.valor_minimo == 1
        assert form_db.preguntas[0].validaciones.valor_maximo == 10

    def test_formulario_con_multiples_preguntas(self):
        """
        CP-DB-08d: Un formulario puede contener múltiples preguntas
        de diferentes tipos simultáneamente.
        """
        admin = _crear_admin()
        preguntas = [
            Pregunta(id=1, tipo="texto_libre", enunciado="Tu nombre",
                     validaciones=Validaciones(longitud_minima=1, longitud_maxima=50)),
            Pregunta(id=2, tipo="opcion_multiple", enunciado="Tu género",
                     opciones=[Opcion(valor="m", texto="M", orden=1)]),
            Pregunta(id=3, tipo="escala_numerica", enunciado="Satisfacción",
                     validaciones=Validaciones(valor_minimo=1, valor_maximo=5)),
        ]

        form = Formulario(
            titulo="Form Completo",
            administrador=admin,
            preguntas=preguntas
        )
        form.save()

        form_db = Formulario.objects.get(id=form.id)
        assert len(form_db.preguntas) == 3
        tipos = [p.tipo for p in form_db.preguntas]
        assert "texto_libre" in tipos
        assert "opcion_multiple" in tipos
        assert "escala_numerica" in tipos


# ═══════════════════════════════════════════════════════════
# CP-DB-09: CONFIGURACIÓN Y CONTROL DE ACCESO
# ═══════════════════════════════════════════════════════════

class TestFormularioConfiguracion:
    """Pruebas de ConfiguracionFormulario y lógica de acceso."""

    def test_configuracion_por_defecto(self):
        """
        CP-DB-09a: Un formulario con configuración por defecto
        debe ser público y sin restricciones especiales.
        """
        admin = _crear_admin()
        config = ConfiguracionFormulario()  # Todo por defecto

        form = Formulario(
            titulo="Form Default",
            administrador=admin,
            configuracion=config
        )
        form.save()

        form_db = Formulario.objects.get(id=form.id)
        assert form_db.configuracion.es_publico is True
        assert form_db.configuracion.requerir_login is True
        assert form_db.configuracion.privado is False

    def test_formulario_privado_con_usuarios_autorizados(self):
        """
        CP-DB-09b: Un formulario privado debe almacenar
        la lista de emails autorizados.
        """
        admin = _crear_admin()
        config = ConfiguracionFormulario(
            requerir_login=True,
            es_publico=False,
            usuarios_autorizados=["user1@test.com", "user2@test.com"]
        )

        form = Formulario(
            titulo="Form Privado",
            administrador=admin,
            configuracion=config
        )
        form.save()

        form_db = Formulario.objects.get(id=form.id)
        assert form_db.configuracion.es_publico is False
        assert len(form_db.configuracion.usuarios_autorizados) == 2
        assert "user1@test.com" in form_db.configuracion.usuarios_autorizados

    def test_tiene_acceso_usuario_autorizado(self):
        """
        CP-DB-09c: El método tiene_acceso() debe retornar True
        para un email que está en la lista de autorizados.
        """
        config = ConfiguracionFormulario(
            requerir_login=True,
            es_publico=False,
            usuarios_autorizados=["permitido@test.com"]
        )

        assert config.tiene_acceso("permitido@test.com") is True

    def test_tiene_acceso_usuario_no_autorizado(self):
        """
        CP-DB-09d: El método tiene_acceso() debe retornar False
        para un email que NO está en la lista.
        """
        config = ConfiguracionFormulario(
            requerir_login=True,
            es_publico=False,
            usuarios_autorizados=["permitido@test.com"]
        )

        assert config.tiene_acceso("intruso@test.com") is False

    def test_tiene_acceso_case_insensitive(self):
        """
        CP-DB-09e: La verificación de acceso debe ser insensible
        a mayúsculas/minúsculas en el email.
        """
        config = ConfiguracionFormulario(
            requerir_login=True,
            es_publico=False,
            usuarios_autorizados=["Usuario@Test.COM"]
        )

        assert config.tiene_acceso("usuario@test.com") is True
        assert config.tiene_acceso("USUARIO@TEST.COM") is True

    def test_formulario_publico_permite_todos(self):
        """
        CP-DB-09f: Un formulario público con login requerido
        debe permitir acceso a cualquier usuario autenticado.
        """
        config = ConfiguracionFormulario(
            requerir_login=True,
            es_publico=True
        )

        assert config.tiene_acceso("cualquiera@test.com") is True

    def test_configuracion_fecha_limite(self):
        """
        CP-DB-09g: La fecha límite debe almacenarse correctamente
        como DateTimeField en la configuración.
        """
        admin = _crear_admin()
        fecha = datetime(2026, 12, 31, 23, 59, 59)
        config = ConfiguracionFormulario(fecha_limite=fecha)

        form = Formulario(
            titulo="Form con Fecha",
            administrador=admin,
            configuracion=config
        )
        form.save()

        form_db = Formulario.objects.get(id=form.id)
        assert form_db.configuracion.fecha_limite is not None

    def test_agregar_usuario_autorizado_despues_de_crear(self):
        """
        CP-DB-09h: Debe poder agregarse un email a la lista de
        autorizados después de crear el formulario.
        """
        admin = _crear_admin()
        config = ConfiguracionFormulario(
            requerir_login=True,
            es_publico=False,
            usuarios_autorizados=["original@test.com"]
        )

        form = Formulario(
            titulo="Form Dinámico",
            administrador=admin,
            configuracion=config
        )
        form.save()

        # Agregar nuevo usuario
        form.configuracion.usuarios_autorizados.append("nuevo@test.com")
        form.save()

        form_db = Formulario.objects.get(id=form.id)
        assert "nuevo@test.com" in form_db.configuracion.usuarios_autorizados
        assert len(form_db.configuracion.usuarios_autorizados) == 2


# ═══════════════════════════════════════════════════════════
# CP-DB-10: CONSULTAS Y FILTROS
# ═══════════════════════════════════════════════════════════

class TestFormularioConsultas:
    """Pruebas de consultas complejas sobre formularios."""

    def test_filtrar_formularios_por_administrador(self):
        """
        CP-DB-10a: Debe poder filtrarse formularios por el ID
        del administrador (caso de uso principal en Home).
        """
        admin1 = _crear_admin()
        admin2 = Usuario(
            nombre="Otro Admin",
            email=f"otro_{datetime.utcnow().timestamp()}@test.com",
            clave_hash="hash"
        )
        admin2.save()

        Formulario(titulo="Form A1", administrador=admin1).save()
        Formulario(titulo="Form A2", administrador=admin1).save()
        Formulario(titulo="Form B1", administrador=admin2).save()

        forms_admin1 = Formulario.objects(administrador=admin1)
        assert forms_admin1.count() == 2

        forms_admin2 = Formulario.objects(administrador=admin2)
        assert forms_admin2.count() == 1

    def test_contar_total_formularios(self):
        """
        CP-DB-10b: count() debe retornar el número correcto
        de formularios en la colección.
        """
        admin = _crear_admin()
        for i in range(5):
            Formulario(titulo=f"Form {i}", administrador=admin).save()

        assert Formulario.objects.count() == 5

    def test_coleccion_correcta_formulario(self):
        """
        CP-DB-10c: El modelo Formulario debe almacenarse en la
        colección 'formularios'.
        """
        assert Formulario._meta.get('collection', None) == 'formularios'


# ═══════════════════════════════════════════════════════════
# CP-DB-11: ELIMINACIÓN DE FORMULARIO
# ═══════════════════════════════════════════════════════════

class TestFormularioEliminacion:
    """Pruebas de eliminación de formularios."""

    def test_eliminar_formulario(self):
        """
        CP-DB-11a: Un formulario eliminado no debe poder
        encontrarse posteriormente en la BD.
        """
        admin = _crear_admin()
        form = Formulario(titulo="A Eliminar", administrador=admin)
        form.save()
        form_id = form.id

        form.delete()

        with pytest.raises(Formulario.DoesNotExist):
            Formulario.objects.get(id=form_id)

    def test_eliminar_formulario_no_elimina_admin(self):
        """
        CP-DB-11b: Eliminar un formulario NO debe eliminar
        al usuario administrador asociado.
        """
        admin = _crear_admin()
        admin_id = admin.id

        form = Formulario(titulo="Form Temporal", administrador=admin)
        form.save()
        form.delete()

        # El admin debe seguir existiendo
        admin_db = Usuario.objects.get(id=admin_id)
        assert admin_db.nombre == "Admin Test"
