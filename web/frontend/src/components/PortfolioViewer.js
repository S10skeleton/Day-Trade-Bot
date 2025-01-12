import React, { useEffect, useState } from "react";
import { getPortfolio } from "../api";
import Plot from "react-plotly.js";
// import "../App.css";


const PortfolioViewer = ({ darkMode }) => {
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
  const portfolioValues = portfolio.stocks.map(
    (stock) => stock["Portfolio Value"]
  );

  return (
    <div>
      <h2>Portfolio</h2>
      <p>Total Value: ${portfolio.total_value.toFixed(2)}</p>
      <div className="chart-container">
        <Plot
          className="chart"
          data={[
            {
              x: steps,
              y: portfolioValues,
              type: "scatter",
              mode: "lines+markers",
              marker: { color: darkMode ? "lightblue" : "blue" },
              name: "Portfolio Value",
            },
          ]}
          layout={{
            width: 1500,
            height: 400,
            plot_bgcolor: darkMode ? "#121212" : "#ffffff",
            paper_bgcolor: darkMode ? "#121212" : "#ffffff",
            font: { color: darkMode ? "#e0e0e0" : "#000000" },
            title: {
              text: "Portfolio Value Over Time",
              font: { color: darkMode ? "#e0e0e0" : "#000000" },
            },
            xaxis: { title: "Steps", color: darkMode ? "#e0e0e0" : "#000000" },
            yaxis: {
              title: "Portfolio Value",
              color: darkMode ? "#e0e0e0" : "#000000",
            },
          }}
        />
      </div>
    </div>
  );
};

export default PortfolioViewer;
