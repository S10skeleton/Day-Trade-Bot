import React, { useEffect, useState } from "react";
import Plot from "react-plotly.js";

const PortfolioViewer = ({ darkMode }) => {
    const [actionLogs, setActionLogs] = useState([]);
    const [error, setError] = useState("");

    useEffect(() => {
        fetchActionLogs();
    }, []);

    const fetchActionLogs = async () => {
        try {
            const response = await fetch("/action-logs");
            const rawText = await response.text();
            console.log("Raw response:", rawText); // Debugging the response
    
            let data = [];
            try {
                data = JSON.parse(rawText); // Attempt to parse as JSON
            } catch (parseError) {
                console.error("Failed to parse JSON:", parseError);
                setError("Invalid data format from the server.");
                return;
            }
    
            // Validate and filter logs
            const validLogs = data.filter(
                (log) =>
                    log.timestamp &&
                    log.action &&
                    typeof log.value === "number"
            );
    
            setActionLogs(validLogs);
    
            if (!validLogs.length) {
                setError("No valid logs found in the server response.");
            }
        } catch (fetchError) {
            console.error("Failed to fetch action logs:", fetchError);
            setError("Unable to fetch action logs. Please check the server.");
        }
    };
    

    if (error) {
        return <p>{error}</p>;
    }

    if (!actionLogs.length) {
        return <p>Loading real-world stats...</p>;
    }

    const actionTimestamps = actionLogs.map((log) => log.timestamp);
    const budgets = actionLogs.map((log) => log.value);
    const portfolioValues = actionLogs.map((log) => log.value);

    return (
        <div>
            <h2>Real-World Stats</h2>
            <Plot
                data={[
                    {
                        x: actionTimestamps,
                        y: budgets,
                        type: "scatter",
                        mode: "lines+markers",
                        marker: { color: "green" },
                        name: "Budget Over Time",
                    },
                    {
                        x: actionTimestamps,
                        y: portfolioValues,
                        type: "scatter",
                        mode: "lines+markers",
                        marker: { color: "blue" },
                        name: "Portfolio Value",
                    },
                ]}
                layout={{
                    plot_bgcolor: darkMode ? "#121212" : "#ffffff",
                    paper_bgcolor: darkMode ? "#121212" : "#ffffff",
                    font: { color: darkMode ? "#e0e0e0" : "#000000" },
                    title: {
                        text: "Portfolio Value Over Time",
                        font: { color: darkMode ? "#e0e0e0" : "#000000" },
                    },
                    xaxis: { color: darkMode ? "#e0e0e0" : "#000000" },
                    yaxis: { color: darkMode ? "#e0e0e0" : "#000000" },
                }}
            />
            <div style={{ maxHeight: "300px", overflowY: "scroll", border: "1px solid #ccc", padding: "10px" }}>
                <h3>Action Logs</h3>
                <ul>
                    {actionLogs.map((log, index) => (
                        <li key={index}>
                            <strong>Timestamp:</strong> {log.timestamp} | 
                            <strong> Action:</strong> {log.action} | 
                            <strong> Value:</strong> ${log.value.toFixed(2)}
                        </li>
                    ))}
                </ul>
            </div>
        </div>
    );
};

export default PortfolioViewer;
