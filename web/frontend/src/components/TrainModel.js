import React, { useState, useEffect } from "react";
import { trainModel, getTrainingStatus } from "../api";

const TrainModel = () => {
    const [training, setTraining] = useState(false);
    const [message, setMessage] = useState("");
    const [activeSessions, setActiveSessions] = useState(0);

    const handleTrainModel = async () => {
        setTraining(true);
        setMessage("");
        try {
            const data = await trainModel();
            setMessage(data.message);
        } catch (error) {
            console.error("Training failed:", error);
            setMessage("Training failed.");
        } finally {
            setTraining(false);
        }
    };

    useEffect(() => {
        const fetchStatus = async () => {
            try {
                const status = await getTrainingStatus();
                setActiveSessions(status.active_sessions);
            } catch (error) {
                console.error("Error fetching training status:", error);
            }
        };

        const interval = setInterval(fetchStatus, 5000); // Poll every 5 seconds
        return () => clearInterval(interval); // Cleanup on unmount
    }, []);

    return (
        <div>
            <h2>Train Model</h2>
            <button onClick={handleTrainModel} disabled={training}>
                {training ? "Training..." : "Train Model"}
            </button>
            {message && <p>{message}</p>}
            <p>Active Training Sessions: {activeSessions}</p>
        </div>
    );
};

export default TrainModel;
