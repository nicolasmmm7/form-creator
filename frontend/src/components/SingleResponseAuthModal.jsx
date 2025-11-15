import React from "react";
import "../css/AuthModal.css";

export default function SingleResponseAuthModal({ onLogin }) {
  return (
    <div className="authmodal-backdrop" role="dialog" aria-modal="true">
      <div className="authmodal-card">
        <h3>Respuesta única</h3>
        <p>
          Este formulario solo permite <strong>una respuesta por usuario</strong>.  
          Para continuar, debes iniciar sesión.
        </p>

        <div className="authmodal-actions">
          <button className="authmodal-btn" onClick={onLogin}>
            Iniciar sesión
          </button>
        </div>
      </div>
    </div>
  );
}
