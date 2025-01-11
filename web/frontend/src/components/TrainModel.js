import React, { useState } from "react";
import { trainModel } from "../api";

const TrainModel = () => {
    const [training, setTraining] = useState(false);
    const [message, setMessage] = useState("");

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

    return (
        <div>
            <h2>Train Model</h2>
            <button onClick={handleTrainModel} disabled={training}>
                {training ? "Training..." : "Train Model"}
            </button>
            {message && <p>{message}</p>}
        </div>
    );
};

export default TrainModel;
