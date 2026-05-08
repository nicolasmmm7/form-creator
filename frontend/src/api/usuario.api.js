const API_URL = process.env.REACT_APP_API_URL || "https://form-creator-production.up.railway.app/api";

/**
 *  FUNCIÓN CRÍTICA: Sincroniza usuario de Firebase con MongoDB
 * 
 * ¿Cuándo se llama?
 * - Después de loginWithGoogle() en Login.jsx
 * - Después de loginWithGoogle() en Register.jsx
 * 
 * ¿Qué hace?
 * 1. Envía el ID Token de Firebase al backend Django
 * 2. Backend verifica el token con Firebase Admin SDK
 * 3. Backend busca/crea el usuario en MongoDB
 * 4. Retorna los datos completos del usuario
 * 
 * @param {Object} user - Objeto user de Firebase (uid, email, displayName, photoURL)
 * @param {string} idToken - JWT Token de Firebase para verificación
 * @returns {Promise<Object>} - Datos del usuario desde MongoDB
 */

export const syncFirebaseUser = async (user, idToken) => {
  console.log("🔵 syncFirebaseUser: Iniciando sincronización con backend...");
  console.log("   ├─ UID:", user.uid);
  console.log("   ├─ Email:", user.email);
  console.log("   ├─ Display Name:", user.displayName);
  console.log("   └─ Token (primeros 30 chars):", idToken.substring(0, 30) + "...");

  try {
    const response = await fetch(`${API_URL}/auth/firebase/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        // ¡CRÍTICO! El token debe ir en el header Authorization
        'Authorization': `Bearer ${idToken}`
      },
      body: JSON.stringify({
        nombre: user.displayName || user.email.split('@')[0],
        email: user.email,
        uid: user.uid
      })
    });

    console.log("📡 Respuesta del servidor:", response.status, response.statusText);

    // Verificar si la respuesta es exitosa
    if (!response.ok) {
      const errorData = await response.json();
      console.error("❌ Error del servidor:", errorData);
      throw new Error(errorData.error || `Error del servidor: ${response.status}`);
    }

    const data = await response.json();
    console.log("✅ Sincronización exitosa:", data);

    return data;

  } catch (error) {
    console.error("❌ Error en syncFirebaseUser:", error);
    throw error;
  }
};


/**
 * Función para login tradicional (email/password)
 *
 */
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


/**
 * Función para registrar nuevo usuario (método tradicional)
 * 
 * @param {Object} usuarioData - Datos del usuario a registrar
 * @returns {Promise<Object>} - ID del usuario creado
 */
export const registrarUsuario = async (usuarioData) => {
  console.log("🔵 registrarUsuario: Creando nuevo usuario...");

  try {
    const response = await fetch(`${API_URL}/usuarios/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(usuarioData)
    });

    const data = await response.json();

    if (!response.ok) {
      console.error("❌ Error al crear usuario:", data);
      // 🆕 Lanzar el objeto completo de error para que el frontend pueda leerlo
      const error = new Error(data.error || 'Error al registrar usuario');
      error.data = data;
      throw error;
    }

    console.log("✅ Usuario creado:", data);
    return data;

  } catch (error) {
    console.error("❌ Error en registro:", error);
    throw error;
  }
};


/**
 * Función para obtener datos del usuario actual
 * Requiere token de autenticación
 * 
 * @param {string} idToken - Token de Firebase
 * @returns {Promise<Object>} - Datos del usuario
 */
export const getUserData = async (idToken) => {
  console.log("🔵 getUserData: Obteniendo datos del usuario...");

  try {
    const response = await fetch(`${API_URL}/usuarios/me/`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        Authorization: idToken ? `Bearer ${idToken}` : "",
      },
    });

    const data = await response.json();
    return { ok: response.ok, data };
  } catch (error) {
    console.error("getUserData error:", error);
    return { ok: false, data: { error: "Error de conexión" } };
  }
};


/**
 * Función para actualizar datos del usuario
 * 
 * @param {string} userId - ID del usuario en MongoDB
 * @param {Object} updateData - Datos a actualizar
 * @param {string} idToken - Token de Firebase
 * @returns {Promise<Object>}
 */
export const updateUsuario = async (userId, updateData, idToken) => {
  console.log("🔵 updateUsuario: Actualizando usuario...");

  try {
    const response = await fetch(`${API_URL}/usuarios/${userId}/`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${idToken}`
      },
      body: JSON.stringify(updateData)
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || 'Error al actualizar usuario');
    }

    console.log("✅ Usuario actualizado:", data);
    return data;

  } catch (error) {
    console.error("❌ Error al actualizar:", error);
    throw error;
  }
};

/**
 *  Restablecimiento de contraseña (flujo de dos pasos)
 * 1️ solicitarResetPassword(email) -> envía código al correo
 * 2️ confirmarResetPassword(email, codigo, nuevaClave) -> cambia la contraseña
 */
export const solicitarResetPassword = async (email) => {
  try {
    const response = await fetch(`${API_URL}/usuarios/reset-password/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ action: "solicitar", email }),
    });

    const data = await response.json();
    return { ok: response.ok, data };
  } catch (error) {
    console.error("❌ Error al solicitar código:", error);
    return { ok: false, data: { error: "Error al conectar con el servidor" } };
  }
};

export const confirmarResetPassword = async (email, token, nueva_clave) => {
  try {
    const response = await fetch(`${API_URL}/usuarios/reset-password/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ action: "confirmar", email, token, nueva_clave }),
    });

    const data = await response.json();
    return { ok: response.ok, data };
  } catch (error) {
    console.error("❌ Error al confirmar restablecimiento:", error);
    return { ok: false, data: { error: "Error al conectar con el servidor" } };
  }
};

export const updateUserData = async (userId, updateData, idToken = null) => {
  try {
    const headers = { "Content-Type": "application/json" };
    if (idToken) headers["Authorization"] = `Bearer ${idToken}`;

    const response = await fetch(`${API_URL}/usuarios/${userId}/`, {
      method: "PATCH",
      headers,
      body: JSON.stringify(updateData),
    });

    const data = await response.json();
    return { ok: response.ok, data };
  } catch (error) {
    console.error("updateUserData error:", error);
    return { ok: false, data: { error: "Error de conexión" } };
  }
};


/**
 * 📧 Verificación de email (flujo de dos acciones)
 * 1️⃣ verificarEmail(email, codigo) -> verifica el código OTP y activa la cuenta
 * 2️⃣ reenviarCodigoVerificacion(email) -> reenvía un nuevo código OTP al correo
 */
export const verificarEmail = async (email, token) => {
  try {
    const response = await fetch(`${API_URL}/usuarios/verify-email/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ action: "verificar", email, token }),
    });

    const data = await response.json();
    return { ok: response.ok, data };
  } catch (error) {
    console.error("❌ Error al verificar email:", error);
    return { ok: false, data: { error: "Error al conectar con el servidor" } };
  }
};

export const reenviarCodigoVerificacion = async (email) => {
  try {
    const response = await fetch(`${API_URL}/usuarios/verify-email/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ action: "reenviar", email }),
    });

    const data = await response.json();
    return { ok: response.ok, data };
  } catch (error) {
    console.error("❌ Error al reenviar código:", error);
    return { ok: false, data: { error: "Error al conectar con el servidor" } };
  }
};
