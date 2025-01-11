import React, { useEffect, useState } from "react";
import StockManager from "./StockManager";
import TrainModel from "./TrainModel";
import PortfolioViewer from "./PortfolioViewer";
import TrainingLogs from "./TrainingLogs";

const Dashboard = ({ darkMode }) => {
    const [portfolio, setPortfolio] = useState(null);
    const [error, setError] = useState("");

    useEffect(() => {
        fetchPortfolio();
    }, []);

    const fetchPortfolio = async () => {
        try {
            const response = await fetch("http://127.0.0.1:5000/portfolio"); // Ensure Flask server is running
            if (!response.ok) {
                throw new Error("Failed to fetch portfolio data");
            }
            const data = await response.json();
            if (data.error) {
                setError(data.error);
            } else {
                setPortfolio(data);
            }
        } catch (err) {
            console.error("Error fetching portfolio:", err);
            setError("Unable to fetch portfolio data. Please check the server.");
        }
    };

    return (
        <div>
            <h1>Day Trade Bot Dashboard</h1>

            {/* Portfolio Summary */}
            <div>
                {error ? (
                    <p style={{ color: "red" }}>{error}</p>
                ) : portfolio ? (
                    <div>
                        <h2>Portfolio Summary</h2>
                        <p>
                            <strong>Total Portfolio Value:</strong> ${portfolio.total_value.toFixed(2)}
                        </p>
                    </div>
                ) : (
                    <p>Loading portfolio data...</p>
                )}
            </div>

            {/* Other Components */}
            <StockManager />
            <TrainModel />
            <PortfolioViewer darkMode={darkMode} /> {/* Pass darkMode to PortfolioViewer */}

            {/* TensorBoard Metrics */}
            <div>
                <h2>Training Metrics</h2>
                <iframe
                    src="http://localhost:6006/"
                    style={{
                        width: "100%",
                        height: "500px",
                        border: "none",
                        backgroundColor: darkMode ? "#121212" : "#ffffff", // Dark mode styling
                    }}
                    title="TensorBoard"
                ></iframe>
            </div>

            {/* Training Logs */}
            <TrainingLogs />
        </div>
    );
};

export default Dashboard;
