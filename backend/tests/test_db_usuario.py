# tests/test_db_usuario.py
"""
═══════════════════════════════════════════════════════════════
PRUEBAS DE BASE DE DATOS - MODELO USUARIO
═══════════════════════════════════════════════════════════════

Estas pruebas verifican las operaciones CRUD y restricciones del
modelo Usuario directamente contra MongoDB (simulado con mongomock).

A diferencia de las pruebas unitarias (que usan mocks), estas pruebas:
- Insertan documentos reales en una BD simulada
- Verifican que los datos persisten correctamente
- Validan restricciones como unicidad de email
- Prueban consultas y filtros de MongoEngine

Casos de prueba organizados por categoría:
- CP-DB-01: Creación de usuario
- CP-DB-02: Lectura/consulta de usuario  
- CP-DB-03: Actualización de usuario
- CP-DB-04: Eliminación de usuario
- CP-DB-05: Restricciones y validaciones de BD
- CP-DB-06: Documentos embebidos (Empresa, Perfil)
"""
import pytest
from datetime import datetime
from mongoengine.errors import NotUniqueError, ValidationError

# Importar modelos
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from usuarioapp.models import Usuario, Empresa, Perfil, ResetPasswordToken


# ═══════════════════════════════════════════════════════════
# CP-DB-01: CREACIÓN DE USUARIO (CREATE)
# ═══════════════════════════════════════════════════════════

class TestUsuarioCreacion:
    """Pruebas de inserción de documentos Usuario en MongoDB."""

    def test_crear_usuario_basico(self):
        """
        CP-DB-01a: Un usuario con los campos mínimos requeridos
        (nombre, email, clave_hash) debe guardarse exitosamente en la BD.
        """
        usuario = Usuario(
            nombre="Juan David",
            email="juandavid@empresa.com",
            clave_hash="hash_seguro_123"
        )
        usuario.save()

        # Verificar que se asignó un ID de MongoDB
        assert usuario.id is not None
        assert str(usuario.id) != ""

    def test_crear_usuario_con_fecha_automatica(self):
        """
        CP-DB-01b: Al crear un usuario, el campo fecha_registro
        debe asignarse automáticamente con la fecha actual.
        """
        usuario = Usuario(
            nombre="Laura Caballero",
            email="laura@empresa.com",
            clave_hash="hash_456"
        )
        usuario.save()

        assert usuario.fecha_registro is not None
        assert isinstance(usuario.fecha_registro, datetime)

    def test_crear_usuario_con_empresa_y_perfil(self):
        """
        CP-DB-01c: Un usuario con documentos embebidos (Empresa y Perfil)
        debe guardarse correctamente con toda la estructura anidada.
        """
        empresa = Empresa(
            nombre="FormCreator SAS",
            telefono=3001234567,
            nit="900123456-1"
        )
        perfil = Perfil(
            avatar_url="https://example.com/avatar.jpg",
            idioma="es",
            timezone="America/Bogota"
        )

        usuario = Usuario(
            nombre="Nicolas Meneses",
            email="nicolas@empresa.com",
            clave_hash="hash_789",
            empresa=empresa,
            perfil=perfil
        )
        usuario.save()

        # Recuperar de la BD y verificar estructura
        user_db = Usuario.objects.get(id=usuario.id)
        assert user_db.empresa.nombre == "FormCreator SAS"
        assert user_db.empresa.telefono == 3001234567
        assert user_db.perfil.idioma == "es"
        assert user_db.perfil.avatar_url == "https://example.com/avatar.jpg"

    def test_crear_usuario_sin_nombre_falla(self):
        """
        CP-DB-01d: Un usuario sin nombre (campo required) debe
        ser rechazado por MongoEngine con ValidationError.
        """
        usuario = Usuario(
            email="sinnombre@test.com",
            clave_hash="hash_abc"
        )
        with pytest.raises(ValidationError):
            usuario.save()

    def test_crear_usuario_sin_email_falla(self):
        """
        CP-DB-01e: Un usuario sin email (campo required) debe
        ser rechazado por MongoEngine.
        """
        usuario = Usuario(
            nombre="Sin Email",
            clave_hash="hash_xyz"
        )
        with pytest.raises(ValidationError):
            usuario.save()

    def test_crear_usuario_sin_clave_falla(self):
        """
        CP-DB-01f: Un usuario sin clave_hash (campo required) debe
        ser rechazado.
        """
        usuario = Usuario(
            nombre="Sin Clave",
            email="sinclave@test.com"
        )
        with pytest.raises(ValidationError):
            usuario.save()


# ═══════════════════════════════════════════════════════════
# CP-DB-02: LECTURA/CONSULTA DE USUARIO (READ)
# ═══════════════════════════════════════════════════════════

