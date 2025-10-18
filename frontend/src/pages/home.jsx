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
    alert("🚧 Funcionalidad de edición en desarrollo");
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
    
    if (form.configuracion?.privado || !form.configuracion?.requerir_login) {
      return "BORRADOR";
    }
    
    return "PUBLICADO";
  };

  if (loading) {
    return (
      <main style={{ padding: "40px", textAlign: "center", background: "#e8f5e9" }}>
        <h2>Cargando formularios...</h2>
      </main>
    );
  }

  return (
    <main style={styles.main}>
      {/* Header */}
      <header style={styles.header}>
        <h1 style={styles.welcomeText}>
          Bienvenido, <span style={styles.userName}>{user?.nombre || "$fulanito name"}</span>
        </h1>
        <div style={styles.userIcon}>
          {user?.perfil?.avatar_url ? (
            <img 
              src={user.perfil.avatar_url} 
              alt="Avatar" 
              style={styles.avatar}
            />
          ) : (
            <svg viewBox="0 0 24 24" fill="none" style={{ width: "35px", height: "35px" }}>
              <circle cx="12" cy="8" r="4" stroke="#6366f1" strokeWidth="2"/>
              <path d="M6 21c0-3.314 2.686-6 6-6s6 2.686 6 6" stroke="#6366f1" strokeWidth="2" strokeLinecap="round"/>
            </svg>
          )}
        </div>
      </header>

      {/* Contenedor principal */}
      <div style={styles.contentWrapper}>
        <section style={styles.grid}>
          {/* Tarjeta CREAR */}
          <div 
            style={styles.cardCrear} 
            onClick={handleCrearFormulario}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = "translateY(-3px)";
              e.currentTarget.style.boxShadow = "0 6px 20px rgba(0, 0, 0, 0.1)";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = "translateY(0)";
              e.currentTarget.style.boxShadow = "0 2px 8px rgba(0, 0, 0, 0.06)";
            }}
          >
            <svg style={styles.plusIcon} viewBox="0 0 24 24" fill="none">
              <path d="M12 5V19M5 12H19" stroke="currentColor" strokeWidth="3" strokeLinecap="round"/>
            </svg>
            <span style={styles.crearText}>CREAR</span>
          </div>

          {/* Tarjetas de formularios */}
          {formularios.map((form) => {
            const estado = obtenerEstado(form);
            
            return (
              <div 
                key={form.id} 
                style={styles.card}
                onMouseEnter={(e) => {
                  e.currentTarget.style.transform = "translateY(-3px)";
                  e.currentTarget.style.boxShadow = "0 8px 24px rgba(0, 0, 0, 0.12)";
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = "translateY(0)";
                  e.currentTarget.style.boxShadow = "0 2px 8px rgba(0, 0, 0, 0.06)";
                }}
              >
                {/* Badge de estado y menú en la misma línea */}
                <div style={styles.topBar}>
                  <div style={{
                    ...styles.badge,
                    backgroundColor: 
                      estado === "PUBLICADO" ? "#22c55e" : 
                      estado === "BORRADOR" ? "#d97706" : 
                      "#94a3b8"
                  }}>
                    {estado}
                  </div>

                  {/* Menú de 3 puntos */}
                  <div style={styles.menuContainer} data-menu>
                    <button
                      style={styles.menuButton}
                      onClick={() => toggleMenu(form.id)}
                      aria-label="Opciones"
                      onMouseEnter={(e) => e.target.style.background = "#f3f4f6"}
                      onMouseLeave={(e) => e.target.style.background = "transparent"}
                    >
                      ⋮
                    </button>

                    {menuAbierto === form.id && (
                      <div style={styles.menuDropdown} data-menu>
                        <button 
                          style={styles.menuItem}
                          onClick={() => handleEliminar(form.id, form.titulo)}
                          onMouseEnter={(e) => e.target.style.background = "#f9fafb"}
                          onMouseLeave={(e) => e.target.style.background = "white"}
                        >
                          🗑️ Eliminar encuesta
                        </button>
                        <button 
                          style={styles.menuItem}
                          onClick={() => handleDuplicar(form)}
                          onMouseEnter={(e) => e.target.style.background = "#f9fafb"}
                          onMouseLeave={(e) => e.target.style.background = "white"}
                        >
                          📋 Duplicar encuesta
                        </button>
                        <button 
                          style={styles.menuItem}
                          onClick={() => handleAnaliticas(form.id)}
                          onMouseEnter={(e) => e.target.style.background = "#f9fafb"}
                          onMouseLeave={(e) => e.target.style.background = "white"}
                        >
                          🔍 Analíticas
                        </button>
                        <button 
                          style={styles.menuItem}
                          onClick={() => handleEditar(form.id)}
                          onMouseEnter={(e) => e.target.style.background = "#f9fafb"}
                          onMouseLeave={(e) => e.target.style.background = "white"}
                        >
                          ✏️ Editar
                        </button>
                      </div>
                    )}
                  </div>
                </div>

                {/* Miniatura con icono de imagen */}
                <div style={styles.thumbnail}>
                  <svg viewBox="0 0 24 24" fill="white" style={{ width: "48px", height: "48px" }}>
                    <rect x="3" y="3" width="18" height="18" rx="2" fill="none" stroke="white" strokeWidth="1.5"/>
                    <path d="M3 16l5-5 5 5" strokeWidth="1.5" stroke="white" fill="none" strokeLinecap="round" strokeLinejoin="round"/>
                    <path d="M13 13l3-3 5 5" strokeWidth="1.5" stroke="white" fill="none" strokeLinecap="round" strokeLinejoin="round"/>
                    <circle cx="8.5" cy="8.5" r="1.5" fill="white"/>
                  </svg>
                </div>

                {/* Título del formulario */}
                <h3 style={styles.cardTitle}>{form.titulo}</h3>
                
                {/* Info adicional */}
                <p style={styles.cardInfo}>
                  {form.preguntas?.length || 0} preguntas
                </p>
              </div>
            );
          })}
        </section>

        {/* Mensaje si no hay formularios */}
        {formularios.length === 0 && (
          <div style={styles.emptyState}>
            <p style={styles.emptyText}>
              No tienes formularios creados aún. ¡Crea tu primer formulario!
            </p>
          </div>
        )}
      </div>
    </main>
  );
};

