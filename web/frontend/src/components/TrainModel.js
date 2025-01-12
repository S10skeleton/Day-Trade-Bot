import React, { useState, useEffect } from "react";
import axios from "axios"; // Axios for API calls

const API_BASE = "http://127.0.0.1:5000"; // Flask backend URL

const TrainModel = () => {
    const [training, setTraining] = useState(false);
    const [message, setMessage] = useState(""); // Feedback message
    const [activeSessions, setActiveSessions] = useState(0); // Track active training sessions

    // Start training
    const handleTrainModel = async () => {
        setTraining(true);
        setMessage("Starting training...");
        try {
            const response = await axios.post(`${API_BASE}/start-training`);
            setMessage(response.data.message);
        } catch (error) {
            console.error("Error starting training:", error);
            setMessage("Failed to start training.");
        } finally {
            setTraining(false);
        }
    };

    // Gather progress logs
    const handleGatherProgress = async () => {
        setMessage("Gathering progress...");
        try {
            const response = await axios.post(`${API_BASE}/gather-progress`);
            setMessage(response.data.message);
        } catch (error) {
            console.error("Error gathering progress:", error);
            setMessage("Failed to gather progress.");
        }
    };

    // Reset logs
    const handleResetLogs = async () => {
        setMessage("Resetting logs...");
        try {
            const response = await axios.post(`${API_BASE}/reset-logs`);
            setMessage(response.data.message);
        } catch (error) {
            console.error("Error resetting logs:", error);
            setMessage("Failed to reset logs.");
        }
    };

    // Update stock data
    const handleUpdateStocks = async () => {
        setMessage("Updating stock data...");
        try {
            const response = await axios.post(`${API_BASE}/update-stock-data`);
            setMessage(response.data.message);
        } catch (error) {
            console.error("Error updating stock data:", error);
            setMessage("Failed to update stock data.");
        }
    };

    // Delete the model
    const handleDeleteModel = async () => {
        setMessage("Deleting model...");
        try {
            const response = await axios.delete(`${API_BASE}/delete-model`);
            setMessage(response.data.message);
        } catch (error) {
            console.error("Error deleting model:", error);
            setMessage("Failed to delete the model.");
        }
    };

    // Fetch active training sessions
    useEffect(() => {
        const fetchActiveSessions = async () => {
            try {
                const response = await axios.get(`${API_BASE}/training-status`);
                setActiveSessions(response.data.active_sessions);
            } catch (error) {
                console.error("Error fetching active sessions:", error);
            }
        };

        const interval = setInterval(fetchActiveSessions, 5000); // Poll every 5 seconds
        return () => clearInterval(interval); // Cleanup on unmount
    }, []);

    return (
        <div>
            <h2>Training Management</h2>

            {/* Buttons for training actions */}
            <div style={{ marginBottom: "20px" }}>
                <button onClick={handleTrainModel} disabled={training} style={{ marginRight: "10px" }}>
                    {training ? "Training in Progress..." : "Start Training"}
                </button>
                <button onClick={handleGatherProgress} style={{ marginRight: "10px" }}>
                    Gather Progress
                </button>
                <button onClick={handleResetLogs} style={{ marginRight: "10px" }}>
                    Reset Logs
                </button>
                <button onClick={handleUpdateStocks} style={{ marginRight: "10px" }}>
                    Update Stocks
                </button>
                <button onClick={handleDeleteModel} style={{ marginRight: "10px" }}>
                    Delete Model
                </button>
            </div>

            {/* Feedback Message */}
            {message && <p style={{ color: training ? "blue" : "green" }}>{message}</p>}

            {/* Active Training Sessions */}
            <p>
                <strong>Active Training Sessions:</strong> {activeSessions}
            </p>
        </div>
    );
};

export default TrainModel;
