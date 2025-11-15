import React, { useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import confetti from "canvas-confetti";
import "../css/EditSuccess.css";

import celebrationsGirl from "../media/success1.png";
import celebrationsBoy from "../media/success2.png";

const EditSuccess = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const params = new URLSearchParams(location.search);
  const isEditing = params.get("edit") === "true";

  // 🎉 Confetti animación al cargar
  useEffect(() => {
    confetti({
      particleCount: 120,
      spread: 80,
      origin: { y: 0.55 }
    });
  }, []);

  return (
    <main className="success-container">
      <section className="success-card">
        <h1 className="success-title">
          🎉 {isEditing ? "¡Cambios guardados con éxito!" : "¡Respuesta enviada con éxito!"}
        </h1>

        <p className="success-description">
          {isEditing
            ? "Tu respuesta ha sido actualizada correctamente. ¡Gracias por contribuir con nuestro formulario!"
            : "Tu respuesta ha sido registrada correctamente. ¡Gracias por participar!"}
        </p>

        <div className="success-images">
          <img src={celebrationsGirl} alt="Celebración" className="celebration-img" />
          <img src={celebrationsBoy} alt="Celebración" className="celebration-img" />
        </div>

        <button className="success-btn" onClick={() => navigate("/home")}>
          Volver al panel
        </button>
      </section>
    </main>
  );
};

export default EditSuccess;