// 🎨 Estilos actualizados
const styles = {
  main: {
    minHeight: "100vh",
    background: "linear-gradient(135deg, #d4f1d4 0%, #a8e6a3 100%)",
    padding: "30px 50px",
  },
  header: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: "30px",
    padding: "20px 30px",
    background: "rgba(255, 255, 255, 0.95)",
    borderRadius: "16px",
    boxShadow: "0 2px 8px rgba(0, 0, 0, 0.06)",
    maxWidth: "1400px",
    margin: "0 auto 30px auto",
  },
  welcomeText: {
    fontSize: "30px",
    fontWeight: "400",
    color: "#1f2937",
    margin: 0,
  },
  userName: {
    color: "#22c55e",
    fontWeight: "400",
    borderBottom: "2px solid #22c55e",
    paddingBottom: "2px",
  },
  userIcon: {
    width: "50px",
    height: "50px",
    borderRadius: "50%",
    background: "#f3f4f6",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    overflow: "hidden",
    border: "2px solid #e5e7eb",
  },
  avatar: {
    width: "100%",
    height: "100%",
    objectFit: "cover",
  },
  contentWrapper: {
    background: "white",
    borderRadius: "24px",
    padding: "40px",
    maxWidth: "1400px",
    margin: "0 auto",
    boxShadow: "0 4px 16px rgba(0, 0, 0, 0.08)",
  },
  grid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))",
    gap: "24px",
  },
  cardCrear: {
    background: "#f9fafb",
    border: "2px dashed #d1d5db",
    borderRadius: "16px",
    minHeight: "320px",
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
    cursor: "pointer",
    transition: "all 0.3s ease",
    boxShadow: "0 2px 8px rgba(0, 0, 0, 0.06)",
  },
  plusIcon: {
    width: "70px",
    height: "70px",
    marginBottom: "12px",
    color: "#d1d5db",
  },
  crearText: {
    fontSize: "28px",
    fontWeight: "300",
    color: "#d1d5db",
    letterSpacing: "3px",
  },
  card: {
    background: "#f9fafb",
    borderRadius: "16px",
    padding: "20px",
    minHeight: "320px",
    display: "flex",
    flexDirection: "column",
    position: "relative",
    boxShadow: "0 2px 8px rgba(0, 0, 0, 0.06)",
    transition: "transform 0.3s ease, box-shadow 0.3s ease",
  },
  topBar: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: "16px",
    height: "32px",
  },
  badge: {
    padding: "6px 16px",
    borderRadius: "16px",
    fontSize: "11px",
    fontWeight: "700",
    color: "white",
    textTransform: "uppercase",
    letterSpacing: "0.5px",
    display: "inline-block",
  },
  menuContainer: {
    position: "relative",
  },
  menuButton: {
    background: "transparent",
    border: "none",
    fontSize: "24px",
    fontWeight: "bold",
    cursor: "pointer",
    padding: "4px 8px",
    color: "#6b7280",
    borderRadius: "6px",
    transition: "background 0.2s",
    lineHeight: "1",
  },
  menuDropdown: {
    position: "absolute",
    top: "100%",
    right: "0",
    background: "white",
    borderRadius: "12px",
    boxShadow: "0 10px 40px rgba(0, 0, 0, 0.15)",
    minWidth: "200px",
    marginTop: "8px",
    zIndex: 1000,
    overflow: "hidden",
    border: "1px solid #e5e7eb",
  },
  menuItem: {
    width: "100%",
    padding: "12px 16px",
    border: "none",
    background: "white",
    textAlign: "left",
    cursor: "pointer",
    fontSize: "14px",
    transition: "background 0.2s",
    display: "block",
    color: "#374151",
    fontWeight: "400",
  },
  thumbnail: {
    background: "#1f2937",
    borderRadius: "12px",
    height: "140px",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    marginBottom: "16px",
    flex: "1",
  },
  cardTitle: {
    fontSize: "17px",
    fontWeight: "600",
    color: "#1f2937",
    margin: "0 0 6px 0",
    overflow: "hidden",
    textOverflow: "ellipsis",
    whiteSpace: "nowrap",
  },
  cardInfo: {
    fontSize: "13px",
    color: "#6b7280",
    margin: 0,
    fontWeight: "400",
  },
  emptyState: {
    textAlign: "center",
    marginTop: "60px",
  },
  emptyText: {
    fontSize: "16px",
    color: "#6b7280",
    fontWeight: "400",
  },
};

export default Home;
