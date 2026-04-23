# Pruebas de Base de Datos - Form-Creator
## Guía de Ejecución

### 1. Instalar dependencias

```bash
cd backend
pip install mongomock pytest pytest-django
```

### 2. Ejecutar todas las pruebas de BD

```bash
# Desde la carpeta backend/
python -m pytest tests/ -v
```

### 3. Ejecutar por archivo

```bash
# Solo pruebas de Usuario
python -m pytest tests/test_db_usuario.py -v

# Solo pruebas de Formulario
python -m pytest tests/test_db_formulario.py -v

# Solo pruebas de Respuestas
python -m pytest tests/test_db_respuesta.py -v
```

### 4. Ejecutar una prueba específica

```bash
# Ejemplo: solo la prueba de email duplicado
python -m pytest tests/test_db_usuario.py::TestUsuarioRestricciones::test_email_unico_rechaza_duplicado -v
```

### 5. Ver reporte detallado

```bash
python -m pytest tests/ -v --tb=short
```

---

## Estructura de las Pruebas

```
tests/
├── conftest.py              # Configuración de mongomock (BD en memoria)
├── test_db_usuario.py       # CP-DB-01 a CP-DB-06
├── test_db_formulario.py    # CP-DB-07 a CP-DB-11
└── test_db_respuesta.py     # CP-DB-12 a CP-DB-16
```

## Casos de Prueba

| ID       | Descripción                                    | Modelo              |
|----------|------------------------------------------------|---------------------|
| CP-DB-01 | Creación de usuario (CREATE)                   | Usuario             |
| CP-DB-02 | Lectura/consulta de usuario (READ)             | Usuario             |
| CP-DB-03 | Actualización de usuario (UPDATE)              | Usuario             |
| CP-DB-04 | Eliminación de usuario (DELETE)                | Usuario             |
| CP-DB-05 | Restricciones de BD (unique email, validación) | Usuario             |
| CP-DB-06 | Tokens de reset password                       | ResetPasswordToken  |
| CP-DB-07 | Creación de formulario                         | Formulario          |
| CP-DB-08 | Preguntas embebidas (texto, opciones, escala)  | Pregunta/Opcion     |
| CP-DB-09 | Configuración y control de acceso              | ConfiguracionForm   |
| CP-DB-10 | Consultas y filtros                            | Formulario          |
| CP-DB-11 | Eliminación de formulario                      | Formulario          |
| CP-DB-12 | Creación de respondedor                        | Respondedor         |
| CP-DB-13 | Creación de respuestas                         | RespuestaFormulario |
| CP-DB-14 | Consultas y estadísticas                       | RespuestaFormulario |
| CP-DB-15 | Actualización/edición de respuestas            | RespuestaFormulario |
| CP-DB-16 | Eliminación de respuestas                      | RespuestaFormulario |

## ¿Cómo funciona mongomock?

Las pruebas usan **mongomock** en lugar de un servidor MongoDB real:

- **No necesita MongoDB instalado** - mongomock simula MongoDB en memoria
- **Cada prueba es aislada** - la BD se limpia automáticamente entre tests
- **No afecta producción** - nunca toca tu BD de MongoDB Atlas
- **Es rápido** - se ejecuta en milisegundos

La configuración está en `conftest.py` y se aplica automáticamente a todas las pruebas.

## Total de pruebas: 50+

Cubre las operaciones CRUD completas para los 3 modelos principales del sistema,
validaciones de integridad, restricciones de BD, y consultas utilizadas en las
vistas de estadísticas y exportación.
