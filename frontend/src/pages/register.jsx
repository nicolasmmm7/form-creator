// src/pages/Register.jsx
import React, { useState } from "react";
import { loginWithGoogle } from "../firebase";
import { useNavigate, Link } from "react-router-dom";
import { registrarUsuario, syncFirebaseUser } from "../api/usuario.api";


const Register = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    nombre: "",
    apellido: "",
    correo: "",
    password: "",
    celular: "",
  });
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  /**
   * Maneja el registro tradicional (formulario)
   */
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    const correoRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    const celularRegex = /^[0-9]{10,15}$/;

    // 🔎 Validaciones previas
    if (!correoRegex.test(formData.correo)) {
      alert("❌ Por favor, ingresa un correo electrónico válido.");
      setLoading(false);
      return;
    }

    if (formData.password.length < 6) {
      alert("⚠️ La contraseña debe tener al menos 6 caracteres.");
      setLoading(false);
      return;
    }

    if (!celularRegex.test(formData.celular)) {
      alert("⚠️ Ingresa un número de celular válido (10–15 dígitos).");
      setLoading(false);
      return;
    }

    const nuevoUsuario = {
      nombre: `${formData.nombre} ${formData.apellido}`,
      email: formData.correo,
      clave_hash: formData.password,
      celular: formData.celular,
      empresa: { nombre: "sin_empresa" },
      perfil: { idioma: "es", timezone: "America/Bogota" },
    };

    try {
      const data = await registrarUsuario(nuevoUsuario);

      if (data.id) {
        alert(`✅ Usuario creado con Exito`);
        console.log("Usuario creado:", data);
        navigate("/login");
      } else {
        console.error("❌ Error del backend:", data);
        alert("Error al registrar usuario. Revisa la consola.");
      }
    } catch (error) {
      console.error("❌ Error de conexión:", error);

      // 🆕 Manejo específico de errores del backend
      if (error.data) {
        // Si es un error de validación (ej: email duplicado)
        if (error.data.email) {
          alert(`❌ ${error.data.email[0]}`); // "Este correo ya está registrado."
        } else if (error.data.error) {
          alert(`❌ ${error.data.error}`);
        } else {
          alert("❌ Error al registrar usuario. Revisa los datos.");
        }
      } else {
        alert("No se pudo conectar con el servidor: " + error.message);
      }
    } finally {
      setLoading(false);
    }
  };

  /**
   * Maneja el registro con Google
   */
  const handleGoogleRegister = async () => {
    setLoading(true);

    try {
      console.log("🔵 PASO 1: Autenticando con Firebase...");
      const { user, idToken } = await loginWithGoogle();

      if (!user) {
        alert("No se pudo autenticar el usuario con Google");
        setLoading(false);
        return;
      }

      console.log("✅ PASO 2: Usuario autenticado en Firebase", user);

      console.log("🔵 PASO 3: Sincronizando con backend Django...");
      const resultado = await syncFirebaseUser(user, idToken);

      if (resultado?.success && resultado?.user) {
        console.log("✅ PASO 4: Usuario sincronizado en MongoDB");

        localStorage.setItem("user", JSON.stringify(resultado.user));
        localStorage.setItem("idToken", idToken);

        alert(`✅ Bienvenido ${resultado.user.nombre}!`);
        navigate("/home");
      } else {
        alert("Error al registrar con Google. Revisa la consola.");
        console.error("Error en respuesta del backend:", resultado);
      }
    } catch (error) {
      console.error("🔥 Error en registro con Google:", error);
      alert("Error al iniciar sesión con Google: " + error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main id="main-register">
      <section id="register-section">
        <h1 id="register-titulo">Registro en Form-creator</h1>
        <form id="register-form" onSubmit={handleSubmit}>
          <p id="register-descripcion">Crea tu cuenta para acceder a todas las funciones.</p>

          <label htmlFor="register-nombre">Nombre:</label>
          <input
            type="text"
            id="register-nombre"
            name="nombre"
            value={formData.nombre}
            onChange={handleChange}
            required
            disabled={loading}
          />

          <label htmlFor="register-apellido">Apellido:</label>
          <input
            type="text"
            id="register-apellido"
            name="apellido"
            value={formData.apellido}
            onChange={handleChange}
            required
            disabled={loading}
          />

          <label htmlFor="register-correo">Correo electrónico:</label>
          <input
            type="email"
            id="register-correo"
            name="correo"
            value={formData.correo}
            onChange={handleChange}
            required
            disabled={loading}
          />

          <label htmlFor="register-password">Contraseña:</label>
          <input
            type="password"
            id="register-password"
            name="password"
            value={formData.password}
            onChange={handleChange}
            required
            minLength="6"
            disabled={loading}
          />

          <label htmlFor="register-celular">Celular:</label>
          <input
            type="tel"
            id="register-celular"
            name="celular"
            value={formData.celular}
            onChange={handleChange}
            required
            pattern="[0-9]{10,15}"
            disabled={loading}
          />

          <button id="register-btn-submit" type="submit" disabled={loading}>
            {loading ? "Registrando..." : "Registrarme"}
          </button>

          <button
            id="register-btn-google"
            type="button"
            onClick={handleGoogleRegister}
            disabled={loading}
            aria-label="Registrarme con Google"
            className="google-btn"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 48 48">
              <path fill="#EA4335" d="M24 9.5c3.94 0 7.13 1.62 9.3 3.29l6.89-6.89C36.84 2.32 30.9 0 24 0 14.8 0 6.8 5.47 2.9 13.42l7.97 6.19C12.47 13.1 17.77 9.5 24 9.5z" />
              <path fill="#34A853" d="M46.5 24.48c0-1.61-.14-3.15-.4-4.65H24v9.05h12.76c-.55 2.8-2.2 5.15-4.64 6.74l7.12 5.51c4.13-3.82 6.26-9.46 6.26-16.65z" />
              <path fill="#FBBC05" d="M10.87 28.73a14.25 14.25 0 01-.75-4.73c0-1.65.27-3.24.76-4.74L2.9 13.42A23.94 23.94 0 000 24c0 3.9.93 7.58 2.57 10.58l8.3-5.85z" />
              <path fill="#4285F4" d="M24 48c6.49 0 11.94-2.15 15.92-5.86l-7.12-5.51c-1.96 1.35-4.46 2.2-7.16 2.20-6.23 0-11.52-4.1-13.77-9.78l-8.3 5.85C6.8 42.53 14.8 48 24 48z" />
            </svg>
            {loading ? "Procesando..." : "Registrarme con Google"}
          </button>

          <p id="register-texto-login">
            ¿Ya tienes cuenta? <Link to="/login">Inicia sesión</Link>
          </p>
        </form>
      </section>
    </main>
  );
};

export default Register;
