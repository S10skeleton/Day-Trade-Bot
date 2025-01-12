import React, { useEffect, useState, useRef } from "react";

const TrainingLogs = () => {
    const [logs, setLogs] = useState("");
    const logContainerRef = useRef(null);

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

    useEffect(() => {
        if (logContainerRef.current) {
            logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight;
        }
    }, [logs]);

    return (
        <div
            ref={logContainerRef}
            style={{
                maxHeight: "400px",
                overflowY: "scroll",
                border: "1px solid #ccc",
                padding: "10px",
                backgroundColor: "#000",
                color: "#0f0",
                fontFamily: "monospace",
            }}
        >
            <pre style={{ whiteSpace: "pre-wrap", wordWrap: "break-word" }}>{logs}</pre>
        </div>
    );
};

export default TrainingLogs;
