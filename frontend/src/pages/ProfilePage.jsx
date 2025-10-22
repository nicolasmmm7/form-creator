import React, { useEffect, useState } from "react";
import { getUserData, updateUserData } from "../api/usuario.api";
import { useNavigate } from "react-router-dom";
import "../css/ProfilePage.css";

const ProfilePage = () => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isEditing, setIsEditing] = useState(false);
  const [editedData, setEditedData] = useState({});
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });
  
  const navigate = useNavigate();

  useEffect(() => {
    const safeParse = (str) => {
      try { return JSON.parse(str); } catch { return null; }
    };

    const localUser = safeParse(localStorage.getItem("user"));

    if (localUser) {
      setUser(localUser);
      setLoading(false);
    }

    // Detectar si el usuario inició sesión por Google/Firebase
    const isGoogleUser =
      !!localUser &&
      (
        localUser.provider === "google" ||
        localUser.auth_provider === "google" ||
        localUser.loginMethod === "google" ||
        localUser.firebase === true ||
        localStorage.getItem("signin_provider") === "google"
      );

    // Sólo usar idToken (Firebase) si el usuario realmente se autenticó con Google
    const idToken = isGoogleUser ? localStorage.getItem("idToken") : null;

    // Si no hay token ni usuario local -> pedir login
    if (!idToken && !localUser) {
      navigate("/login");
      return;
    }

    // Si hay token (usuario Google) o existe user cached, solicitar datos autoritativos
    (async () => {
      // Evitar repetir fetch si no hay necesidad
      if (!idToken && localUser) {
        // ya mostramos el usuario cacheado
        return;
      }

      if (idToken) {
        setLoading(true);
        const res = await getUserData(idToken);
        if (res.ok) {
          setUser(res.data);
          try { localStorage.setItem("user", JSON.stringify(res.data)); } catch {}
        } else {
          console.warn("No autorizado o error al obtener usuario:", res.data);
          // Si no hay usuario cacheado, redirigir al login
          if (!localUser) navigate("/login");
        }
        setLoading(false);
      }
    })();
  }, [navigate]);

  const handleStartEdit = () => {
    setEditedData({
      nombre: user.nombre || '',
      empresa: {
        nombre: user.empresa?.nombre || '',
        telefono: user.empresa?.telefono || '',
        nit: user.empresa?.nit || ''
      },
      perfil: {
        avatar_url: user.perfil?.avatar_url || '',
        idioma: user.perfil?.idioma || '',
        timezone: user.perfil?.timezone || ''
      }
    });
    setIsEditing(true);
    setMessage({ type: '', text: '' });
  };

  const handleCancelEdit = () => {
    setIsEditing(false);
    setEditedData({});
    setMessage({ type: '', text: '' });
  };

  const handleInputChange = (e, section = null) => {
    const { name, value } = e.target;

    if (section) {
      setEditedData(prev => ({
        ...prev,
        [section]: {
          ...prev[section],
          [name]: value
        }
      }));
    } else {
      setEditedData(prev => ({
        ...prev,
        [name]: value
      }));
    }
  };

  const handleSaveChanges = async () => {
    setSaving(true);
    setMessage({ type: '', text: '' });

    try {
      const signinProvider = localStorage.getItem("signin_provider") || user?.provider || user?.auth_provider || "normal";
      const tokenForUpdate = signinProvider === "google" ? localStorage.getItem("idToken") : null;

      // Crear copias de los objetos para no modificar el estado directamente
      const empresaInput = editedData.empresa ? { ...editedData.empresa } : {};
      const perfilInput = editedData.perfil ? { ...editedData.perfil } : {};
      const payload = { ...editedData };

      // Validar teléfono si existe
      if (empresaInput.telefono) {
        const digits = String(empresaInput.telefono).replace(/\D/g, "");
        if (digits.length !== 10) {
          setMessage({ type: 'error', text: 'El teléfono debe tener exactamente 10 dígitos.' });
          setSaving(false);
          return;
        }
        empresaInput.telefono = digits;
      }

      // Limpiar campos vacíos de empresa
      Object.keys(empresaInput).forEach(key => {
        if (empresaInput[key] === "" || (typeof empresaInput[key] === "string" && empresaInput[key].trim() === "")) {
          delete empresaInput[key];
        }
      });

      // Limpiar campos vacíos de perfil
      Object.keys(perfilInput).forEach(key => {
        if (perfilInput[key] === "" || (typeof perfilInput[key] === "string" && perfilInput[key].trim() === "")) {
          delete perfilInput[key];
        }
      });

      // Limpiar campos vacíos del payload principal
      Object.keys(payload).forEach(key => {
        if (payload[key] === "" || (typeof payload[key] === "string" && payload[key].trim() === "")) {
          delete payload[key];
        }
      });

      // Asignar objetos limpios al payload solo si tienen propiedades
      if (Object.keys(empresaInput).length > 0) {
        payload.empresa = empresaInput;
      }
      if (Object.keys(perfilInput).length > 0) {
        payload.perfil = perfilInput;
      }

      const res = await updateUserData(user.id, payload, tokenForUpdate);

      if (res.ok) {
        const updatedUser = res.data.usuario || res.data;
        setUser(updatedUser);
        localStorage.setItem("user", JSON.stringify(updatedUser));
        setMessage({ type: 'success', text: 'Perfil actualizado correctamente' });
        setIsEditing(false);
        setTimeout(() => setMessage({ type: '', text: '' }), 3000);
      } else {
        // Manejar 401/403 específicamente
        if (res.data && (res.data.status === 401 || res.data.status === 403)) {
          setMessage({ type: 'error', text: 'No autorizado para actualizar. Inicia sesión nuevamente.' });
        } else {
          setMessage({ type: 'error', text: res.data.error || 'Error al actualizar el perfil' });
        }
      }
    } catch (error) {
      console.error('Error:', error);
      setMessage({ type: 'error', text: 'Error al guardar los cambios' });
    } finally {
      setSaving(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("idToken");
    localStorage.removeItem("user");
    localStorage.removeItem("userId");
    localStorage.removeItem("signin_provider");
    navigate("/login");
  };

  const handleBackToHome = () => {
    navigate("/home");
  };

  if (loading && !user) return <div className="pp-loading">Cargando...</div>;
  if (!user) return <div className="pp-error">No se encontró información del usuario.</div>;

  return (
    <div className="profile-page">
      <div className="profile-card">
        <header className="profile-header">
          <button
            className="pp-back-button"
            onClick={handleBackToHome}
            aria-label="Volver"
            title="Volver a home"
          >
            ←
          </button>

          <h2 className="profile-title">Perfil de usuario</h2>

          {!isEditing ? (
            <button className="pp-edit-button" onClick={handleStartEdit}>✏️ Editar</button>
          ) : (
            <div className="pp-edit-actions">
              <button className="pp-save" onClick={handleSaveChanges} disabled={saving}>
                {saving ? 'Guardando...' : '💾 Guardar'}
              </button>
              <button className="pp-cancel" onClick={handleCancelEdit} disabled={saving}>Cancelar</button>
            </div>
          )}
        </header>

        {message.text && (
          <div className={`pp-message ${message.type === 'success' ? 'success' : 'error'}`}>
            {message.text}
          </div>
        )}

        <div className="pp-main">
          <div className="pp-avatar-block">
          {user?.perfil?.avatar_url ? (
            <img
              src={user.perfil.avatar_url}
              alt={user?.nombre || "Avatar"}
              className="pp-avatar"
              onError={(e) => {
                // Si la imagen falla, reemplázala dinámicamente por el ícono SVG
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
            <svg
              viewBox="0 0 24 24"
              fill="none"
              style={{ width: "35px", height: "35px" }}
            >
              <circle cx="12" cy="8" r="4" stroke="#6366f1" strokeWidth="2" />
              <path
                d="M6 21c0-3.314 2.686-6 6-6s6 2.686 6 6"
                stroke="#6366f1"
                strokeWidth="2"
                strokeLinecap="round"
              />
            </svg>
          )}
        </div>

          <div className="pp-info">
            {isEditing ? (
              <>
                <label className="pp-label">Nombre</label>
                <input className="pp-input" name="nombre" value={editedData.nombre} onChange={(e) => handleInputChange(e)} />

                <p className="pp-email"><strong>Email:</strong> {user.email} <span className="pp-noedit">(no editable)</span></p>
              </>
            ) : (
              <>
                <h3 className="pp-name">{user.nombre}</h3>
                <p className="pp-email"><strong>Email:</strong> {user.email}</p>
              </>
            )}

            <p className="pp-date"><strong>Miembro desde:</strong> {user.fecha_registro ? new Date(user.fecha_registro).toLocaleDateString('es-ES', { year:'numeric', month:'long', day:'numeric' }) : "—"}</p>
          </div>
        </div>

        <div className="pp-grid">
          <section className="pp-card">
            <h4>Empresa</h4>
            {isEditing ? (
              <>
                <label className="pp-label">Nombre</label>
                <input className="pp-input" name="nombre" value={editedData.empresa?.nombre || ''} onChange={(e) => handleInputChange(e, 'empresa')} />

                <label className="pp-label">Teléfono</label>
                <input className="pp-input" name="telefono" value={editedData.empresa?.telefono || ''} onChange={(e) => handleInputChange(e, 'empresa')} />

                <label className="pp-label">NIT</label>
                <input className="pp-input" name="nit" value={editedData.empresa?.nit || ''} onChange={(e) => handleInputChange(e, 'empresa')} />
              </>
            ) : (
              <>
                <p><strong>Nombre:</strong> {user.empresa?.nombre || "No asignada"}</p>
                <p><strong>Teléfono:</strong> {user.empresa?.telefono || "—"}</p>
                <p><strong>NIT:</strong> {user.empresa?.nit || "—"}</p>
              </>
            )}
          </section>

          <section className="pp-card">
            <h4>Preferencias</h4>
            {isEditing ? (
              <>
                <label className="pp-label">Idioma</label>
                <select className="pp-input" name="idioma" value={editedData.perfil?.idioma || 'es'} onChange={(e) => handleInputChange(e, 'perfil')}>
                  <option value="es">Español</option>
                  <option value="en">English</option>
                </select>

                <label className="pp-label">Zona horaria</label>
                <select className="pp-input" name="timezone" value={editedData.perfil?.timezone || 'America/Bogota'} onChange={(e) => handleInputChange(e, 'perfil')}>
                  <option value="America/Bogota">Bogotá</option>
                  <option value="Europe/Madrid">Madrid</option>
                </select>

                <label className="pp-label">Imagen de perfil</label>
                <input
                  className="pp-input"
                  name="avatar_url"
                  value={editedData.perfil?.avatar_url || ''}
                  onChange={(e) => handleInputChange(e, 'perfil')}
                  placeholder="inserta la url de tu imagen"
                />
              </>
            ) : (
              <>
                <p><strong>Idioma:</strong> {user.perfil?.idioma || "No especificado"}</p>
                <p><strong>Zona horaria:</strong> {user.perfil?.timezone || "No especificada"}</p>
              </>
            )}
          </section>
        </div>

        <div className="pp-actions">
          {!isEditing ? (
            <button className="pp-logout" onClick={handleLogout}>🚪 Cerrar sesión</button>
          ) : null}
        </div>
      </div>
    </div>
  );
};

export default ProfilePage;
