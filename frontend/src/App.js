import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Login from "./pages/login";
import Register from "./pages/register";
import Home from "./pages/home";
import CreateForm from "./pages/CreateForm";

import "./css/Auth.css";
import "./css/Home.css"
import "./css/CreateForm.css"

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/home" element={<Home />} />
        <Route path="/create" element={<CreateForm />} /> 
      </Routes>
    </Router>
  );
}

export default App;