import React, { useEffect, useState } from "react";

const TrainingLogs = () => {
    const [logs, setLogs] = useState("");

    useEffect(() => {
        const eventSource = new EventSource("http://127.0.0.1:5000/stream-logs");
    
        eventSource.onmessage = (event) => {
            setLogs((prevLogs) => prevLogs + event.data + "\n");
        };
    
        eventSource.onerror = () => {
            console.error("Error connecting to the log stream.");
            setLogs((prevLogs) => prevLogs + "Error: Unable to connect to logs.\n");
            eventSource.close();
        };
    
        return () => {
            eventSource.close();
        };
    }, []);
    

    // Auto-scroll to the bottom whenever logs update
    useEffect(() => {
        const element = document.querySelector('pre');
        if (element) element.scrollTop = element.scrollHeight;
    }, [logs]);

    return (
        <div style={{ maxHeight: "300px", overflowY: "scroll", border: "1px solid #ccc", padding: "10px" }}>
            <h3>Training Logs</h3>
            <button onClick={() => setLogs("")} style={{ marginBottom: "10px", padding: "5px 10px" }}>
                Clear Logs
            </button>
            <pre style={{ whiteSpace: "pre-wrap", wordWrap: "break-word" }}>{logs}</pre>
        </div>
    );
};

export default TrainingLogs;
