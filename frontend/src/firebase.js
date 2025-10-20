// src/firebase.js
import { initializeApp } from "firebase/app";
import { getAuth, GoogleAuthProvider, signInWithPopup } from "firebase/auth";

// ==========================================
// CONFIGURACIÓN DE FIREBASE
// ==========================================
// Estos datos vienen de Firebase Console
const firebaseConfig = {
  apiKey: process.env.REACT_APP_API_KEY,
  authDomain: "formcreator-87594.firebaseapp.com",
  projectId: "formcreator-87594",
  storageBucket: "formcreator-87594.firebasestorage.app",
  messagingSenderId: "190236889711",
  appId: "1:190236889711:web:085fa6f8f65845821d339a",
  measurementId: "G-HPBP2TTS02"
};

// Inicializar Firebase en el cliente
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const provider = new GoogleAuthProvider();

// Configuración adicional del provider de Google
provider.setCustomParameters({
  prompt: 'select_account'  // Forzar selección de cuenta cada vez
});

/**
 * Función para iniciar sesión con Google
 * 
 * ¿Qué hace?
 * 1. Abre popup de Google para seleccionar cuenta
 * 2. Usuario autoriza la aplicación
 * 3. Firebase devuelve objeto user con datos
 * 4. Genera un ID Token JWT para verificar en backend
 * 5. Retorna user y idToken para sincronizar con MongoDB
 * 
 * @returns {Promise<{user: Object, idToken: string}>}
 */
export const loginWithGoogle = async () => {
  try {
    console.log("🔵 Iniciando autenticación con Google...");
    
    // Abrir popup de Google OAuth
    const result = await signInWithPopup(auth, provider);
    const user = result.user;
    
    // ===============================================
    // OBTENER ID TOKEN (CRÍTICO)
    // ===============================================
    // Este token es un JWT que contiene:
    // - uid: ID único del usuario en Firebase
    // - email: Email verificado por Google
    // - exp: Timestamp de expiración (1 hora)
    // - Firma digital para verificar autenticidad
    const idToken = await user.getIdToken();
    
    console.log("✅ Usuario autenticado:", {
      uid: user.uid,
      email: user.email,
      displayName: user.displayName
    });
    
    console.log("🔑 ID Token obtenido (primeros 50 chars):", idToken.substring(0, 10) + "...");
    
    // Retornar datos para el componente
    return { user, idToken };
    
  } catch (error) {
    console.error("❌ Error al iniciar sesión con Google:", error);
    
    // Manejar errores específicos
    if (error.code === 'auth/popup-closed-by-user') {
      throw new Error('Popup cerrado. Por favor intenta nuevamente.');
    } else if (error.code === 'auth/cancelled-popup-request') {
      throw new Error('Operación cancelada.');
    } else {
      throw new Error(`Error: ${error.message}`);
    }
  }
};

// Exportar para usar en otros archivos
export { auth, provider };
