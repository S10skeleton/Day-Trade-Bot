import axios from "axios";

const API_BASE = "http://127.0.0.1:5000"; // Ensure this matches your Flask server

// Fetch all stocks
export const getStocks = async () => {
    try {
        const response = await axios.get(`${API_BASE}/stocks`);
        return response.data;
    } catch (error) {
        console.error("Error fetching stocks:", error.message);
        throw error;
    }
};

// Add a new stock
export const addStock = async (symbol) => {
    try {
        const response = await axios.post(`${API_BASE}/stocks`, { symbol });
        return response.data;
    } catch (error) {
        console.error("Error adding stock:", error.message);
        throw error;
    }
};

// Remove a stock
export const removeStock = async (symbol) => {
    try {
        const response = await axios.delete(`${API_BASE}/stocks`, { data: { symbol } });
        return response.data;
    } catch (error) {
        console.error("Error removing stock:", error.message);
        throw error;
    }
};

// Trigger model training
export const trainModel = async () => {
    try {
        const response = await axios.post(`${API_BASE}/train`);
        return response.data;
    } catch (error) {
        console.error("Error training model:", error.message);
        throw error;
    }
};

// Fetch portfolio data
export const getPortfolio = async () => {
    try {
        const response = await axios.get(`${API_BASE}/portfolio`);
        return response.data;
    } catch (error) {
        console.error("Error fetching portfolio:", error.message);
        throw error;
    }
};
