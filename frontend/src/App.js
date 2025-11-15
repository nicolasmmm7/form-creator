import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Login from "./pages/login";
import Register from "./pages/register";
import Home from "./pages/home";
import CreateForm from "./pages/CreateForm";
import PasswordReset from "./pages/password-reset"; 
import ProfilePage from "./pages/ProfilePage";
import AnswerForm from "./pages/AnswerForm";
import ThankYou from "./pages/ThankYou";
import EditSuccess from "./pages/EditSuccess";


import "./css/Auth.css";
import "./css/Home.css"
import "./css/CreateForm.css"
import "./css/password.css"


function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Login />} />

        <Route path="/form/:id/answer" element={<AnswerForm />} />
        <Route path="/thankyou" element={<ThankYou />} />

        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        
        <Route path="/home" element={<Home />} />
        <Route path="/create/:formId?" element={<CreateForm />} />
        <Route path="/password-reset" element={<PasswordReset />} />
        <Route path="/ProfilePage" element={<ProfilePage />} />
        <Route path="/editSuccess" element={<EditSuccess />} />
      </Routes>
    </Router>
  );
}

export default App;