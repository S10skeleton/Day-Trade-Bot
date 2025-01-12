import React, { useEffect, useState } from "react";
import StockManager from "./StockManager";
import TrainModel from "./TrainModel";
import PortfolioViewer from "./PortfolioViewer";
import TrainingLogs from "./TrainingLogs";

const Dashboard = ({ darkMode }) => {
  return (
    <div>
      <div className="stat-view">
        <div>
        <h1>Day Trade Bot Dashboard</h1>
        <StockManager />
        <TrainModel />
        </div>
        <div>
        <PortfolioViewer darkMode={darkMode} />{" "}
        </div>
      </div>
      {/* TensorBoard Metrics */}
      <div className="metric-view">
        <h2>Training Metrics</h2>
        <iframe
          src="http://localhost:6006/"
          style={{
            width: "99%",
            height: "500px",
            border: "none",
            backgroundColor: darkMode ? "#121212" : "#ffffff", // Dark mode styling
          }}
          title="TensorBoard"
        ></iframe>
      </div>

      <div className="console-view">
        <TrainingLogs />
      </div>
    </div>
  );
};

export default Dashboard;
