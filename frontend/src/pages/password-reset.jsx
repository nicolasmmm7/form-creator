import React, { useState } from "react";
import { solicitarResetPassword, confirmarResetPassword } from "../api/usuario.api";
import { useNavigate } from "react-router-dom";

const PasswordReset = () => {
  const [step, setStep] = useState(1); // 1: solicitar, 2: confirmar
  const [email, setEmail] = useState("");
  const [token, setToken] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSolicitar = async () => {
    setLoading(true);
    try {
      const res = await solicitarResetPassword(email);
      if (res.ok) {
        setStep(2);
        alert(res.data.message || "Código enviado al correo");
      } else {
        alert(res.data.error || "No se pudo enviar el código");
      }
    } catch (err) {
      console.error(err);
      alert("Error de conexión");
    } finally {
      setLoading(false);
    }
  };

  const handleConfirmar = async () => {
    setLoading(true);
    try {
      const res = await confirmarResetPassword(email, token, newPassword);
      if (res && res.ok) {
        alert(res.data.message || "Contraseña cambiada correctamente");
        navigate("/login");
      } else {
        alert((res && res.data && (res.data.error || res.data.message)) || "No se pudo cambiar la contraseña");
      }
    } catch (err) {
      console.error(err);
      alert("Error de conexión");
    } finally {
      setLoading(false);
    }
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
          <button onClick={handleSolicitar} disabled={loading || !email}>
            {loading ? "Enviando..." : "Enviar código"}
          </button>
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
          <button
            onClick={handleConfirmar}
            disabled={loading || !token || !newPassword}
          >
            {loading ? "Procesando..." : "Cambiar contraseña"}
          </button>
        </>
      )}
      <button 
      className="secondary-link"
        type="button"
        onClick={() => navigate("/login")}>
          Volver al login
      </button>
    </div>
  );
};

export default PasswordReset;