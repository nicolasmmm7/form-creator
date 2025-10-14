import axios from 'axios';

const API_URL = 'http://localhost:8000/api/usuarios/'; // Asegúrate de que esta URL coincida con la configuración de tu backend

export const registrarUsuario = async (usuario) => {
  const response = await axios.post(`${API_URL}/registro`, usuario);
  return response.data;
};

export const loginUsuario = async (credenciales) => {
  const response = await axios.post(`${API_URL}/login`, credenciales);
  return response.data;
};

export const obtenerPerfil = async (token) => {
    const response = await axios.get(`${API_URL}/perfil`, {
        headers: { Authorization: `Bearer ${token}` },
    });
    return response.data;
    }