import React from "react";
import "../css/AnswerEditModal.css";

const AnswerEditModal = ({
  visible,
  title,
  message,
  onClose,
  onAction,
  actionLabel,
  children,
}) => {
  if (!visible) return null;

  return (
    <>
      {/* Fondo semitransparente */}
      <div className="answer-edit-modal-overlay"></div>

      {/* Contenedor de la modal */}
      <div className="answer-edit-modal">
        {title && <h2>{title}</h2>}
        {message && <p>{message}</p>}

        {/* Contenido adicional */}
        {children && <div className="modal-content">{children}</div>}

        {/* Botones */}
        <div className="modal-buttons">
          <button className="btn-secondary" onClick={onClose}>
            Cerrar
          </button>
          {onAction && (
            <button className="btn-primary" onClick={onAction}>
              {actionLabel || "Aceptar"}
            </button>
          )}
        </div>
      </div>
    </>
  );
};

export default AnswerEditModal;
