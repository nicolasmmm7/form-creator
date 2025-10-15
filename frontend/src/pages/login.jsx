// src/pages/Login.jsx
import React, { useState } from "react";
import { loginWithGoogle } from "../firebase";
import { useNavigate, Link } from "react-router-dom";
import { loginUsuario, syncFirebaseUser } from "../api/usuario.api";

const Login = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  /**
   * Maneja el login tradicional (email/password)
   */
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
  const result = await loginUsuario(email, password);

  if (result.ok) {
    // Detectar si los datos vienen dentro de "usuario" o no
    const user = result.data.usuario || result.data;

    alert(`✅ Bienvenido ${user.nombre || "Usuario"}`);
    console.log("Usuario logueado:", user);

    // Guardar en localStorage
    localStorage.setItem('user', JSON.stringify(user));

    // Redirigir
    navigate("/home");
  } else {
    alert("❌ Error: " + (result.data.error || "Credenciales incorrectas"));
  }
} catch (error) {
  console.error("Error en login:", error);
  alert("Error de conexión: " + error.message);
} finally {
  setLoading(false);
}
  };

  /**
   * Maneja el login con Google
   * 
   * FLUJO COMPLETO:
   * 1. Llama a loginWithGoogle() que abre popup de Google
   * 2. Firebase autentica y devuelve user + idToken
   * 3. Llama a syncFirebaseUser() que sincroniza con backend
   * 4. Backend busca/crea usuario en MongoDB
   * 5. Guarda datos en localStorage
   * 6. Redirige a /home
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
      console.log("Datos del usuario:", {
        uid: user.uid,
        email: user.email,
        displayName: user.displayName,
        photoURL: user.photoURL
      });

      console.log("🔵 PASO 3: Sincronizando con backend Django/MongoDB...");
      const resultado = await syncFirebaseUser(user, idToken);

      if (resultado?.success && resultado?.user) {
        console.log("✅ PASO 4: Usuario sincronizado correctamente");
        console.log("Datos desde MongoDB:", resultado.user);
        
        // Guardar en localStorage para mantener sesión
        localStorage.setItem('user', JSON.stringify(resultado.user));
        localStorage.setItem('idToken', idToken);
        
        alert(`✅ Bienvenido ${resultado.user.nombre}!`);
        navigate("/home");
      } else {
        alert("Error al iniciar sesión con Google. Revisa la consola.");
        console.error("Error en respuesta del backend:", resultado);
      }

    } catch (error) {
      console.error("🔥 Error en login con Google:", error);
      alert("Error al iniciar sesión con Google: " + error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main>
      <section>
        <h1>Iniciar Sesión</h1>
        <form onSubmit={handleSubmit}>
          <label htmlFor="email">Correo electrónico</label>
          <input
            type="email"
            id="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            disabled={loading}
          />

          <label htmlFor="password">Contraseña</label>
          <input
            type="password"
            id="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            disabled={loading}
          />

          <button type="submit" disabled={loading}>
            {loading ? "Ingresando..." : "Ingresar"}
          </button>

          {/* Botón de Google */}
          <button
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

          <p>
            <Link to="#">¿Olvidaste tu contraseña?</Link>
          </p>
          <p>
            ¿Sin cuenta? <Link to="/register">Regístrate aquí</Link>
          </p>
        </form>
      </section>
    </main>
  );
};

export default Login;
