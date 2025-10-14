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

