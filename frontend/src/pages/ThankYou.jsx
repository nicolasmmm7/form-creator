import React from "react";
import { useNavigate } from "react-router-dom";
import "../css/CreateForm.css"; // reusar estilos

const ThankYou = () => {
  const navigate = useNavigate();

  return (
    <main className="create-form-main">
      <section className="create-section-main">
        <h2 className="answer-title">🎉 ¡Gracias por responder!</h2>
        <p className="answer-description">
          Tu respuesta ha sido registrada correctamente Papu.  
          Si deseas gestionar tus formularios o crear los tuyos propios,
          inicia sesión con tu cuenta.
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
