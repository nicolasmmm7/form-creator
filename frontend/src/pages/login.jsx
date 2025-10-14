import React, { useState } from "react";
import { loginWithGoogle } from "../firebase";
import { useNavigate, Link } from "react-router-dom";

const Login = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log("Login con email:", email, password);
  };

  const handleGoogleLogin = async () => {
    const user = await loginWithGoogle();
    if (user) navigate("/home"); // redirige si el login fue exitoso
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
          />

          <label htmlFor="password">Contraseña</label>
          <input
            type="password"
            id="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />

          <button type="submit">Ingresar</button>

          {/* 🔥 Botón Google */}
          <button
            type="button"
            onClick={handleGoogleLogin}
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
                d="M24 48c6.49 0 11.94-2.15 15.92-5.86l-7.12-5.51c-1.96 1.35-4.46 2.2-7.16 2.2-6.23 0-11.52-4.1-13.77-9.78l-8.3 5.85C6.8 42.53 14.8 48 24 48z"
              />
            </svg>
            Iniciar sesión con Google
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
