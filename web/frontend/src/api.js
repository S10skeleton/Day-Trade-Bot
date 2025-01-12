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

// Fetch TensorBoard URL
export const getTensorBoardUrl = async () => {
    try {
        const response = await axios.get(`${API_BASE}/tensorboard`);
        return response.data.url;
    } catch (error) {
        console.error("Error fetching TensorBoard URL:", error.message);
        throw error;
    }
};

// Example for the /stream-logs endpoint
export const fetchLogs = async () => {
    try {
        const response = await fetch(`${API_BASE}/stream-logs`, {
            method: "GET",
            headers: {
                "Accept": "text/event-stream",
            },
        });
        return response.body;
    } catch (error) {
        console.error("Error fetching stream logs:", error.message);
        throw error;
    }
};

export const getTrainingStatus = async () => {
    try {
        const response = await axios.get(`${API_BASE}/training-status`);
        return response.data;
    } catch (error) {
        console.error("Error fetching training status:", error.message);
        throw error;
    }
};

// Delete the training model
export const deleteModel = async () => {
    try {
        const response = await axios.delete(`${API_BASE}/delete-model`);
        return response.data;
    } catch (error) {
        console.error("Error deleting model:", error.message);
        throw error;
    }
};

// Wipe logs
export const wipeLogs = async () => {
    try {
        const response = await axios.delete(`${API_BASE}/wipe-logs`);
        return response.data;
    } catch (error) {
        console.error("Error wiping logs:", error.message);
        throw error;
    }
};

export const updateStockData = async () => {
    try {
        const response = await axios.post(`${API_BASE}/update-stock-data`);
        return response.data;
    } catch (error) {
        console.error("Error updating stock data:", error.message);
        throw error;
    }
};

