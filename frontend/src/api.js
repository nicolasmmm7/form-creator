// src/api.js
const API_URL = "http://127.0.0.1:8000/api"; // URL base del backend Django

export const registrarUsuario = async (usuarioData) => {
  try {
    const response = await fetch(`${API_URL}/usuarios/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(usuarioData),
    });
    return await response.json();
  } catch (error) {
    console.error("❌ Error al registrar usuario:", error);
    throw error;
  }
};

export const loginUsuario = async (email, password) => {
  try {
    const response = await fetch(`${API_URL}/usuarios/login/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, clave_hash: password }),
    });

    const data = await response.json();
    return { ok: response.ok, data };
  } catch (error) {
    console.error("❌ Error al iniciar sesión:", error);
    return { ok: false, data: { error: "Error de conexión con el servidor" } };
  }
};
