// src/pages/verify-email.jsx
import React, { useState } from "react";
import { verificarEmail, reenviarCodigoVerificacion } from "../api/usuario.api";
import { useNavigate, useLocation } from "react-router-dom";

const VerifyEmail = () => {
  const navigate = useNavigate();
  const location = useLocation();

  // Obtener el email desde el state de navegación o query params
  const emailFromState = location.state?.email || "";
  const params = new URLSearchParams(location.search);
  const emailFromQuery = params.get("email") || "";

  const [email] = useState(emailFromState || emailFromQuery);
  const [token, setToken] = useState("");
  const [loading, setLoading] = useState(false);
  const [mensaje, setMensaje] = useState("");
  const [error, setError] = useState("");

  const handleVerificar = async () => {
    if (!token || token.length < 6) {
      setError("Ingresa el código de 6 dígitos.");
      return;
    }

    setLoading(true);
    setError("");
    setMensaje("");

    try {
      const res = await verificarEmail(email, token);
      if (res.ok) {
        setMensaje(res.data.message || "¡Correo verificado exitosamente!");
        // Redirigir al login después de 2 segundos
        setTimeout(() => navigate("/login"), 2000);
      } else {
        setError(res.data.error || "No se pudo verificar el código.");
      }
    } catch (err) {
      console.error(err);
      setError("Error de conexión.");
    } finally {
      setLoading(false);
    }
  };

  const handleReenviar = async () => {
    setLoading(true);
    setError("");
    setMensaje("");

    try {
      const res = await reenviarCodigoVerificacion(email);
      if (res.ok) {
        setMensaje(res.data.message || "Nuevo código enviado al correo.");
      } else {
        setError(res.data.error || "No se pudo reenviar el código.");
      }
    } catch (err) {
      console.error(err);
      setError("Error de conexión.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="verify-email-container">
      <div className="verify-email-icon">✉️</div>
      <h2>Verifica tu correo electrónico</h2>

      <p className="verify-email-desc">
        Enviamos un código de 6 dígitos a<br />
        <strong>{email || "tu correo"}</strong>
      </p>

      {error && <div className="verify-email-error">{error}</div>}
      {mensaje && <div className="verify-email-success">{mensaje}</div>}

      <input
        type="text"
        id="verify-email-code"
        placeholder="Código de verificación"
        value={token}
        onChange={(e) => {
          // Solo permitir dígitos, máximo 6
          const val = e.target.value.replace(/\D/g, "").slice(0, 6);
          setToken(val);
        }}
        maxLength={6}
        autoComplete="one-time-code"
        disabled={loading}
      />

      <button
        id="verify-email-btn-submit"
        onClick={handleVerificar}
        disabled={loading || token.length < 6}
      >
        {loading ? "Verificando..." : "Verificar cuenta"}
      </button>

      <button
        className="verify-email-resend"
        type="button"
        onClick={handleReenviar}
        disabled={loading}
      >
        ¿No recibiste el código? Reenviar
      </button>

      <button
        className="verify-email-back"
        type="button"
        onClick={() => navigate("/login")}
      >
        Volver al login
      </button>
    </div>
  );
};

export default VerifyEmail;
