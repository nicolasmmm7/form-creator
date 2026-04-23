# tests/test_db_respuesta.py
"""
═══════════════════════════════════════════════════════════════
PRUEBAS DE BASE DE DATOS - MODELO RESPUESTAFORMULARIO
═══════════════════════════════════════════════════════════════

Pruebas que verifican operaciones CRUD y relaciones del modelo
RespuestaFormulario, incluyendo:
- Creación de respondedores
- Creación de respuestas con referencias a formularios
- Consultas de respuestas por formulario
- Datos para estadísticas (dispositivos, navegadores, tiempos)

CP-DB-12: Creación de respondedor
CP-DB-13: Creación de respuestas
CP-DB-14: Consultas y estadísticas
CP-DB-15: Actualización y edición de respuestas
CP-DB-16: Eliminación de respuestas
"""
import pytest
from datetime import datetime
from mongoengine.errors import ValidationError

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from responseapp.models import RespuestaFormulario, Respondedor, RespuestaPregunta
from formapp.models import Formulario, Pregunta, Validaciones
from usuarioapp.models import Usuario


def _crear_admin():
    """Helper: crea un usuario administrador."""
    admin = Usuario(
        nombre="Admin",
        email=f"admin_{datetime.utcnow().timestamp()}@test.com",
        clave_hash="hash"
    )
    admin.save()
    return admin


def _crear_formulario_con_preguntas(admin):
    """Helper: crea un formulario con 2 preguntas para pruebas."""
    preguntas = [
        Pregunta(
            id=1, tipo="texto_libre",
            enunciado="¿Tu nombre?", obligatorio=True,
            validaciones=Validaciones(longitud_minima=1, longitud_maxima=100)
        ),
        Pregunta(
            id=2, tipo="escala_numerica",
            enunciado="Satisfacción", obligatorio=True,
            validaciones=Validaciones(valor_minimo=1, valor_maximo=10)
        ),
    ]
    form = Formulario(
        titulo="Encuesta Test",
        administrador=admin,
        preguntas=preguntas
    )
    form.save()
    return form


def _crear_respondedor(email="respondedor@test.com"):
    """Helper: crea un respondedor."""
    resp = Respondedor(
        ip_address="192.168.1.1",
        email=email,
        nombre="Respondedor Test"
    )
    resp.save()
    return resp


# ═══════════════════════════════════════════════════════════
# CP-DB-12: CREACIÓN DE RESPONDEDOR
# ═══════════════════════════════════════════════════════════

class TestRespondedorCreacion:
    """Pruebas de inserción de documentos Respondedor."""

    def test_crear_respondedor_basico(self):
        """
        CP-DB-12a: Un respondedor con IP y email debe
        guardarse correctamente.
        """
        resp = Respondedor(
            ip_address="10.0.0.1",
            email="test@respondedor.com",
            nombre="Juan Respondedor"
        )
        resp.save()

        assert resp.id is not None
        resp_db = Respondedor.objects.get(id=resp.id)
        assert resp_db.email == "test@respondedor.com"

    def test_crear_respondedor_solo_con_ip(self):
        """
        CP-DB-12b: Un respondedor anónimo (solo IP, sin email)
        debe poder guardarse (caso de formulario sin login).
        """
        resp = Respondedor(ip_address="172.16.0.1")
        resp.save()

        assert resp.id is not None
        assert resp.email is None

    def test_respondedor_con_google_id(self):
        """
        CP-DB-12c: Un respondedor autenticado con Google debe
        almacenar su google_id como identificador adicional.
        """
        resp = Respondedor(
            ip_address="10.0.0.1",
            email="google@test.com",
            google_id=1234567890,
            nombre="Google User",
            foto_perfil="https://photo.url"
        )
        resp.save()

        resp_db = Respondedor.objects.get(id=resp.id)
        assert resp_db.google_id == 1234567890

    def test_buscar_respondedor_por_email(self):
        """
        CP-DB-12d: Un respondedor debe poder encontrarse
        filtrando por email.
        """
        Respondedor(ip_address="1.1.1.1", email="buscar@test.com").save()

        encontrado = Respondedor.objects(email="buscar@test.com").first()
        assert encontrado is not None
        assert encontrado.ip_address == "1.1.1.1"

    def test_coleccion_correcta_respondedor(self):
        """
        CP-DB-12e: El modelo Respondedor debe usar la colección
        'respondedores'.
        """
        assert Respondedor._meta.get('collection', None) == 'respondedores'


