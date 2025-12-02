import React, { useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import confetti from "canvas-confetti";
import "../css/ThankYou.css";

import celebrationsGirl from "../media/success1.png";
import celebrationsBoy from "../media/success2.png";

const ThankYou = () => {
  const navigate = useNavigate();
  const location = useLocation();

  // 📌 Detectar el parámetro "edit" de la URL
  const params = new URLSearchParams(location.search);
  const isEditing = params.get("edit") === "true";

  // 🎉 Confetti animación al cargar
  useEffect(() => {
    confetti({
      particleCount: 150,
      spread: 90,
      origin: { y: 0.5 },
      colors: ['#4C9A92', '#52C88C', '#F28C8C', '#E8D9D1']
    });
  }, []);

  return (
    <main className="success-container">
      <section className="success-card thankyou-card">
        <div className="success-icon">🎊</div>
        
        <h1 className="success-title">
          {isEditing ? "¡Cambios guardados!" : "¡Gracias por responder!"}
        </h1>

        <p className="success-description">
          {isEditing
            ? "Tu respuesta ha sido actualizada correctamente. Puedes volver a revisar el formulario cuando lo desees."
            : "Tu respuesta ha sido registrada correctamente. Si deseas gestionar tus formularios o crear los tuyos propios, puedes iniciar sesión o registrarte."}
        </p>

        <div className="success-images">
          <img src={celebrationsGirl} alt="Celebración" className="celebration-img" />
          <img src={celebrationsBoy} alt="Celebración" className="celebration-img" />
        </div>

        <div className="success-buttons">
          <button 
            className="success-btn primary" 
            onClick={() => navigate("/login")}
          >
            Iniciar sesión
          </button>
          
          <button 
            className="success-btn secondary" 
            onClick={() => navigate("/register")}
          >
            Registrarme
          </button>
        </div>

        <button 
          className="success-link" 
          onClick={() => navigate("/home")}
        >
          Volver al inicio →
        </button>
      </section>
    </main>
  );
};

export default ThankYou;