class TestUsuarioLectura:
    """Pruebas de consulta y recuperación de documentos Usuario."""

    def _crear_usuario(self, nombre="Test User", email="test@test.com"):
        """Helper para crear un usuario de prueba."""
        u = Usuario(nombre=nombre, email=email, clave_hash="hash123")
        u.save()
        return u

    def test_buscar_usuario_por_id(self):
        """
        CP-DB-02a: Un usuario guardado debe poder recuperarse
        por su ObjectId de MongoDB.
        """
        usuario = self._crear_usuario()
        encontrado = Usuario.objects.get(id=usuario.id)

        assert encontrado.nombre == "Test User"
        assert encontrado.email == "test@test.com"

    def test_buscar_usuario_por_email(self):
        """
        CP-DB-02b: Un usuario debe poder encontrarse por su email
        (campo con índice unique).
        """
        self._crear_usuario(nombre="Angely Pino", email="angely@empresa.com")
        encontrado = Usuario.objects.get(email="angely@empresa.com")

        assert encontrado.nombre == "Angely Pino"

    def test_buscar_usuario_inexistente_lanza_excepcion(self):
        """
        CP-DB-02c: Buscar un usuario con email que no existe
        debe lanzar DoesNotExist.
        """
        with pytest.raises(Usuario.DoesNotExist):
            Usuario.objects.get(email="noexiste@test.com")

    def test_listar_todos_los_usuarios(self):
        """
        CP-DB-02d: objects() debe retornar todos los usuarios
        almacenados en la colección.
        """
        self._crear_usuario("User 1", "user1@test.com")
        self._crear_usuario("User 2", "user2@test.com")
        self._crear_usuario("User 3", "user3@test.com")

        todos = Usuario.objects()
        assert todos.count() == 3

    def test_filtrar_usuarios_por_nombre(self):
        """
        CP-DB-02e: Debe poder filtrarse usuarios usando
        operadores de consulta de MongoEngine.
        """
        self._crear_usuario("Juan David", "juan@test.com")
        self._crear_usuario("Juan Sebastian", "sebastian@test.com")
        self._crear_usuario("Laura", "laura@test.com")

        juanes = Usuario.objects(nombre__startswith="Juan")
        assert juanes.count() == 2

    def test_consulta_con_first_retorna_none_si_no_existe(self):
        """
        CP-DB-02f: .first() debe retornar None (no excepción)
        cuando no encuentra resultados.
        """
        resultado = Usuario.objects(email="fantasma@test.com").first()
        assert resultado is None


# ═══════════════════════════════════════════════════════════
# CP-DB-03: ACTUALIZACIÓN DE USUARIO (UPDATE)
# ═══════════════════════════════════════════════════════════

class TestUsuarioActualizacion:
    """Pruebas de actualización de documentos Usuario."""

    def _crear_usuario(self):
        u = Usuario(
            nombre="Original",
            email="original@test.com",
            clave_hash="hash_original"
        )
        u.save()
        return u

    def test_actualizar_nombre_usuario(self):
        """
        CP-DB-03a: Cambiar el nombre de un usuario y guardar
        debe reflejarse al recuperarlo nuevamente de la BD.
        """
        usuario = self._crear_usuario()
        usuario.nombre = "Nombre Actualizado"
        usuario.save()

        actualizado = Usuario.objects.get(id=usuario.id)
        assert actualizado.nombre == "Nombre Actualizado"

    def test_actualizar_clave_hash(self):
        """
        CP-DB-03b: Actualizar la clave_hash (cambio de contraseña)
        debe persistir en la BD.
        """
        usuario = self._crear_usuario()
        usuario.clave_hash = "nueva_clave_segura"
        usuario.save()

        actualizado = Usuario.objects.get(id=usuario.id)
        assert actualizado.clave_hash == "nueva_clave_segura"

    def test_agregar_empresa_a_usuario_existente(self):
        """
        CP-DB-03c: Agregar un documento embebido (Empresa) a un
        usuario que no lo tenía debe funcionar correctamente.
        """
        usuario = self._crear_usuario()
        assert usuario.empresa is None

        usuario.empresa = Empresa(nombre="Mi Empresa SAS", nit="123456789-0")
        usuario.save()

        actualizado = Usuario.objects.get(id=usuario.id)
        assert actualizado.empresa is not None
        assert actualizado.empresa.nombre == "Mi Empresa SAS"

    def test_actualizar_campo_embebido_perfil(self):
        """
        CP-DB-03d: Modificar un campo dentro de un documento
        embebido (Perfil.idioma) debe persistir.
        """
        usuario = self._crear_usuario()
        usuario.perfil = Perfil(idioma="es", timezone="America/Bogota")
        usuario.save()

        # Cambiar idioma
        usuario.perfil.idioma = "en"
        usuario.save()

        actualizado = Usuario.objects.get(id=usuario.id)
        assert actualizado.perfil.idioma == "en"

    def test_update_atomico_con_mongoengine(self):
        """
        CP-DB-03e: La operación update() de MongoEngine debe
        modificar el documento sin necesidad de .save().
        """
        usuario = self._crear_usuario()
        Usuario.objects(id=usuario.id).update(set__nombre="Actualizado Atómico")

        actualizado = Usuario.objects.get(id=usuario.id)
        assert actualizado.nombre == "Actualizado Atómico"


