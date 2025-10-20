import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";


const Home = () => {
  const navigate = useNavigate();
  const [formularios, setFormularios] = useState([]);
  const [usuario, setUsuario] = useState({ nombre: "Usuario" });

  useEffect(() => {
    // simula usuario logueado
    const usuarioGuardado = JSON.parse(localStorage.getItem("usuario"));
    if (usuarioGuardado) setUsuario(usuarioGuardado);

    // cargar formularios
    if (usuarioGuardado?.id) {
      fetch(`http://127.0.0.1:8000/api/formularios/?admin=${usuarioGuardado.id}`)
        .then((res) => res.json())
        .then((data) => setFormularios(data))
        .catch((err) => console.error("Error al obtener formularios:", err));
    }
  }, []);

  return (
    <main className="home">
      <h2>Welcome again, {usuario.nombre}</h2>

      {/* Botón para crear formulario */}
      <div style={{ textAlign: "right", marginBottom: "1rem" }}>
        <button
          onClick={() => navigate("/create")}
          style={{
            backgroundColor: "#28a745",
            color: "white",
            border: "none",
            padding: "10px 16px",
            borderRadius: "8px",
            cursor: "pointer",
            fontSize: "1rem",
          }}
        >
          + Crear formulario
        </button>
      </div>


      {/* Lista formularios */}
      <section className="formularios-grid">
        {formularios.length === 0 ? (
          <p>No tienes formularios aún.</p>
        ) : (
          formularios.map((f) => (
            <div key={f.id} className="form-card">
              <h3>{f.titulo}</h3>
              <p>{f.descripcion || "Sin descripción"}</p>
              <span
                className={`estado ${f.configuracion?.privado ? "borrador" : "publicado"}`}
              >
                {f.configuracion?.privado ? "Borrador" : "Publicado"}
              </span>
            </div>
          ))
        )}
      </section>


      
    </main>
  );
};

export default Home;
