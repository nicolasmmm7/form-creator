// src/pages/Home.jsx
import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";


const Home = () => {
  const navigate = useNavigate();
  const [formularios, setFormularios] = useState([]);
  const [loading, setLoading] = useState(true);
  const [menuAbierto, setMenuAbierto] = useState(null);
  const [user, setUser] = useState(null);

  // 🔐 Verificar autenticación y cargar usuario
  useEffect(() => {
    const userData = JSON.parse(localStorage.getItem("user"));

    if (!userData?.id) {
      alert("⚠️ Debe iniciar sesión para acceder");
      navigate("/login");
      return;
    }

    setUser(userData);
    cargarFormularios(userData.id);
  }, [navigate]);

  // 🎯 Cerrar menú al hacer clic fuera
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (menuAbierto && !event.target.closest('[data-menu]')) {
        setMenuAbierto(null);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [menuAbierto]);

  // 📥 Cargar formularios del usuario
  const cargarFormularios = async (userId) => {
    setLoading(true);
    try {
      const res = await fetch(`http://127.0.0.1:8000/api/formularios/?admin=${userId}`);

      if (!res.ok) {
        throw new Error("Error al cargar formularios");
      }

      const data = await res.json();
      console.log("📋 Formularios cargados:", data);
      setFormularios(data);
    } catch (error) {
      console.error("❌ Error:", error);
      alert("No se pudieron cargar los formularios");
    } finally {
      setLoading(false);
    }
  };

  // ➕ Navegar a crear formulario
  const handleCrearFormulario = () => {
    navigate("/create");
  };

  // ✏️ Editar formulario
  const handleEditar = (id) => {
    console.log("✏️ Editar formulario:", id);
    navigate(`/create/${id}`); // 👈 Navegar a CreateForm con ID
    setMenuAbierto(null);
  };
  // 📊 Ver analíticas
  const handleAnaliticas = (id) => {
    console.log("📊 Ver analíticas:", id);
    alert("🚧 Funcionalidad de analíticas en desarrollo");
    setMenuAbierto(null);
  };

  // 📋 Duplicar formulario
  const handleDuplicar = async (formulario) => {
    setMenuAbierto(null);

    const confirmacion = window.confirm(
      `¿Deseas duplicar el formulario "${formulario.titulo}"?`
    );

    if (!confirmacion) return;

    try {
      const formularioDuplicado = {
        titulo: `${formulario.titulo} (copia)`,
        descripcion: formulario.descripcion,
        administrador: user.id,
        configuracion: formulario.configuracion || {
          privado: false,
          fecha_limite: null,
          notificaciones_email: false,
          requerir_login: false,
          una_respuesta: true,
          permitir_edicion: false,
        },
        preguntas: formulario.preguntas || [],
      };

      const res = await fetch("http://127.0.0.1:8000/api/formularios/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formularioDuplicado),
      });

      if (!res.ok) {
        throw new Error("Error al duplicar formulario");
      }

      alert("✅ Formulario duplicado correctamente");
      cargarFormularios(user.id);
    } catch (error) {
      console.error("❌ Error al duplicar:", error);
      alert("Error al duplicar el formulario");
    }
  };

  // 🗑️ Eliminar formulario
  const handleEliminar = async (id, titulo) => {
    setMenuAbierto(null);

    const confirmacion = window.confirm(
      `¿Estás seguro de eliminar el formulario "${titulo}"? Esta acción no se puede deshacer.`
    );

    if (!confirmacion) return;

    try {
      const res = await fetch(`http://127.0.0.1:8000/api/formularios/${id}/`, {
        method: "DELETE",
      });

      if (!res.ok) {
        throw new Error("Error al eliminar formulario");
      }

      alert("✅ Formulario eliminado correctamente");
      cargarFormularios(user.id);
    } catch (error) {
      console.error("❌ Error al eliminar:", error);
      alert("Error al eliminar el formulario");
    }
  };

  // 📍 Toggle menú de opciones
  const toggleMenu = (id) => {
    setMenuAbierto(menuAbierto === id ? null : id);
  };

  // 🎨 Determinar estado del formulario
  const obtenerEstado = (form) => {
    if (form.configuracion?.fecha_limite) {
      const fechaLimite = new Date(form.configuracion.fecha_limite);
      if (fechaLimite < new Date()) {
        return "CERRADO";
      }
    }

    // 📌 Si privado = true → no publicado
    if (form.configuracion?.privado) {
      return "BORRADOR";
    }

    // 📌 Si privado = false → publicado
    return "PUBLICADO";
  };




  // 🔗 Compartir formulario
  const handleCompartir = async (id) => {
    const enlace = `${window.location.origin}/form/${id}/answer`;

    try {
      await navigator.clipboard.writeText(enlace);
      alert("🔗 Enlace copiado al portapapeles:\n" + enlace);
    } catch (err) {
      console.error("❌ No se pudo copiar:", err);
      alert("⚠️ No se pudo copiar el enlace");
    }

    setMenuAbierto(null);
  };

  const handleTogglePublicar = async (form) => {
    const estaPublicado = form.configuracion?.privado === false;
    const nuevoPrivado = estaPublicado ? true : false;

    const confirmar = window.confirm(
      estaPublicado
        ? `¿Deseas despublicar el formulario "${form.titulo}"?`
        : `¿Deseas publicar el formulario "${form.titulo}"?`
    );

    if (!confirmar) return;

    try {
      const actualizado = {
        ...form,
        configuracion: {
          ...form.configuracion,
          privado: nuevoPrivado, // 🔁 si es publicado → privado = false
        },
      };

      const res = await fetch(`http://127.0.0.1:8000/api/formularios/${form.id}/`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(actualizado),
      });

      if (!res.ok) throw new Error("Error al actualizar estado");

      alert(
        !nuevoPrivado
          ? "✅ Formulario publicado correctamente"
          : "📤 Formulario despublicado"
      );
      cargarFormularios(user.id);
    } catch (error) {
      console.error("❌ Error al cambiar estado:", error);
      alert("No se pudo actualizar el estado del formulario");
    }
  };

  return (
    <main className="home-main">
      {/* Header */}
      <header className="home-header">
        <h1 className="home-welcome-text">
          Bienvenido, <span className="home-user-name">{user?.nombre || "$fulanito name"}</span>
        </h1>
        <div
          className="home-user-icon"
          onClick={() => navigate("/ProfilePage")}
          role="button"
          tabIndex={0}
          onKeyDown={(e) => { if (e.key === "Enter" || e.key === " ") navigate("/ProfilePage"); }}
          title="Ver perfil"
          style={{ cursor: "pointer" }}
        >
          {user?.perfil?.avatar_url ? (
            <img
              src={user.perfil.avatar_url}
              alt={user?.nombre || "Avatar"}
              className="home-avatar"
              onError={(e) => {
                // Si la imagen falla al cargar, reemplázala por el ícono SVG genérico
                e.target.outerHTML = `
                  <svg viewBox="0 0 24 24" fill="none" style="width: 35px; height: 35px;">
                    <circle cx="12" cy="8" r="4" stroke="#6366f1" stroke-width="2"/>
                    <path d="M6 21c0-3.314 2.686-6 6-6s6 2.686 6 6"
                          stroke="#6366f1" stroke-width="2" stroke-linecap="round"/>
                  </svg>
                `;
              }}
            />
          ) : (
            <svg viewBox="0 0 24 24" fill="none" style={{ width: "35px", height: "35px" }}>
              <circle cx="12" cy="8" r="4" stroke="#6366f1" strokeWidth="2" />
              <path d="M6 21c0-3.314 2.686-6 6-6s6 2.686 6 6" stroke="#6366f1" strokeWidth="2" strokeLinecap="round" />
            </svg>
          )}
        </div>
      </header>

      {/* Contenedor principal */}
      <div className="home-content-wrapper">
        <section className="home-grid">
          {/* Tarjeta CREAR */}
          <div
            className="home-card-crear"
            onClick={handleCrearFormulario}
          >
            <svg className="home-plus-icon" viewBox="0 0 24 24" fill="none">
              <path d="M12 5V19M5 12H19" stroke="currentColor" strokeWidth="3" strokeLinecap="round" />
            </svg>
            <span className="home-crear-text">CREAR</span>
          </div>

          {/* Tarjetas de formularios */}
          {formularios.map((form) => {
            const estado = obtenerEstado(form);

            return (
              <div
                key={form.id}
                className="home-card"
              >
                {/* Badge de estado y menú en la misma línea */}
                <div className="home-top-bar">
                  <div className={`home-badge ${estado === "PUBLICADO" ? "home-badge-publicado" :
                    estado === "BORRADOR" ? "home-badge-borrador" :
                      "home-badge-cerrado"
                    }`}>
                    {estado}
                  </div>

                  {/* Menú de 3 puntos */}
                  <div className="home-menu-container" data-menu>
                    <button
                      className="home-menu-button"
                      onClick={() => toggleMenu(form.id)}
                      aria-label="Opciones"
                    >
                      ⋮
                    </button>

                    {menuAbierto === form.id && (
                      <div className="home-menu-dropdown" data-menu>
                        <button
                          className="home-menu-item"
                          onClick={() => handleEliminar(form.id, form.titulo)}
                        >
                          🗑️ Eliminar encuesta
                        </button>
                        <button
                          className="home-menu-item"
                          onClick={() => handleDuplicar(form)}
                        >
                          📋 Duplicar encuesta
                        </button>
                        <button
                          className="home-menu-item"
                          onClick={() => navigate(`/form/${form.id}/stats`)}
                        >
                          📊 Estadísticas
                        </button>
                        <button
                          className="home-menu-item"
                          onClick={() => handleEditar(form.id)}
                        >
                          ✏️ Editar
                        </button>

                        {/* 🔗 NUEVA OPCIÓN DE COMPARTIR */}
                        {obtenerEstado(form) === "PUBLICADO" && (
                          <button
                            className="home-menu-item"
                            onClick={() => handleCompartir(form.id)}
                          >
                            📤 Compartir enlace
                          </button>
                        )}
                      </div>
                    )}
                  </div>
                </div>

                {/* Miniatura con icono de imagen */}
                <div className="home-thumbnail">
                  <svg viewBox="0 0 24 24" fill="white" style={{ width: "48px", height: "48px" }}>
                    <rect x="3" y="3" width="18" height="18" rx="2" fill="none" stroke="white" strokeWidth="1.5" />
                    <path d="M3 16l5-5 5 5" strokeWidth="1.5" stroke="white" fill="none" strokeLinecap="round" strokeLinejoin="round" />
                    <path d="M13 13l3-3 5 5" strokeWidth="1.5" stroke="white" fill="none" strokeLinecap="round" strokeLinejoin="round" />
                    <circle cx="8.5" cy="8.5" r="1.5" fill="white" />
                  </svg>
                </div>

                {/* Título del formulario */}
                <h3 className="home-card-title">{form.titulo}</h3>

                {/* Info adicional */}
                <p className="home-card-info">
                  {form.preguntas?.length || 0} preguntas
                </p>

                {/* Botón Publicar / Despublicar */}
                <div className="home-card-footer">
                  <button
                    className={`home-btn-publicar ${estado === "PUBLICADO" ? "despublicar" : "publicar"
                      }`}
                    onClick={() => handleTogglePublicar(form)}
                  >
                    {estado === "PUBLICADO" ? "Despublicar" : "Publicar"}
                  </button>
                </div>
              </div>
            );
          })}
        </section>

        {/* Mensaje si no hay formularios */}
        {formularios.length === 0 && (
          <div className="home-empty-state">
            <p className="home-empty-text">
              No tienes formularios creados aún. ¡Crea tu primer formulario!
            </p>
          </div>
        )}
      </div>
    </main>
  );
};

export default Home;