# ═══════════════════════════════════════════════════════════
# CP-DB-13: CREACIÓN DE RESPUESTAS
# ═══════════════════════════════════════════════════════════

class TestRespuestaCreacion:
    """Pruebas de inserción de RespuestaFormulario."""

    def test_crear_respuesta_completa(self):
        """
        CP-DB-13a: Una respuesta con formulario, respondedor y
        respuestas a preguntas debe guardarse correctamente.
        """
        admin = _crear_admin()
        form = _crear_formulario_con_preguntas(admin)
        respondedor = _crear_respondedor()

        respuestas = [
            RespuestaPregunta(pregunta_id=1, tipo="texto_libre", valor=["Mi nombre"]),
            RespuestaPregunta(pregunta_id=2, tipo="escala_numerica", valor=["8"]),
        ]

        rf = RespuestaFormulario(
            formulario=form,
            respondedor=respondedor,
            tiempo_completacion=45,
            navegador="Chrome",
            dispositivo="Desktop",
            respuestas=respuestas
        )
        rf.save()

        assert rf.id is not None
        rf_db = RespuestaFormulario.objects.get(id=rf.id)
        assert len(rf_db.respuestas) == 2
        assert rf_db.tiempo_completacion == 45
        assert rf_db.navegador == "Chrome"
        assert rf_db.dispositivo == "Desktop"

    def test_respuesta_tiene_fecha_envio(self):
        """
        CP-DB-13b: La respuesta debe tener fecha_envio asignada
        automáticamente al crearse.
        """
        admin = _crear_admin()
        form = _crear_formulario_con_preguntas(admin)
        respondedor = _crear_respondedor()

        rf = RespuestaFormulario(
            formulario=form,
            respondedor=respondedor,
            respuestas=[]
        )
        rf.save()

        assert rf.fecha_envio is not None
        assert isinstance(rf.fecha_envio, datetime)

    def test_referencia_a_formulario_correcta(self):
        """
        CP-DB-13c: La respuesta debe mantener una referencia
        válida al formulario original.
        """
        admin = _crear_admin()
        form = _crear_formulario_con_preguntas(admin)
        respondedor = _crear_respondedor()

        rf = RespuestaFormulario(
            formulario=form,
            respondedor=respondedor,
            respuestas=[]
        )
        rf.save()

        rf_db = RespuestaFormulario.objects.get(id=rf.id)
        assert str(rf_db.formulario.id) == str(form.id)
        assert rf_db.formulario.titulo == "Encuesta Test"

    def test_respuesta_pregunta_tipo_checkbox_multiples_valores(self):
        """
        CP-DB-13d: Una respuesta tipo checkbox debe almacenar
        múltiples valores en la lista.
        """
        admin = _crear_admin()
        form = _crear_formulario_con_preguntas(admin)
        respondedor = _crear_respondedor()

        respuestas = [
            RespuestaPregunta(
                pregunta_id=1,
                tipo="checkbox",
                valor=["Opción A", "Opción B", "Opción C"]
            ),
        ]

        rf = RespuestaFormulario(
            formulario=form,
            respondedor=respondedor,
            respuestas=respuestas
        )
        rf.save()

        rf_db = RespuestaFormulario.objects.get(id=rf.id)
        assert len(rf_db.respuestas[0].valor) == 3
        assert "Opción B" in rf_db.respuestas[0].valor

    def test_coleccion_correcta_respuesta(self):
        """
        CP-DB-13e: El modelo RespuestaFormulario debe usar la
        colección 'respuestaFormularios'.
        """
        assert RespuestaFormulario._meta.get('collection', None) == 'respuestaFormularios'


# ═══════════════════════════════════════════════════════════
# CP-DB-14: CONSULTAS Y ESTADÍSTICAS
# ═══════════════════════════════════════════════════════════