# ═══════════════════════════════════════════════════════════
# CP-DB-04: ELIMINACIÓN DE USUARIO (DELETE)
# ═══════════════════════════════════════════════════════════

class TestUsuarioEliminacion:
    """Pruebas de eliminación de documentos Usuario."""

    def test_eliminar_usuario_existente(self):
        """
        CP-DB-04a: Eliminar un usuario existente debe removerlo
        completamente de la colección.
        """
        usuario = Usuario(
            nombre="A Eliminar",
            email="eliminar@test.com",
            clave_hash="hash"
        )
        usuario.save()
        user_id = usuario.id

        usuario.delete()

        with pytest.raises(Usuario.DoesNotExist):
            Usuario.objects.get(id=user_id)

    def test_eliminar_reduce_conteo(self):
        """
        CP-DB-04b: Después de eliminar un usuario, el conteo
        total de la colección debe disminuir en 1.
        """
        u1 = Usuario(nombre="User 1", email="u1@test.com", clave_hash="h1")
        u2 = Usuario(nombre="User 2", email="u2@test.com", clave_hash="h2")
        u1.save()
        u2.save()

        assert Usuario.objects.count() == 2

        u1.delete()

        assert Usuario.objects.count() == 1

    def test_eliminar_usuario_no_afecta_otros(self):
        """
        CP-DB-04c: Eliminar un usuario no debe afectar a los
        demás usuarios de la colección.
        """
        u1 = Usuario(nombre="Sobrevive", email="sobrevive@test.com", clave_hash="h1")
        u2 = Usuario(nombre="Eliminado", email="eliminado@test.com", clave_hash="h2")
        u1.save()
        u2.save()

        u2.delete()

        sobreviviente = Usuario.objects.get(email="sobrevive@test.com")
        assert sobreviviente.nombre == "Sobrevive"


# ═══════════════════════════════════════════════════════════
# CP-DB-05: RESTRICCIONES Y VALIDACIONES DE BD
# ═══════════════════════════════════════════════════════════

class TestUsuarioRestricciones:
    """Pruebas de restricciones de integridad en la BD."""

    def test_email_unico_rechaza_duplicado(self):
        """
        CP-DB-05a: Intentar crear dos usuarios con el mismo email
        debe lanzar NotUniqueError (restricción unique=True).
        """
        Usuario(
            nombre="Primero",
            email="duplicado@test.com",
            clave_hash="hash1"
        ).save()

        with pytest.raises(NotUniqueError):
            Usuario(
                nombre="Segundo",
                email="duplicado@test.com",
                clave_hash="hash2"
            ).save()

    def test_email_formato_invalido_es_rechazado(self):
        """
        CP-DB-05b: Un email con formato inválido debe ser rechazado
        por el campo EmailField de MongoEngine.
        """
        usuario = Usuario(
            nombre="Email Malo",
            email="esto_no_es_email",
            clave_hash="hash"
        )
        with pytest.raises(ValidationError):
            usuario.save()

    def test_coleccion_correcta(self):
        """
        CP-DB-05c: El modelo Usuario debe almacenarse en la
        colección 'usuarios' (definida en meta).
        """
        assert Usuario._meta.get('collection', None) == 'usuarios'


# ═══════════════════════════════════════════════════════════
# CP-DB-06: TOKENS DE RESET PASSWORD
# ═══════════════════════════════════════════════════════════

class TestResetPasswordToken:
    """Pruebas CRUD para tokens de recuperación de contraseña."""

    def test_crear_token_reset(self):
        """
        CP-DB-06a: Crear un token de reset con email y código
        debe persistir en la BD.
        """
        token = ResetPasswordToken(
            email="reset@test.com",
            token="123456"
        )
        token.save()

        encontrado = ResetPasswordToken.objects.get(email="reset@test.com")
        assert encontrado.token == "123456"
        assert encontrado.expires_at is not None

    def test_eliminar_tokens_anteriores(self):
        """
        CP-DB-06b: Debe poder eliminarse todos los tokens previos
        de un email antes de crear uno nuevo (flujo real del sistema).
        """
        ResetPasswordToken(email="user@test.com", token="111111").save()
        ResetPasswordToken(email="user@test.com", token="222222").save()

        assert ResetPasswordToken.objects(email="user@test.com").count() == 2

        # Simular el flujo real: borrar anteriores
        ResetPasswordToken.objects(email="user@test.com").delete()

        assert ResetPasswordToken.objects(email="user@test.com").count() == 0

        # Crear nuevo
        ResetPasswordToken(email="user@test.com", token="333333").save()
        assert ResetPasswordToken.objects(email="user@test.com").count() == 1
