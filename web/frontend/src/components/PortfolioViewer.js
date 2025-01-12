import React, { useEffect, useState } from "react";
import { getPortfolio } from "../api";
import Plot from "react-plotly.js";
import Slider from "rc-slider"; // Install with: npm install rc-slider
import "rc-slider/assets/index.css"; // Slider styling

const PortfolioViewer = ({ darkMode }) => {
  const [portfolio, setPortfolio] = useState(null);
  const [error, setError] = useState("");
  const [visibleWeeks, setVisibleWeeks] = useState([0, 52]); // Default slider range: Full year

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

  // Aggregate data into weekly intervals
  const intervalMinutes = 1440; // Daily intervals
  const startTime = new Date("2025-01-01T00:00:00");
  const aggregatedData = portfolio.stocks.reduce((acc, stock, index) => {
    const step = stock.Step || index; // Fallback to index if Step is missing
    const currentTimestamp = new Date(startTime.getTime() + step * intervalMinutes * 60000);
    const weekKey = `${currentTimestamp.getFullYear()}-W${Math.ceil(currentTimestamp.getDate() / 7)}`;

    if (!acc[weekKey]) {
      acc[weekKey] = { timestamp: weekKey, portfolioValues: [] };
    }
    acc[weekKey].portfolioValues.push(stock["Portfolio Value"]);

    return acc;
  }, {});

  const timestamps = Object.keys(aggregatedData);
  const portfolioValues = Object.values(aggregatedData).map((data) => {
    const sum = data.portfolioValues.reduce((a, b) => a + b, 0);
    return sum / data.portfolioValues.length;
  });

  // Filter data based on slider range
  const filteredTimestamps = timestamps.slice(visibleWeeks[0], visibleWeeks[1]);
  const filteredPortfolioValues = portfolioValues.slice(visibleWeeks[0], visibleWeeks[1]);

  return (
    <div style={{ display: "flex", flexDirection: "column" }}>
      <h2>Portfolio</h2>
      <p>Total Value: ${portfolio.total_value.toFixed(2)}</p>
      <div className="chart-container" style={{ display: "flex" }}>
        <Plot
          className="chart"
          data={[
            {
              x: filteredTimestamps, // Use filtered timestamps
              y: filteredPortfolioValues, // Use filtered portfolio values
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
            xaxis: {
              title: "Week",
              color: darkMode ? "#e0e0e0" : "#000000",
            },
            yaxis: {
              title: "Portfolio Value",
              color: darkMode ? "#e0e0e0" : "#000000",
            },
            showlegend: true, // Enable the legend
            legend: {
              x: 1.1, // Position legend outside the chart on the right
              y: 1,
              bgcolor: darkMode ? "#121212" : "#ffffff",
              bordercolor: darkMode ? "#e0e0e0" : "#000000",
              borderwidth: 1,
            },
          }}
        />
      </div>
      {/* Slider */}
      <div style={{ margin: "20px 0" }}>
        <Slider
          range
          min={0}
          max={timestamps.length - 1}
          defaultValue={visibleWeeks}
          onChange={(value) => setVisibleWeeks(value)} // Update the visible range
          trackStyle={[{ backgroundColor: "blue" }]} // Custom track color
          handleStyle={[{ borderColor: "blue" }]} // Custom handle color
        />
      </div>
    </div>
  );
};

export default PortfolioViewer;
