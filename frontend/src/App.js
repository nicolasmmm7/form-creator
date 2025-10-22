import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Login from "./pages/login";
import Register from "./pages/register";
import Home from "./pages/home";
import CreateForm from "./pages/CreateForm";
import PasswordReset from "./pages/password-reset"; 
import ProfilePage from "./pages/ProfilePage";

import "./css/Auth.css";
import "./css/Home.css"
import "./css/CreateForm.css"
import "./css/password.css"

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/home" element={<Home />} />
        <Route path="/create" element={<CreateForm />} /> 
        <Route path="/password-reset" element={<PasswordReset />} />
        <Route path="/ProfilePage" element={<ProfilePage />} />
      </Routes>
    </Router>
  );
}

export default App;