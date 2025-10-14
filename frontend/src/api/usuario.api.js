import axios from 'axios'; //librería para hacer peticiones HTTP

const API_URL = 'http://localhost:8000/api/usuarios/'; //de aquí papus se conecta con el backend (la url es del backend de usuarios)

export const registrarUsuario = async (usuario) => {
  const response = await axios.post(`${API_URL}/registro`, usuario); //envía una petición POST a la URL de registro con los datos del usuario
  return response.data;
};

export const loginUsuario = async (credenciales) => {
  const response = await axios.post(`${API_URL}/login`, credenciales); //envía una petición POST a la URL de login con las credenciales del usuario
  return response.data;
};

export const obtenerPerfil = async (token) => {  
    const response = await axios.get(`${API_URL}/perfil`, {  //envía una petición GET a la URL de perfil //todavia no toy segura si es así
        headers: { Authorization: `Bearer ${token}` }, //envía el token en los headers para autenticar la petición
    });
    return response.data;  //devuelve los datos del perfil del usuario
    }

    //en api basicamente se hacen las peticiones al backend, se encarga de comunicar con el servidor y traer o enviar datos, bueno creo que esto se intuye porque se llama API xd xd xd 
    //aclarar que solo hay peticiones de usuarios porque es usuario.api.js, si hubiera otro tipo de datos (formularios, respuestas, etc) habria otro archivo api para cada uno
    //ademas: SOLO PETICIONES, nada de funcionalidades, lógicas, etc. Solo peticiones al backend