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

// ✅ Función de login con Google
export const loginWithGoogle = async () => {
  try {
    console.log("🔵 Iniciando autenticación con Google...");
    
    // Abrir popup de Google OAuth
    const result = await signInWithPopup(auth, provider);
    console.log("✅ Usuario autenticado:", result.user);
    return result.user;
  } catch (error) {
    console.error("❌ Error al iniciar sesión con Google:", error.message);
  }

};

// Exportar auth y provider por si los necesitas luego
export { auth, provider };
