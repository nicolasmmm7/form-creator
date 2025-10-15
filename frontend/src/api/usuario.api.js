// src/usuario.api.js
const API_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000'; // URL base del backend Django

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

/**
 * 🔥 Sincronizar usuario de Firebase con backend Django/MongoDB
 * 
 * 1️⃣ Envía el ID Token de Firebase al backend
 * 2️⃣ El backend verifica el token con Firebase Admin SDK
 * 3️⃣ El backend crea/actualiza el usuario en MongoDB
 * 4️⃣ Retorna los datos completos del usuario
 */
export const syncFirebaseUser = async (firebaseUser, idToken) => {
  try {
    console.log("📡 Sincronizando usuario con backend...");
    console.log("Usuario Firebase:", {
      uid: firebaseUser.uid,
      email: firebaseUser.email,
      displayName: firebaseUser.displayName
    });

    // ⚠️ IMPORTANTE: La ruta correcta incluye /api/ SOLO si está definida así en urls.py
    // En la mayoría de casos es /api/auth/firebase/
    console.log("ver el ID Token:", idToken); //para ver cuál se envía y si se envía bien
    const response = await fetch(`${API_URL}/api/auth/firebase/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${idToken}`, // Enviar token en header
      },
      body: JSON.stringify({
        uid: firebaseUser.uid,
        email: firebaseUser.email,
        nombre: firebaseUser.displayName,
        avatar_url: firebaseUser.photoURL,
        empresa: { nombre: "sin_empresa" },
      }),
    });

    // Si el backend devuelve HTML, significa que la ruta está mal (404 o error del servidor)
    const contentType = response.headers.get("content-type");
    if (!contentType || !contentType.includes("application/json")) {
      const text = await response.text();
      console.error("⚠️ Respuesta no JSON del backend:", text);
      throw new Error("Respuesta inválida del backend (no es JSON). Verifica la URL del endpoint.");
    }

    const data = await response.json();

    if (!response.ok) {
      console.error("❌ Error del backend:", data);
      throw new Error(data.error || data.detail || "Error al sincronizar usuario");
    }

    console.log("✅ Usuario sincronizado correctamente:", data);
    return data;

  } catch (error) {
    console.error("❌ Error en syncFirebaseUser:", error);
    throw error;
  }
};