class TestRespuestaConsultas:
    """Pruebas de consultas para estadísticas y reportes."""

    def _crear_respuestas(self, form, n=3):
        """Helper: crea N respuestas para un formulario."""
        respuestas_creadas = []
        navegadores = ["Chrome", "Firefox", "Safari"]
        dispositivos = ["Desktop", "Móvil", "Tablet"]

        for i in range(n):
            resp = Respondedor(
                ip_address=f"10.0.0.{i+1}",
                email=f"user{i}@test.com"
            )
            resp.save()

            rf = RespuestaFormulario(
                formulario=form,
                respondedor=resp,
                tiempo_completacion=30 + (i * 10),
                navegador=navegadores[i % len(navegadores)],
                dispositivo=dispositivos[i % len(dispositivos)],
                respuestas=[
                    RespuestaPregunta(
                        pregunta_id=1,
                        tipo="texto_libre",
                        valor=[f"Respuesta {i}"]
                    ),
                ]
            )
            rf.save()
            respuestas_creadas.append(rf)

        return respuestas_creadas

    def test_filtrar_respuestas_por_formulario(self):
        """
        CP-DB-14a: Debe poder filtrarse respuestas por el
        formulario al que pertenecen (caso de uso principal).
        """
        admin = _crear_admin()
        form1 = _crear_formulario_con_preguntas(admin)
        form2 = Formulario(titulo="Otro Form", administrador=admin)
        form2.save()

        self._crear_respuestas(form1, 3)
        self._crear_respuestas(form2, 2)

        resp_form1 = RespuestaFormulario.objects(formulario=form1)
        assert resp_form1.count() == 3

        resp_form2 = RespuestaFormulario.objects(formulario=form2)
        assert resp_form2.count() == 2

    def test_contar_total_respuestas(self):
        """
        CP-DB-14b: count() debe retornar el número correcto
        de respuestas para un formulario.
        """
        admin = _crear_admin()
        form = _crear_formulario_con_preguntas(admin)
        self._crear_respuestas(form, 5)

        total = RespuestaFormulario.objects(formulario=form).count()
        assert total == 5

    def test_calcular_tiempo_promedio(self):
        """
        CP-DB-14c: Debe poder calcularse el tiempo promedio
        de completación desde las respuestas almacenadas.
        """
        admin = _crear_admin()
        form = _crear_formulario_con_preguntas(admin)
        self._crear_respuestas(form, 3)  # tiempos: 30, 40, 50

        respuestas = RespuestaFormulario.objects(formulario=form)
        tiempos = [r.tiempo_completacion for r in respuestas]
        promedio = sum(tiempos) / len(tiempos)

        assert promedio == 40.0  # (30 + 40 + 50) / 3

    def test_agrupar_por_dispositivo(self):
        """
        CP-DB-14d: Debe poder contarse respuestas por tipo de
        dispositivo (para gráfico de pie en estadísticas).
        """
        admin = _crear_admin()
        form = _crear_formulario_con_preguntas(admin)
        self._crear_respuestas(form, 3)

        respuestas = RespuestaFormulario.objects(formulario=form)
        dispositivos = {}
        for r in respuestas:
            dev = r.dispositivo
            dispositivos[dev] = dispositivos.get(dev, 0) + 1

        assert len(dispositivos) == 3  # Desktop, Móvil, Tablet
        assert all(v == 1 for v in dispositivos.values())

    def test_agrupar_por_navegador(self):
        """
        CP-DB-14e: Debe poder contarse respuestas por navegador
        (para gráfico de pie en estadísticas).
        """
        admin = _crear_admin()
        form = _crear_formulario_con_preguntas(admin)
        self._crear_respuestas(form, 3)

        respuestas = RespuestaFormulario.objects(formulario=form)
        navegadores = {}
        for r in respuestas:
            nav = r.navegador
            navegadores[nav] = navegadores.get(nav, 0) + 1

        assert "Chrome" in navegadores
        assert "Firefox" in navegadores
        assert "Safari" in navegadores

    def test_formulario_sin_respuestas_retorna_vacio(self):
        """
        CP-DB-14f: Un formulario sin respuestas debe retornar
        un queryset vacío con count() == 0.
        """
        admin = _crear_admin()
        form = _crear_formulario_con_preguntas(admin)

        respuestas = RespuestaFormulario.objects(formulario=form)
        assert respuestas.count() == 0


