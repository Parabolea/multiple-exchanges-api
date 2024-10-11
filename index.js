import express from 'express';
import Redis from 'ioredis';
import cors from 'cors'
import { PythonShell } from 'python-shell';
import {convertToJsonObject} from "./lib/utils.js";

// Initialize Redis client
const redis = new Redis();

// Set cache expiry time in seconds (15 minutes = 900 seconds)
const CACHE_EXPIRY = 900;

const app = express();


const PORT = 8081;

app.use(cors());

app.get('/deribit', async (req, res) => {
    const cacheKey = 'python-script-response'; // Unique cache key for the Python script

    try {
        // Check if data is already cached
        const cachedResponse = await redis.get(cacheKey);

        if (cachedResponse) {1
            console.log('Returning cached Python response');
            return res.json(JSON.parse(cachedResponse)); // Return cached response
        }

        // If not cached, execute the Python script
        const pythResponse = await PythonShell.run('./pyth/PortfolioUI.py');
        console.log({ pythResponse });

        const results = convertToJsonObject(pythResponse[pythResponse.length - 1]);

        // Store the Python script results in Redis with an expiry time
        const response = {
            status: 200,
            statusText: "OK",
            results,
        };
        await redis.set(cacheKey, JSON.stringify(response), 'EX', CACHE_EXPIRY);

        // Return the fresh Python script response
        res.json(response);

    } catch (error) {
        console.error('Error executing Python script:', error);
        res.status(500).json({ error: 'Something went wrong' });
    }
});

app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});
