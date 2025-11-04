// src/pages/CreateForm.jsx
import React, { useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";


const defaultQuestion = (id) => ({
  id,
  tipo: "texto_libre",
  enunciado: "",
  obligatorio: false,
  posicion: id,
  opciones: [],
  validaciones: { longitud_minima: 1, longitud_maxima: 255 }
});

export default function CreateForm() {
  const navigate = useNavigate();
  const { formId } = useParams();
  const [titulo, setTitulo] = useState("");
  const [descripcion, setDescripcion] = useState("");
  const [preguntas, setPreguntas] = useState([defaultQuestion(1)]);
  const [nextId, setNextId] = useState(2);
  const [loading, setLoading] = useState(false); 

  // 🔧 Nueva configuración del formulario
  const [config, setConfig] = useState({
    privado: false,
    fecha_limite: "",
    notificaciones_email: false,
    requerir_login: false,
    una_respuesta: true,
    permitir_edicion: false,
  });


  const user = JSON.parse(localStorage.getItem("user"));

  //cargar datos del formulario si estamos en modo edición
  useEffect(() => {
    if (formId) {
      cargarFormularioParaEditar();
    }
  }, [formId]);
  
  const cargarFormularioParaEditar = async () => {
    setLoading(true);
    try {
      const res = await fetch(`http://127.0.0.1:8000/api/formularios/${formId}/`);
      
      if (!res.ok) {
        throw new Error("No se pudo cargar el formulario");
      }

      const data = await res.json();
      console.log("📋 Formulario cargado para editar:", data);

      // Cargar datos del formulario
      setTitulo(data.titulo);
      setDescripcion(data.descripcion);
      setPreguntas(data.preguntas || []);
      
      // Calcular el siguiente ID (máximo ID + 1)
      const maxId = Math.max(...(data.preguntas?.map(p => p.id) || [0]));
      setNextId(maxId + 1);

      // Cargar configuración
      if (data.configuracion) {
        setConfig({
          privado: data.configuracion.privado || false,
          fecha_limite: data.configuracion.fecha_limite || "",
          notificaciones_email: data.configuracion.notificaciones_email || false,
          requerir_login: data.configuracion.requerir_login || false,
          una_respuesta: data.configuracion.una_respuesta ?? true,
          permitir_edicion: data.configuracion.permitir_edicion || false,
        });
      }
    } catch (error) {
      console.error("❌ Error al cargar formulario:", error);
      alert("Error al cargar el formulario para editar");
      navigate("/home");
    } finally {
      setLoading(false);
    }
  };

  if (!user?.id) {
    alert("Debe iniciar sesión antes de crear un formulario");
    navigate("/login");
    return null;
  }

  const addQuestion = () => {
    setPreguntas((prev) => [...prev, defaultQuestion(nextId)]);
    setNextId((v) => v + 1);
  };

  const updateQuestion = (idx, patch) => {
    setPreguntas((prev) =>
      prev.map((q, i) => (i === idx ? { ...q, ...patch } : q))
    );
  };

  const removeQuestion = (idx) => {
    setPreguntas((prev) => prev.filter((_, i) => i !== idx));
  };

  const addOption = (qIdx) => {
    const q = preguntas[qIdx];
    updateQuestion(qIdx, {
      opciones: [
        ...q.opciones,
        { valor: `opt${q.opciones.length + 1}`, texto: "", orden: q.opciones.length + 1 }
      ],
    });
  };

  const removeOption = (qIdx, optIdx) => {
  const q = preguntas[qIdx];
  updateQuestion(qIdx, {
    opciones: q.opciones.filter((_, i) => i !== optIdx),
  });
};


  const handleSave = async () => {
    if (!titulo.trim()) return alert("Escribe un título");
    if (preguntas.some(p => !p.enunciado.trim())) {
        alert("⚠️ Todas las preguntas deben tener un enunciado");
        return;
        }

    const payload = {
      titulo,
      descripcion,
      administrador: user.id,
      configuracion: {
        ...config, // 👈 usa el estado actual del formulario
        fecha_limite: config.fecha_limite || null, // por si viene vacío
      },
      preguntas: preguntas.map((p, i) => ({
        id: p.id,
        tipo: p.tipo,
        enunciado: p.enunciado,
        obligatorio: p.obligatorio,
        posicion: i + 1,
        opciones: p.opciones.map((o, idx) => ({
          valor: o.valor || `opt${idx + 1}`,
          texto: o.texto || `Opción ${idx + 1}`,
          orden: idx + 1,
        })),
        validaciones: p.validaciones || null,
      })),
    };

    try {
      let res;

      // 👇 NUEVO: Detectar si es creación o edición
      if (formId) {
        // EDICIÓN: Usar PUT
        res = await fetch(`http://127.0.0.1:8000/api/formularios/${formId}/`, {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
      } else {
        // CREACIÓN: Usar POST
        res = await fetch("http://127.0.0.1:8000/api/formularios/", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
      }

      let data = null;
      try {
        data = await res.json();
      } catch {
        throw new Error("Respuesta no válida del servidor");
      }

      if (!res.ok) {
        console.error("Error backend:", data);
        alert("Error creando formulario: " + JSON.stringify(data));
        return;
      }

      const mensaje = formId ? "✅ Formulario actualizado correctamente" : "✅ Formulario creado correctamente";
    alert(mensaje);
    navigate("/home");
    } catch (e) {
      console.error("❌ Error en handleSave:", e);
      alert("Fallo de conexión al crear formulario");
    }
  };

return (
  

  <main className="create-form-main">
    {/* Botón Volver */}
    <div className="create-back-container">
      <button 
        className="create-btn-back" 
        onClick={() => navigate("/home")}
      >
        <span className="create-back-arrow">←</span>
        Volver
      </button>
    </div>
    {/* ---------------------- Sección principal ---------------------- */}
    <section className="create-section-main">
      <h2>{formId ? "Editar formulario" : "Crear formulario"}</h2>
      <label className="create-label">Título</label>
      <input
        className="create-input"
        value={titulo}
        onChange={(e) => setTitulo(e.target.value)}
        style={{marginBottom: 5}}
      />
      <label className="create-label">Descripción</label>
      <textarea
        className="create-textarea"
        value={descripcion}
        onChange={(e) => setDescripcion(e.target.value)}
      />

      <h3>Preguntas</h3>
      {preguntas.map((q, idx) => (
        <div key={q.id} className="create-question-card">
          <label className="create-label" >
            Tipo:
            <select
              className="create-select"
              value={q.tipo}
              onChange={(e) => updateQuestion(idx, { tipo: e.target.value })}
              style={{marginLeft: 10}}
            >
              <option value="texto_libre">Texto libre</option>
              <option value="opcion_multiple">Opción múltiple</option>
              <option value="escala_numerica">Escala numérica</option>
              <option value="checkbox">Checkbox (varias)</option>
            </select>
          </label>

          <label className="create-label">
            Enunciado:
            <input
              className="create-input"
              value={q.enunciado}
              style= {{marginTop: 10}}
              onChange={(e) =>
                updateQuestion(idx, { enunciado: e.target.value })
              }

            />
          </label>

          <label className="create-label">
            Obligatorio:
            <input
              className="create-checkbox"
              type="checkbox"
              checked={q.obligatorio}
              onChange={(e) =>
                updateQuestion(idx, { obligatorio: e.target.checked })
              }
              style={{ marginLeft: 10 }}
            />
          </label>

          {q.tipo === "texto_libre" && (
            <div className="create-validations">
              <h4>Validaciones de texto</h4>
              <label className="create-label">
                Longitud mínima:
                <input
                  className="create-input"
                  type="number"
                  value={q.validaciones?.longitud_minima ?? ""}
                  style= {{marginTop: 10}}
                  onChange={(e) => {
                    const v = {
                      ...(q.validaciones || {}),
                      longitud_minima: Number(e.target.value),
                    };
                    updateQuestion(idx, { validaciones: v });
                  }}
                />
              </label>
              <label className="create-label">
                Longitud máxima:
                <input
                  className="create-input"
                  type="number"
                  value={q.validaciones?.longitud_maxima ?? ""}
                  style= {{marginTop: 10}}
                  onChange={(e) => {
                    const v = {
                      ...(q.validaciones || {}),
                      longitud_maxima: Number(e.target.value),
                    };
                    updateQuestion(idx, { validaciones: v });
                  }}
                />
              </label>
            </div>
          )}

          {q.tipo === "escala_numerica" && (
            <div className="create-validations">
              <h4>Rango numérico</h4>
              <label className="create-label">
                Mínimo:
                <input
                  className="create-input"
                  type="number"
                  value={q.validaciones?.valor_minimo ?? ""}
                  style= {{marginTop: 10}}
                  onChange={(e) => {
                    const v = {
                      ...(q.validaciones || {}),
                      valor_minimo: Number(e.target.value),
                    };
                    updateQuestion(idx, { validaciones: v });
                  }}
                />
              </label>
              <label className="create-label">
                Máximo:
                <input
                  className="create-input"
                  type="number"
                  value={q.validaciones?.valor_maximo ?? ""}
                  style= {{marginTop: 10}}
                  onChange={(e) => {
                    const v = {
                      ...(q.validaciones || {}),
                      valor_maximo: Number(e.target.value),
                    };
                    updateQuestion(idx, { validaciones: v });
                  }}
                />
              </label>
            </div>
          )}

          {(q.tipo === "opcion_multiple" || q.tipo === "checkbox") && (
            <div className="create-options">
              <h4>Opciones</h4>
              {q.opciones.map((opt, i) => (
                <div key={i} className="create-option-row">
                  <input
                    className="create-input create-option-input"
                    placeholder="Texto de opción"
                    value={opt.texto}
                    onChange={(e) => {
                      const ops = [...q.opciones];
                      ops[i] = { ...ops[i], texto: e.target.value };
                      updateQuestion(idx, { opciones: ops });
                    }}
                  />
                  <button
                    className="create-btn-remove-option"
                    type="button"
                    onClick={() => removeOption(idx, i)}
                    title="Eliminar opción"
                  >
                    ✕
                  </button>
                </div>
              ))}
              <button className="create-btn-add-option" type="button" onClick={() => addOption(idx)}>
                + Agregar opción
              </button>
            </div>
          )}

          <button
            className="create-btn-delete"
            type="button"
            onClick={() => removeQuestion(idx)}
          >
            Eliminar pregunta
          </button>
        </div>
      ))}

      <button className="create-btn-add" onClick={addQuestion}>
        + Agregar pregunta
      </button>
      <hr className="create-divider" />
      <button className="create-btn-save" onClick={handleSave}>
        Guardar formulario
      </button>
    </section>

    {/* ---------------------- Panel lateral derecho ---------------------- */}
    <aside className="create-sidebar">
      <h3 className="create-sidebar-title">⚙️ Configuración</h3>

      <label className="create-config-label">
        Borrador:
        <input
          className="create-checkbox"
          type="checkbox"
          checked={config.privado}
          onChange={(e) =>
            setConfig({ ...config, privado: e.target.checked })
          }
        />
      </label>

      <label className="create-config-label">
        Requiere login:
        <input
          className="create-checkbox"
          type="checkbox"
          checked={config.requerir_login}
          onChange={(e) =>
            setConfig({ ...config, requerir_login: e.target.checked })
          }
        />
      </label>

      <label className="create-config-label">
        Notificar por email:
        <input
          className="create-checkbox"
          type="checkbox"
          checked={config.notificaciones_email}
          onChange={(e) =>
            setConfig({ ...config, notificaciones_email: e.target.checked })
          }
        />
      </label>

      <label className="create-config-label">
        Fecha límite:
        <input
          className="create-input-date"
          type="date"
          value={config.fecha_limite}
          onChange={(e) =>
            setConfig({ ...config, fecha_limite: e.target.value })
          }
        />
      </label>

      <label className="create-config-label">
        Solo una respuesta:
        <input
          className="create-checkbox"
          type="checkbox"
          checked={config.una_respuesta}
          onChange={(e) =>
            setConfig({ ...config, una_respuesta: e.target.checked })
          }
        />
      </label>

      <label className="create-config-label">
        Permitir edición:
        <input
          className="create-checkbox"
          type="checkbox"
          checked={config.permitir_edicion}
          onChange={(e) =>
            setConfig({ ...config, permitir_edicion: e.target.checked })
          }
        />
      </label>
    </aside>
  </main>
);

}
