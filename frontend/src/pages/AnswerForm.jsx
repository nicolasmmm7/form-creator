// src/pages/AnswerForm.jsx
import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import "../css/CreateForm.css"; // reutilizamos el mismo estilo

function AnswerForm() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [formulario, setFormulario] = useState(null);
  const [respuestas, setRespuestas] = useState({});
  const [mensaje, setMensaje] = useState("");

  useEffect(() => {
    fetch(`http://127.0.0.1:8000/api/formularios/${id}/`)
      .then((res) => res.json())
      .then((data) => setFormulario(data))
      .catch((err) => console.error(err));
  }, [id]);

  const handleChange = (pid, tipo, value) => {
    setRespuestas((prev) => ({
      ...prev,
      [pid]: { tipo, valor: value },
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!formulario) return;

    const payload = {
      formulario: id,
      respondedor: { ip_address: "frontend-ip" },
      tiempo_completacion: 30,
      respuestas: Object.entries(respuestas).map(([pid, { tipo, valor }]) => ({
        pregunta_id: Number(pid),
        tipo,
        valor: Array.isArray(valor) ? valor : [valor],
      })),
    };

    const res = await fetch("http://127.0.0.1:8000/api/respuestas/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const data = await res.json();
    if (res.ok) {
        setMensaje("✅ ¡Respuesta enviada correctamente!");
        const userData = JSON.parse(localStorage.getItem("user"));
        setTimeout(() => {
        if (userData?.id) {
            navigate("/home");
        } else {
            navigate("/thankyou");
        }
        }, 2000);
    } else {
        setMensaje(`⚠️ Error: ${data.error || JSON.stringify(data)}`);
    }
    };

  if (!formulario) return <div className="create-section-main">Cargando formulario...</div>;

  return (
    <main className="create-form-main">
      {/* ===== Botón Volver ===== */}
      <div className="create-back-container">
        <button
          className="create-btn-back"
          onClick={() => navigate("/home")}
        >
          <span className="create-back-arrow">←</span>
          Volver
        </button>
      </div>

      {/* ===== Sección principal ===== */}
      <section className="create-section-main">
        {/*<h3>Responder formulario</h3>  me parece redundante*/}

        {/* Header del formulario */}
        {/* ===== Encabezado del formulario ===== */}
        <section className="answer-header">
        <h2 className="answer-title">{formulario.titulo}</h2>
        {formulario.descripcion && (
            <p className="answer-description">{formulario.descripcion}</p>
        )}
        </section>

        <h3>Preguntas</h3>
        {formulario.preguntas.map((p, idx) => (
          <div key={p.id} className="create-question-card">
            <label className="create-label">
              {`${idx + 1}. ${p.enunciado}`}
              {p.obligatorio && <span style={{ color: "red" }}> *</span>}
            </label>

            {/* ===== Tipo texto libre ===== */}
            {p.tipo === "texto_libre" && (
              <input
                className="create-input"
                type="text"
                placeholder="Tu respuesta..."
                onChange={(e) => handleChange(p.id, p.tipo, e.target.value)}
              />
            )}

            {/* ===== Tipo opción múltiple ===== */}
            {p.tipo === "opcion_multiple" && (
            <div className="create-options">
                <h4>Selecciona una opción</h4>
                {p.opciones.map((o) => (
                <div key={o.valor} className="create-option-row">
                    <input
                    type="radio"
                    name={`pregunta_${p.id}`}
                    className="create-checkbox"
                    value={o.texto}
                    onChange={(e) => handleChange(p.id, p.tipo, e.target.value)}
                    />
                    <label className="create-label">{o.texto}</label>
                </div>
                ))}
            </div>
            )}

            {/* ===== Tipo checkbox ===== */}
            {p.tipo === "checkbox" && (
              <div className="create-options">
                <h4>Selecciona una o más opciones</h4>
                {p.opciones.map((o) => (
                  <div key={o.valor} className="create-option-row">
                    <input
                      type="checkbox"
                      className="create-checkbox"
                      value={o.texto}
                      onChange={(e) => {
                        const current = respuestas[p.id]?.valor || [];
                        if (e.target.checked)
                          handleChange(p.id, p.tipo, [...current, e.target.value]);
                        else
                          handleChange(p.id, p.tipo, current.filter((v) => v !== e.target.value));
                      }}
                    />
                    <label className="create-label">{o.texto}</label>
                  </div>
                ))}
              </div>
            )}

            {/* ===== Tipo escala numérica ===== */}
            {p.tipo === "escala_numerica" && (
              <div className="create-validations">
                <h4>Selecciona un valor numérico</h4>
                <input
                  className="create-input"
                  type="number"
                  min={p.validaciones.valor_minimo || 0}
                  max={p.validaciones.valor_maximo || 10}
                  onChange={(e) => handleChange(p.id, p.tipo, e.target.value)}
                />
              </div>
            )}
          </div>
        ))}

        <hr className="create-divider" />

        {/* Botón enviar respuesta */}
        <button type="submit" className="create-btn-save" onClick={handleSubmit}>
          Enviar respuestas
        </button>

        {mensaje && (
          <p style={{ marginTop: "1rem", color: "green", fontWeight: "600" }}>
            {mensaje}
          </p>
        )}
      </section>

      {/* ===== Panel lateral ===== */}
        <aside className="create-sidebar">
        <h3 className="create-sidebar-title">🧾 Detalles</h3>
        <div className="create-config-group">
            <label className="create-config-label">
            <strong>Privado:</strong> {formulario.configuracion?.privado ? "Sí" : "No"}
            </label>
            <label className="create-config-label">
            <strong>Requiere login:</strong> {formulario.configuracion?.requerir_login ? "Sí" : "No"}
            </label>
            <label className="create-config-label">
            <strong>Fecha límite:</strong>{" "}
            {formulario.configuracion?.fecha_limite || "Sin límite"}
            </label>
            <label className="create-config-label">
            <strong>Respuestas múltiples:</strong>{" "}
            {formulario.configuracion?.una_respuesta ? "No" : "Sí"}
            </label>
        </div>
        </aside>
    </main>
  );
}

export default AnswerForm;
