import React, { useState, useEffect } from "react";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import Dashboard from "./components/Dashboard";

function App() {
    const [darkMode, setDarkMode] = useState(false);

    useEffect(() => {
        // Load the initial theme from localStorage
        const storedTheme = localStorage.getItem("darkMode");
        if (storedTheme === "true") {
            document.body.classList.add("dark-mode");
            setDarkMode(true);
        }
    }, []);

    const toggleTheme = () => {
        const isDarkMode = !darkMode;
        setDarkMode(isDarkMode);

        // Add or remove the 'dark-mode' class on <body>
        if (isDarkMode) {
            document.body.classList.add("dark-mode");
        } else {
            document.body.classList.remove("dark-mode");
        }

        // Save the preference in localStorage
        localStorage.setItem("darkMode", isDarkMode);
    };

    return (
        <Router>
            <div>
                <header style={{ padding: "10px", textAlign: "right" }}>
                    <button onClick={toggleTheme}>
                        {darkMode ? "Switch to Light Mode" : "Switch to Dark Mode"}
                    </button>
                </header>
                <Routes>
                    <Route path="/" element={<Dashboard darkMode={darkMode} />} />
                </Routes>
            </div>
        </Router>
    );
}

export default App;
