# Script de Verificación: Validaciones en Edición de Respuestas

Este script documenta las pruebas que debes realizar para verificar que las validaciones de formulario se aplican correctamente al editar respuestas existentes.

## Preparación

### 1. Crear Formulario de Prueba

Crea un formulario con las siguientes características:

**Configuración del formulario:**
- Título: "Prueba de Validaciones en Edición"
- **Permitir edición:** ✅ Activado
- **Requiere login:** (opcional, según prefieras)

**Preguntas:**

1. **Texto Libre (Obligatorio)**
   - Enunciado: "Describe tu experiencia"
   - Tipo: Texto libre
   - Obligatorio: ✅ Sí
   - Longitud mínima: 10 caracteres
   - Longitud máxima: 50 caracteres

2. **Escala Numérica (Obligatorio)**
   - Enunciado: "Califica del 1 al 10"
   - Tipo: Escala numérica
   - Obligatorio: ✅ Sí
   - Valor mínimo: 1
   - Valor máximo: 10

3. **Opción Múltiple (No obligatorio)**
   - Enunciado: "¿Cómo nos conociste?"
   - Tipo: Opción múltiple
   - Obligatorio: ❌ No
   - Opciones: Redes sociales, Amigo, Búsqueda web, Otro

---

## Pruebas de Validación

### ✅ Prueba 1: Validaciones en Creación (Baseline)

**Objetivo:** Confirmar que las validaciones funcionan en la creación inicial.

1. Abre el formulario
2. **Intenta enviar sin responder preguntas obligatorias**
   - Resultado esperado: ❌ Error en rojo: "¡Oops! Esta pregunta es obligatoria, no olvides responderla 📝"

3. **Escribe solo 5 caracteres en el texto libre**
   - Ejemplo: "Hola"
   - Resultado esperado: ❌ Error: "Tu respuesta es un poco corta. Por favor escribe al menos 10 caracteres ✍️"

4. **Ingresa un número fuera del rango (ej: 15)**
   - Resultado esperado: ❌ Error: "Por favor ingresa un número menor o igual a 10 😊"

5. **Completa correctamente y envía**
   - Texto: "Esta es mi experiencia de prueba" (30 caracteres)
   - Escala: 7
   - Resultado esperado: ✅ Respuesta guardada correctamente

---

### ✅ Prueba 2: Validaciones en Edición (Objetivo Principal)

**Objetivo:** Verificar que las mismas validaciones se aplican al editar.

#### Escenario A: Borrar respuesta obligatoria

1. Vuelve al formulario respondido
2. El sistema detecta que ya respondiste → aparece modal "Ya has respondido este formulario"
3. Haz clic en **"Editar mi respuesta"**
4. Las respuestas previas deben aparecer precargadas
5. **Borra completamente el texto de "Describe tu experiencia"**
6. Haz clic en "Enviar respuestas"
7. Resultado esperado: ❌ Error en rojo: "¡Oops! Esta pregunta es obligatoria, no olvides responderla 📝"

#### Escenario B: Longitud mínima

1. Edita la respuesta nuevamente
2. **Cambia el texto a "Prueba"** (6 caracteres)
3. Haz clic en "Enviar respuestas"
4. Resultado esperado: ❌ Error: "Tu respuesta es un poco corta. Por favor escribe al menos 10 caracteres ✍️"

#### Escenario C: Longitud máxima

1. Edita la respuesta nuevamente
2. **Escribe un texto de más de 50 caracteres**
   - Ejemplo: "Este es un texto muy largo que definitivamente excede el límite de cincuenta caracteres establecido"
3. Haz clic en "Enviar respuestas"
4. Resultado esperado: ❌ Error: "Tu respuesta es un poco larga. Por favor no excedas 50 caracteres ✂️"

#### Escenario D: Valor numérico fuera de rango (mínimo)

1. Edita la respuesta nuevamente
2. **Cambia la calificación a 0** (menor que el mínimo de 1)
3. Haz clic en "Enviar respuestas"
4. Resultado esperado: ❌ Error: "Por favor ingresa un número mayor o igual a 1 😊"

#### Escenario E: Valor numérico fuera de rango (máximo)

1. Edita la respuesta nuevamente
2. **Cambia la calificación a 15** (mayor que el máximo de 10)
3. Haz clic en "Enviar respuestas"
4. Resultado esperado: ❌ Error: "Por favor ingresa un número menor o igual a 10 😊"

#### Escenario F: Edición exitosa

1. Edita la respuesta nuevamente
2. **Cambia el texto a "Nueva experiencia actualizada"** (29 caracteres - válido)
3. **Cambia la calificación a 9** (dentro del rango)
4. Haz clic en "Enviar respuestas"
5. Resultado esperado: ✅ Mensaje "¡Cambios guardados con éxito!" con confetti

---

## Verificación Backend (Opcional)

Si tienes acceso a los logs del servidor, verifica que:

1. Las peticiones PUT a `/api/respuestas/<id>/` retornan **HTTP 400** cuando hay errores de validación
2. Los errores tienen el formato: `{"pregunta_1": ["Error..."], "pregunta_2": ["Error..."]}`
3. Las respuestas válidas retornan **HTTP 200** con el mensaje de éxito

---

## Checklist Final

- [ ] Prueba 1: Validaciones en creación funcionan correctamente
- [ ] Escenario A: Borrar respuesta obligatoria en edición → rechazado ✅
- [ ] Escenario B: Longitud mínima en edición → rechazado ✅
- [ ] Escenario C: Longitud máxima en edición → rechazado ✅
- [ ] Escenario D: Valor mínimo en edición → rechazado ✅
- [ ] Escenario E: Valor máximo en edición → rechazado ✅
- [ ] Escenario F: Edición válida → aceptada ✅
- [ ] Los mensajes de error son idénticos entre creación y edición
- [ ] Los errores se muestran en rojo debajo de cada pregunta
- [ ] El frontend muestra el mensaje general "Por favor revisa los campos marcados en rojo"

---

## Notas

- **Frontend:** Los errores deben aparecer en cajas rojas debajo de cada pregunta (líneas 509-529 de `AnswerForm.jsx`)
- **Backend:** El serializer aplica las mismas validaciones en `create()` y `update()` gracias al método `validate()` compartido
- **Mensajes amigables:** Todos los mensajes incluyen emojis y son user-friendly (según conversación dbdf0eb4-7699-489b-9f81-b7a562bc31f9)
