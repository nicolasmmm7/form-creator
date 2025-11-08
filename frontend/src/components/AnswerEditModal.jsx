// src/components/Modal.jsx
import React from "react";
import "../css/CreateForm.css";

const AnswerEditModal = ({ visible, title, message, onClose, actionLabel, onAction, children }) => {
  if (!visible) return null;

  return (
    <div className="modal-overlay">
      <div className="modal-container">
        {title && <h3>{title}</h3>}
        {message && <p>{message}</p>}
        {children}
        <div className="modal-actions">
          <button className="modal-btn-close" onClick={onClose}>
            Cerrar
          </button>
          {onAction && (
            <button className="modal-btn-action" onClick={onAction}>
              {actionLabel || "Aceptar"}
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default AnswerEditModal;
