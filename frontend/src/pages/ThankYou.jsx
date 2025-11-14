import React from "react";
import { useNavigate, useLocation } from "react-router-dom";
import "../css/CreateForm.css"; // reusar estilos

const ThankYou = () => {
  const navigate = useNavigate();
  const location = useLocation();

   // 📌 Detectar el parámetro "edit" de la URL
  const params = new URLSearchParams(location.search);
  const isEditing = params.get("edit") === "true";

  return (
    <main className="create-form-main">
      <section className="create-section-main">
        <h2 className="answer-title">🎉 ¡Gracias por {isEditing ? "actualizar tu respuesta" : "responder"}!</h2>
        <p className="answer-description">
          {isEditing
            ? "Tus cambios han sido guardados correctamente. Puedes volver a revisar el formulario si lo deseas."
            : "Tu respuesta ha sido registrada correctamente Papu. Si deseas gestionar tus formularios o crear los tuyos propios, inicia sesión con tu cuenta."}
        </p>
        <button
          className="create-btn-primary"
          onClick={() => navigate("/login")}
        >
          Iniciar sesión
        </button>
      </section>
    </main>
  );
};



export default ThankYou;
