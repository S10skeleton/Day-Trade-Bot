import React, { useEffect, useState } from "react";
import { getPortfolio } from "../api";
import Plot from "react-plotly.js";

const PortfolioViewer = () => {
    const [portfolio, setPortfolio] = useState(null);
    const [error, setError] = useState("");

    useEffect(() => {
        fetchPortfolio();
    }, []);

    const fetchPortfolio = async () => {
        try {
            const data = await getPortfolio();
            setPortfolio(data);
        } catch (err) {
            console.error("Failed to fetch portfolio:", err);
            setError("No portfolio data available. Run a training session first.");
        }
    };

    if (error) {
        return <p>{error}</p>;
    }

    if (!portfolio) {
        return <p>Loading portfolio...</p>;
    }

    const steps = portfolio.stocks.map((stock) => stock.Step);
    const portfolioValues = portfolio.stocks.map((stock) => stock["Portfolio Value"]);

    return (
        <div>
            <h2>Portfolio</h2>
            <p>Total Value: ${portfolio.total_value.toFixed(2)}</p>
            <Plot
                data={[
                    {
                        x: steps,
                        y: portfolioValues,
                        type: "scatter",
                        mode: "lines+markers",
                        marker: { color: "blue" },
                        name: "Portfolio Value",
                    },
                ]}
                layout={{
                    title: "Portfolio Value Over Time",
                    xaxis: { title: "Steps" },
                    yaxis: { title: "Portfolio Value" },
                }}
            />
        </div>
    );
};

export default PortfolioViewer;