# ═══════════════════════════════════════════════════════════
# CP-DB-15: ACTUALIZACIÓN DE RESPUESTAS (EDICIÓN)
# ═══════════════════════════════════════════════════════════

class TestRespuestaActualizacion:
    """Pruebas de edición de respuestas existentes."""

    def test_actualizar_respuestas_de_preguntas(self):
        """
        CP-DB-15a: Al editar una respuesta, los nuevos valores
        deben reemplazar los anteriores en la BD.
        """
        admin = _crear_admin()
        form = _crear_formulario_con_preguntas(admin)
        respondedor = _crear_respondedor()

        rf = RespuestaFormulario(
            formulario=form,
            respondedor=respondedor,
            respuestas=[
                RespuestaPregunta(pregunta_id=1, tipo="texto_libre", valor=["Original"]),
            ]
        )
        rf.save()

        # Editar
        rf.respuestas = [
            RespuestaPregunta(pregunta_id=1, tipo="texto_libre", valor=["Editado"]),
        ]
        rf.save()

        rf_db = RespuestaFormulario.objects.get(id=rf.id)
        assert rf_db.respuestas[0].valor[0] == "Editado"

    def test_actualizar_tiempo_completacion(self):
        """
        CP-DB-15b: Al editar una respuesta, el tiempo de
        completación debe actualizarse.
        """
        admin = _crear_admin()
        form = _crear_formulario_con_preguntas(admin)
        respondedor = _crear_respondedor()

        rf = RespuestaFormulario(
            formulario=form,
            respondedor=respondedor,
            tiempo_completacion=30,
            respuestas=[]
        )
        rf.save()

        rf.tiempo_completacion = 60
        rf.save()

        rf_db = RespuestaFormulario.objects.get(id=rf.id)
        assert rf_db.tiempo_completacion == 60


# ═══════════════════════════════════════════════════════════
# CP-DB-16: ELIMINACIÓN DE RESPUESTAS
# ═══════════════════════════════════════════════════════════

class TestRespuestaEliminacion:
    """Pruebas de eliminación de respuestas."""

    def test_eliminar_respuesta(self):
        """
        CP-DB-16a: Eliminar una respuesta debe removerla
        de la colección.
        """
        admin = _crear_admin()
        form = _crear_formulario_con_preguntas(admin)
        respondedor = _crear_respondedor()

        rf = RespuestaFormulario(
            formulario=form,
            respondedor=respondedor,
            respuestas=[]
        )
        rf.save()
        rf_id = rf.id

        rf.delete()

        with pytest.raises(RespuestaFormulario.DoesNotExist):
            RespuestaFormulario.objects.get(id=rf_id)

    def test_eliminar_respuesta_no_elimina_formulario(self):
        """
        CP-DB-16b: Eliminar una respuesta NO debe eliminar
        el formulario asociado.
        """
        admin = _crear_admin()
        form = _crear_formulario_con_preguntas(admin)
        form_id = form.id
        respondedor = _crear_respondedor()

        rf = RespuestaFormulario(
            formulario=form,
            respondedor=respondedor,
            respuestas=[]
        )
        rf.save()
        rf.delete()

        # El formulario debe seguir existiendo
        form_db = Formulario.objects.get(id=form_id)
        assert form_db.titulo == "Encuesta Test"

    def test_eliminar_respuesta_no_elimina_respondedor(self):
        """
        CP-DB-16c: Eliminar una respuesta NO debe eliminar
        al respondedor asociado.
        """
        admin = _crear_admin()
        form = _crear_formulario_con_preguntas(admin)
        respondedor = _crear_respondedor()
        resp_id = respondedor.id

        rf = RespuestaFormulario(
            formulario=form,
            respondedor=respondedor,
            respuestas=[]
        )
        rf.save()
        rf.delete()

        resp_db = Respondedor.objects.get(id=resp_id)
        assert resp_db.email == "respondedor@test.com"
