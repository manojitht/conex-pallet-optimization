import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import './assets/css/style.css'
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import HomePage from './components/Form.jsx'; 

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <Router>
      <Routes>
        {/* Define routes here */}
        <Route path="/" element={<HomePage />} />
      </Routes>
    </Router>
  </StrictMode>
);
