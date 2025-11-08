// src/pages/AnswerForm.jsx
import { useEffect, useState } from "react";
import { useParams, useNavigate, useLocation } from "react-router-dom";
import "../css/CreateForm.css"; // reutilizamos el mismo estilo
import AuthModal from "../components/AuthModal"; //modal para cuando el form requiere login
import AnswerEditModal from "../components/AnswerEditModal";



function AnswerForm() {
  const { id } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
  const [formulario, setFormulario] = useState(null);
  const [respuestas, setRespuestas] = useState({});
  const [mensaje, setMensaje] = useState("");
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [existingResponse, setExistingResponse] = useState(null);
  const [isEditing, setIsEditing] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [modalDismissed, setModalDismissed] = useState(false);

  function Modal({ visible, title, message, onClose, actionLabel, onAction }) {
  if (!visible) return null;
  return (
    <div className="modal-overlay">
      <div className="modal-container">
        <h3>{title}</h3>
        <p>{message}</p>
        <div className="modal-actions">
          <button className="modal-btn-close" onClick={onClose}>Cerrar</button>
          {onAction && (
            <button className="modal-btn-action" onClick={onAction}>
              {actionLabel || "Acción"}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

// === Función para precargar respuestas existentes ===
  const precargarRespuestas = (respuestaExistente) => {
    if (!respuestaExistente || !respuestaExistente.respuestas) return;

    const respuestasPrecargadas = {};
    respuestaExistente.respuestas.forEach((r) => {
      respuestasPrecargadas[r.pregunta_id] = {
        tipo: r.tipo,
        valor: r.valor?.length > 1 ? r.valor : r.valor[0],
      };
    });

    setRespuestas(respuestasPrecargadas);
  };

 
 useEffect(() => {
  const user = JSON.parse(localStorage.getItem("user") || "null");
  const ip = localStorage.getItem("client_ip") || "frontend-ip";
  fetch(`http://127.0.0.1:8000/api/formularios/${id}/`)
    .then(res => res.json())
    .then(data => {
      setFormulario(data);

    //verificar si ya respondio
    fetch(`http://127.0.0.1:8000/api/respuestas/?formulario=${id}`)
      .then((res) => res.json())
      .then((data) => {
        const match = data.find((r) =>
          user?.email
            ? r.respondedor.email === user.email
            : r.respondedor.ip_address === ip
        );
        if (match) {
          setExistingResponse(match);
          setShowModal(true);
        }
      });

      const hoy = new Date();
      const fechaLimite = data.configuracion?.fecha_limite
        ? new Date(data.configuracion.fecha_limite)
        : null;

      // 1️⃣ Formulario cerrado por fecha límite
      if (fechaLimite && fechaLimite < hoy) {
        setModal({
          visible: true,
          title: "Formulario cerrado 🕒",
          message: "Este formulario ya no acepta respuestas porque la fecha límite ha pasado.",
          action: () => navigate("/home"),
        });
        return;
      }

      // 2️⃣ Formulario no publicado (privado = true)
      if (data.configuracion?.privado === true) {
        setModal({
            visible: true,
            title: "Formulario no disponible 🚫",
            message: "El creador ha despublicado este formulario. Ya no puedes enviar respuestas.",
            action: () => navigate("/home"),
        });
        return;
        }

      
    })
    .catch(err => console.error(err));
}, [id, navigate]);


  // Recuperar respuestas pendientes si hay (después de login)
  useEffect(() => {
    const pending = localStorage.getItem(`pending_answers_${id}`);
    if (pending) {
      try {
        setRespuestas(JSON.parse(pending));
        // opcional: eliminar pending si ya lo quieras limpiar
        // localStorage.removeItem(`pending_answers_${id}`);
      } catch (e) {}
    }
  }, [id]);

  // Auto-mostrar modal si el formulario requiere login y no hay user
  useEffect(() => {
    if (!formulario) return;
    const requiereLogin = formulario.configuracion?.requerir_login;
    const user = JSON.parse(localStorage.getItem("user") || "null");
    if (requiereLogin && !user) {
      setShowAuthModal(true);
    }
  }, [formulario]);

  // Validación: devuelve true si hay un usuario o no se requiere login
  function validateLogin() {
    const requiereLogin = formulario?.configuracion?.requerir_login;
    const user = JSON.parse(localStorage.getItem("user") || "null");
    return !requiereLogin || !!user;
  }


  const handleChange = (pid, tipo, value) => {
    setRespuestas((prev) => ({
      ...prev,
      [pid]: { tipo, valor: value },
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!formulario) return;

    // Si requiere login y no está logueado -> abrir modal y guardar respuestas
    if (!validateLogin()) {
      // guarda estado actual para recuperarlo luego
      localStorage.setItem(`pending_answers_${id}`, JSON.stringify(respuestas));
      setShowAuthModal(true);
      return;
    }

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

    const url = isEditing
  ? `http://127.0.0.1:8000/api/respuestas/${existingResponse.id}/`
  : "http://127.0.0.1:8000/api/respuestas/";
  const method = isEditing ? "PUT" : "POST";


    const res = await fetch(url, {
      method,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });



    const data = await res.json();
    if (res.ok) {
        setMensaje("✅ ¡Respuesta enviada correctamente!");
        localStorage.removeItem(`pending_answers_${id}`); //limpiar pending si existía (esto lo agregó angely perdón si esta mal)
        const userData = JSON.parse(localStorage.getItem("user"));
        // Redirigir según si hay user o no
        if (userData?.id) {
            navigate("/home");
        } else {
            navigate(`/thankyou?edit=${isEditing}`);
        }
      } else if (res.status === 401) {
      // backend puede rechazar con 401 -> abrir modal
      localStorage.setItem(`pending_answers_${id}`, JSON.stringify(respuestas));
      setShowAuthModal(true);
    } else {
      setMensaje(`⚠️ Error: ${data.error || JSON.stringify(data)}`);
    }
  };



    const [modal, setModal] = useState({
        visible: false,
        title: "",
        message: "",
        action: null,
    });




  if (!formulario) return <div className="create-section-main">Cargando formulario...</div>;

  if (modal.visible) {
  return (
    <Modal
      visible={modal.visible}
      title={modal.title}
      message={modal.message}
      onClose={() => navigate("/home")}
      onAction={modal.action}
      actionLabel="Ir"
    />
  );
}


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

       <AnswerEditModal
  visible={showModal}
  onClose={() => {
    setShowModal(false);
    setModalDismissed(true); // evita que el useEffect lo vuelva a abrir
  }}
>
  {existingResponse && (
    <>
      <h2 className="text-xl font-semibold mb-2">Ya has respondido este formulario</h2>

      {formulario?.configuracion?.permitir_edicion ? (
        <>
          <p className="mb-4">Puedes editar tu respuesta anterior. ¿Deseas hacerlo ahora?</p>
          <div className="flex gap-2">
            <button
              onClick={() => {
                setIsEditing(true);
                precargarRespuestas(existingResponse);
                setShowModal(false);
              }}
              className="bg-blue-500 text-white px-4 py-2 rounded"
            >
              Editar mi respuesta
            </button>
            <button
              onClick={() => {
                setModalDismissed(true);
                navigate("/")}}
              className="bg-gray-400 text-white px-4 py-2 rounded"
              
            >
              Cancelar
            </button>
          </div>
        </>
      ) : (
        <>
          <p className="mb-4">
            Ya completaste este formulario y no se permiten nuevas respuestas.
          </p>
          <button
            onClick={() => navigate("/")}
            className="bg-gray-500 text-white px-4 py-2 rounded"
          >
            Volver al inicio
          </button>
        </>
      )}
    </>
  )}
</AnswerEditModal>

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

         {/* Modal de autenticación */}
      {showAuthModal && (
        <AuthModal
          onClose={() => setShowAuthModal(false)}
          onLogin={() => {
            // Guardar pending y redirigir al login con next
            localStorage.setItem(`pending_answers_${id}`, JSON.stringify(respuestas));
            navigate(`/login?next=/form/${id}/answer`);
          }}
          onRegister={() => {
            localStorage.setItem(`pending_answers_${id}`, JSON.stringify(respuestas));
            navigate(`/register?next=/form/${id}/answer`);

          }}
          allowGuest={!formulario.configuracion?.requerir_login && !formulario.configuracion?.privado}
        />
      )}

    </main>
  );
}

export default AnswerForm;
