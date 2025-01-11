import React from "react";
import StockManager from "./StockManager";
import TrainModel from "./TrainModel";
import PortfolioViewer from "./PortfolioViewer";

const Dashboard = () => {
    return (
        <div>
            <h1>Day Trade Bot Dashboard</h1>
            <StockManager />
            <TrainModel />
            <PortfolioViewer />
            <div>
                <h2>Training Metrics</h2>
                <iframe
                    src="http://localhost:6006/"
                    style={{ width: "100%", height: "500px", border: "none" }}
                    title="TensorBoard"
                ></iframe>
            </div>
        </div>
    );
};

export default Dashboard;
