import React, { useEffect, useState } from "react";
import { getStocks, addStock, removeStock } from "../api";

const StockManager = () => {
    const [stocks, setStocks] = useState([]);
    const [newStock, setNewStock] = useState("");

    // Fetch stocks on component mount
    useEffect(() => {
        fetchStocks();
    }, []);

    const fetchStocks = async () => {
        try {
            const data = await getStocks();
            setStocks(data);
        } catch (error) {
            console.error("Failed to fetch stocks:", error);
        }
    };

    const handleAddStock = async () => {
        try {
            await addStock(newStock);
            setNewStock("");
            fetchStocks(); // Refresh stocks
        } catch (error) {
            console.error("Failed to add stock:", error);
        }
    };

    const handleRemoveStock = async (symbol) => {
        try {
            await removeStock(symbol);
            fetchStocks(); // Refresh stocks
        } catch (error) {
            console.error("Failed to remove stock:", error);
        }
    };

    return (
        <div>
            <h2>Stock Manager</h2>
            <ul>
                {stocks.map((stock) => (
                    <li key={stock}>
                        {stock}{" "}
                        <button onClick={() => handleRemoveStock(stock)}>Remove</button>
                    </li>
                ))}
            </ul>
            <input
                type="text"
                placeholder="Add stock symbol"
                value={newStock}
                onChange={(e) => setNewStock(e.target.value)}
            />
            <button onClick={handleAddStock}>Add Stock</button>
        </div>
    );
};

export default StockManager;
