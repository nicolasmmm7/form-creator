// src/components/AuthModal.jsx
import React from "react";
import "../css/AuthModal.css"; // crea estilos simples para el modal

export default function AuthModal({ onClose, onLogin, onRegister, allowGuest }) {
  return (
    <div className="authmodal-backdrop" role="dialog" aria-modal="true">
      <div className="authmodal-card">
        <button className="authmodal-close" onClick={onClose} aria-label="Cerrar">×</button>
        <h3>Acceso requerido</h3>
        <p>Este formulario requiere que inicies sesión para poder responder.</p>

        <div className="authmodal-actions">
          <button className="authmodal-btn" onClick={onLogin}>Iniciar sesión</button>
          <button className="authmodal-btn outline" onClick={onRegister}>Registrarse</button>
          {allowGuest && (
            <button className="authmodal-btn ghost" onClick={onClose}>Continuar como invitado</button>
          )}
        </div>
      </div>
    </div>
  );
}
