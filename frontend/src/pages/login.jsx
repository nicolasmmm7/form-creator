import React, { useState, useEffect } from "react";
import { loginWithGoogle } from "../firebase";
import { useNavigate, useLocation, Link } from "react-router-dom";
import { loginUsuario, syncFirebaseUser } from "../api/usuario.api";

const Login = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const params = new URLSearchParams(location.search);
  const next = params.get("next") || "/home";
  
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [isCheckingAuth, setIsCheckingAuth] = useState(true);

  // ====================================================
  // 🔍 VERIFICAR SESIÓN EXISTENTE AL CARGAR
  // ====================================================
  useEffect(() => {
    const checkExistingSession = () => {
      const storedUser = localStorage.getItem("user");
      const storedToken = localStorage.getItem("idToken");
      
      if (storedUser && storedToken) {
        console.log("✅ Sesión existente encontrada, redirigiendo...");
        navigate(next);
      }
      setIsCheckingAuth(false);
    };

    checkExistingSession();
  }, [navigate, next]);

  // ====================================================
  // 📧 LOGIN TRADICIONAL (Email/Password)
  // ====================================================
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const result = await loginUsuario(email, password);

      if (result.ok) {
        alert(`✅ Bienvenido ${result.data.usuario.nombre}`);
        console.log("Usuario logueado:", result.data.usuario);

        // Guardar usuario en localStorage
        localStorage.setItem("user", JSON.stringify(result.data.usuario));
        localStorage.setItem("signin_provider", "normal");

        navigate(next);
      } else {
        alert("❌ Error: " + (result.data.error || "Credenciales incorrectas"));
      }
    } catch (error) {
      console.error("Error en login tradicional:", error);
      alert("Error al iniciar sesión");
    } finally {
      setLoading(false);
    }
  };

  // ====================================================
  // 🔵 LOGIN CON GOOGLE
  // ====================================================
  /**
   * FLUJO COMPLETO DE LOGIN CON GOOGLE:
   * 
   * 1. loginWithGoogle() abre popup de autenticación de Google
   * 2. Firebase autentica y devuelve:
   *    - user (con uid, email, displayName, photoURL)
   *    - idToken (JWT para autenticar con backend)
   * 3. syncFirebaseUser() sincroniza usuario con backend Django/MongoDB
   * 4. Backend busca/crea usuario en base de datos
   * 5. Enriquecemos datos del usuario con photoURL de Firebase
   * 6. Guardamos todo en localStorage (user + idToken + imagen)
   * 7. Redirigimos a /home
   */
  const handleGoogleLogin = async () => {
    setLoading(true);
    
    try {
      console.log("🔵 PASO 1: Iniciando autenticación con Google...");
      const { user, idToken } = await loginWithGoogle();

      if (!user) {
        alert("No se pudo autenticar el usuario con Google");
        setLoading(false);
        return;
      }

      console.log("✅ PASO 2: Usuario autenticado en Firebase");
      console.log("Datos del usuario de Firebase:", {
        uid: user.uid,
        email: user.email,
        displayName: user.displayName,
        photoURL: user.photoURL // 👈 ESTA ES LA IMAGEN DE GOOGLE
      });

      console.log("🔵 PASO 3: Sincronizando con backend Django/MongoDB...");
      const resultado = await syncFirebaseUser(user, idToken);

      if (resultado?.success && resultado?.user) {
        console.log("✅ PASO 4: Usuario sincronizado correctamente");
        console.log("Datos desde MongoDB:", resultado.user);
        
        // ====================================================
        // 🎯 SOLUCIÓN CRÍTICA: ENRIQUECER CON IMAGEN DE GOOGLE
        // ====================================================
        // El backend puede no tener la imagen actualizada o no devolverla
        // Por eso tomamos photoURL directamente de Firebase
        const userWithImage = {
          ...resultado.user,
          perfil: {
            ...resultado.user.perfil,
            // Prioridad: photoURL de Firebase > avatar_url del backend > string vacío
            avatar_url: user.photoURL || resultado.user.perfil?.avatar_url || ''
          },
          // Agregar metadatos útiles de Firebase
          firebase_uid: user.uid,
          auth_provider: 'google',
          displayName: user.displayName,
          provider: 'google'
        };

        console.log("📸 Usuario con imagen incluida:", userWithImage);
        console.log("🖼️ URL de imagen:", userWithImage.perfil.avatar_url);
        
        // ====================================================
        // 💾 GUARDAR EN LOCALSTORAGE
        // ====================================================
        localStorage.setItem('user', JSON.stringify(userWithImage));
        localStorage.setItem('idToken', idToken);
        localStorage.setItem('signin_provider', 'google'); // Marcar como usuario de Google
        
        console.log("✅ Datos guardados en localStorage");
        
        alert(`✅ Bienvenido ${userWithImage.nombre || user.displayName}!`);
        navigate(next);
      } else {
        alert("Error al iniciar sesión con Google. Revisa la consola.");
        console.error("❌ Error en respuesta del backend:", resultado);
      }

    } catch (error) {
      console.error("🔥 Error en login con Google:", error);
      alert("Error al iniciar sesión con Google: " + error.message);
    } finally {
      setLoading(false);
    }
  };

  // ====================================================
  // ⏳ PANTALLA DE CARGA INICIAL
  // ====================================================
  if (isCheckingAuth) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh',
        fontSize: '18px',
        color: '#6366f1',
        flexDirection: 'column',
        gap: '20px'
      }}>
        <div style={{
          width: '40px',
          height: '40px',
          border: '4px solid #e5e7eb',
          borderTop: '4px solid #6366f1',
          borderRadius: '50%',
          animation: 'spin 1s linear infinite'
        }} />
        <p>Verificando sesión...</p>
        <style>{`
          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
        `}</style>
      </div>
    );
  }

  // ====================================================
  // 🎨 FORMULARIO DE LOGIN
  // ====================================================
  return (
    <main id="main-login">
      <section id="login-section">
        <h1 id="login-titulo">Iniciar Sesión</h1>
        <form id="login-form" onSubmit={handleSubmit}>
          <label htmlFor="login-email">Correo electrónico</label>
          <input
            type="email"
            id="login-email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            disabled={loading}
          />

          <label htmlFor="login-password">Contraseña</label>
          <input
            type="password"
            id="login-password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            disabled={loading}
          />

          <button id="login-btn-submit" type="submit" disabled={loading}>
            {loading ? "Ingresando..." : "Ingresar"}
          </button>

          <button
            id="login-btn-google"
            type="button"
            onClick={handleGoogleLogin}
            disabled={loading}
            aria-label="Iniciar sesión con Google"
            className="google-btn"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="20"
              height="20"
              viewBox="0 0 48 48"
              style={{ marginRight: "8px" }}
            >
              <path
                fill="#EA4335"
                d="M24 9.5c3.94 0 7.13 1.62 9.3 3.29l6.89-6.89C36.84 2.32 30.9 0 24 0 14.8 0 6.8 5.47 2.9 13.42l7.97 6.19C12.47 13.1 17.77 9.5 24 9.5z"
              />
              <path
                fill="#34A853"
                d="M46.5 24.48c0-1.61-.14-3.15-.4-4.65H24v9.05h12.76c-.55 2.8-2.2 5.15-4.64 6.74l7.12 5.51c4.13-3.82 6.26-9.46 6.26-16.65z"
              />
              <path
                fill="#FBBC05"
                d="M10.87 28.73a14.25 14.25 0 01-.75-4.73c0-1.65.27-3.24.76-4.74L2.9 13.42A23.94 23.94 0 000 24c0 3.9.93 7.58 2.57 10.58l8.3-5.85z"
              />
              <path
                fill="#4285F4"
                d="M24 48c6.49 0 11.94-2.15 15.92-5.86l-7.12-5.51c-1.96 1.35-4.46 2.2-7.16 2.20-6.23 0-11.52-4.1-13.77-9.78l-8.3 5.85C6.8 42.53 14.8 48 24 48z"
              />
            </svg>
            {loading ? "Procesando..." : "Iniciar sesión con Google"}
          </button>

          <p id="login-texto-registro">
            <Link to="/password-reset">¿Olvidaste tu contraseña?</Link>
          </p>
          <p id="login-texto-registro">
            ¿Sin cuenta? <Link to={`/register?next=${encodeURIComponent(next)}`}>Regístrate aquí</Link>
          </p>
        </form>
      </section>
    </main>
  );
};

export default Login;