import React, { useState } from "react";
import { solicitarResetPassword, confirmarResetPassword } from "../api/usuario.api";

const PasswordReset = () => {
  const [step, setStep] = useState(1); // 1: solicitar, 2: confirmar
  const [email, setEmail] = useState("");
  const [token, setToken] = useState("");
  const [newPassword, setNewPassword] = useState("");

  const handleSolicitar = async () => {
    const res = await solicitarResetPassword(email);
    if (res.ok) setStep(2);
    alert(res.data.message || res.data.error);
  };

  const handleConfirmar = async () => {
    const res = await confirmarResetPassword(email, token, newPassword);
    alert(res.data.message || res.data.error);
  };

  return (
    <div className="reset-container">
      <h2>Restablecer contraseña</h2>

      {step === 1 && (
        <>
          <p>Ingresa tu correo para recibir un código:</p>
          <input
            type="email"
            placeholder="Correo electrónico"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
          <button onClick={handleSolicitar}>Enviar código</button>
        </>
      )}

      {step === 2 && (
        <>
          <p>Revisa tu correo y escribe el código recibido:</p>
          <input
            type="text"
            placeholder="Código de verificación"
            value={token}
            onChange={(e) => setToken(e.target.value)}
          />
          <input
            type="password"
            placeholder="Nueva contraseña"
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
          />
          <button onClick={handleConfirmar}>Cambiar contraseña</button>
        </>
      )}
    </div>
  );
};

export default PasswordReset;
