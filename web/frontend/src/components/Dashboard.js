import React from "react";
import StockManager from "./StockManager";
import TrainModel from "./TrainModel";
import PortfolioViewer from "./PortfolioViewer";
import TrainingLogs from "./TrainingLogs";

const Dashboard = ({ darkMode }) => {
    return (
        <div>
            <h1>Day Trade Bot Dashboard</h1>
            <StockManager />
            <TrainModel />
            <PortfolioViewer darkMode={darkMode} /> {/* Pass darkMode to PortfolioViewer */}
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
            <TrainingLogs />
        </div>
    );
};

export default Dashboard;
