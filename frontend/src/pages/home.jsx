import React, { useState, useEffect } from "react";

const Home = () => {
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
