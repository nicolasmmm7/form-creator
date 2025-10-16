// src/pages/CreateForm.jsx
import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

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
  const [titulo, setTitulo] = useState("");
  const [descripcion, setDescripcion] = useState("");
  const [preguntas, setPreguntas] = useState([defaultQuestion(1)]);
  const [nextId, setNextId] = useState(2);

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
        privado: false,
        fecha_limite: null,
        notificaciones_email: false,
        requerir_login: false,
        una_respuesta: true,
        permitir_edicion: false,
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
      const res = await fetch("http://127.0.0.1:8000/api/formularios/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

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

      alert("✅ Formulario creado correctamente");
      navigate("/home");
    } catch (e) {
      console.error("❌ Error en handleSave:", e);
      alert("Fallo de conexión al crear formulario");
    }
  };

return (
    <main
      style={{
        display: "flex",
        flexDirection: "row",
        gap: "20px",
        padding: "20px",
      }}
    >
      {/* ---------------------- Sección principal ---------------------- */}
      <section style={{ flex: 3 }}>
        <h2>Crear formulario</h2>
        <label>Título</label>
        <input
          value={titulo}
          onChange={(e) => setTitulo(e.target.value)}
          style={{ width: "100%" }}
        />
        <label>Descripción</label>
        <textarea
          value={descripcion}
          onChange={(e) => setDescripcion(e.target.value)}
          style={{ width: "100%" }}
        />

        <h3>Preguntas</h3>
        {preguntas.map((q, idx) => (
          <div
            key={q.id}
            style={{
              border: "1px solid #ddd",
              padding: 10,
              marginBottom: 10,
              borderRadius: 6,
              background: "#e7f9f8",
            }}
          >
            <label>
              Tipo:
              <select
                value={q.tipo}
                onChange={(e) => updateQuestion(idx, { tipo: e.target.value })}
              >
                <option value="texto_libre">Texto libre</option>
                <option value="opcion_multiple">Opción múltiple</option>
                <option value="escala_numerica">Escala numérica</option>
                <option value="checkbox">Checkbox (varias)</option>
              </select>
            </label>

            <label>
              Enunciado:
              <input
                value={q.enunciado}
                onChange={(e) =>
                  updateQuestion(idx, { enunciado: e.target.value })
                }
              />
            </label>

            <label>
              Obligatorio:
              <input
                type="checkbox"
                checked={q.obligatorio}
                onChange={(e) =>
                  updateQuestion(idx, { obligatorio: e.target.checked })
                }
              />
            </label>

            {q.tipo === "texto_libre" && (
              <>
                <h4>Validaciones de texto</h4>
                <label>
                  Longitud mínima:
                  <input
                    type="number"
                    value={q.validaciones?.longitud_minima ?? ""}
                    onChange={(e) => {
                      const v = {
                        ...(q.validaciones || {}),
                        longitud_minima: Number(e.target.value),
                      };
                      updateQuestion(idx, { validaciones: v });
                    }}
                  />
                </label>
                <label>
                  Longitud máxima:
                  <input
                    type="number"
                    value={q.validaciones?.longitud_maxima ?? ""}
                    onChange={(e) => {
                      const v = {
                        ...(q.validaciones || {}),
                        longitud_maxima: Number(e.target.value),
                      };
                      updateQuestion(idx, { validaciones: v });
                    }}
                  />
                </label>
              </>
            )}

            {q.tipo === "escala_numerica" && (
              <>
                <h4>Rango numérico</h4>
                <label>
                  Mínimo:
                  <input
                    type="number"
                    value={q.validaciones?.valor_minimo ?? ""}
                    onChange={(e) => {
                      const v = {
                        ...(q.validaciones || {}),
                        valor_minimo: Number(e.target.value),
                      };
                      updateQuestion(idx, { validaciones: v });
                    }}
                  />
                </label>
                <label>
                  Máximo:
                  <input
                    type="number"
                    value={q.validaciones?.valor_maximo ?? ""}
                    onChange={(e) => {
                      const v = {
                        ...(q.validaciones || {}),
                        valor_maximo: Number(e.target.value),
                      };
                      updateQuestion(idx, { validaciones: v });
                    }}
                  />
                </label>
              </>
            )}

            {(q.tipo === "opcion_multiple" || q.tipo === "checkbox") && (
              <>
                <h4>Opciones</h4>
                {q.opciones.map((opt, i) => (
                  <input
                    key={i}
                    placeholder="Texto de opción"
                    value={opt.texto}
                    onChange={(e) => {
                      const ops = [...q.opciones];
                      ops[i] = { ...ops[i], texto: e.target.value };
                      updateQuestion(idx, { opciones: ops });
                    }}
                  />
                ))}
                <button type="button" onClick={() => addOption(idx)}>
                  + Agregar opción
                </button>
              </>
            )}

            <button
              type="button"
              onClick={() => removeQuestion(idx)}
              style={{ marginTop: "10px", color: "red" }}
            >
              Eliminar pregunta
            </button>
          </div>
        ))}

        <button onClick={addQuestion}>+ Agregar pregunta</button>
        <hr />
        <button onClick={handleSave}>Guardar formulario</button>
      </section>

      {/* ---------------------- Panel lateral derecho ---------------------- */}
      <aside
        style={{
          flex: 1,
          background: "#f7fdfb",
          padding: 15,
          borderRadius: 10,
          border: "1px solid #ccc",
        }}
      >
        <h3>⚙️ Configuración</h3>

        <label>
          Privado:
          <input
            type="checkbox"
            checked={config.privado}
            onChange={(e) =>
              setConfig({ ...config, privado: e.target.checked })
            }
          />
        </label>

        <label>
          Requiere login:
          <input
            type="checkbox"
            checked={config.requerir_login}
            onChange={(e) =>
              setConfig({ ...config, requerir_login: e.target.checked })
            }
          />
        </label>

        <label>
          Notificar por email:
          <input
            type="checkbox"
            checked={config.notificaciones_email}
            onChange={(e) =>
              setConfig({ ...config, notificaciones_email: e.target.checked })
            }
          />
        </label>

        <label>
          Fecha límite:
          <input
            type="date"
            value={config.fecha_limite}
            onChange={(e) =>
              setConfig({ ...config, fecha_limite: e.target.value })
            }
          />
        </label>

        <label>
          Solo una respuesta:
          <input
            type="checkbox"
            checked={config.una_respuesta}
            onChange={(e) =>
              setConfig({ ...config, una_respuesta: e.target.checked })
            }
          />
        </label>

        <label>
          Permitir edición:
          <input
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
