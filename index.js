import { fileURLToPath } from 'url'
import express from 'express';
import Redis from 'ioredis';
import cors from 'cors'
import {PythonShell} from 'python-shell';
import {convertToJsonObject} from "./lib/utils.js";
import * as path from "node:path";

const __filename = fileURLToPath(import.meta.url);

const __dirname = path.dirname(__filename);


// Set cache expiry time in seconds (15 minutes = 900 seconds)
const CACHE_EXPIRY = 900;

const app = express();

const PORT = process.env.PORT || 8080

// Initialize Redis client
const redis = Redis.createClient(process.env.REDIS_PORT || 6379, process.env.REDIS_HOST || 'localhost', {
    connectTimeout: 10000,
    keepAlive: true
});

redis.on('connect', () => console.log('Connected to Redis'));
redis.on('error', (err) => console.error('Redis connection error:', err));

app.use(cors());

app.use('/graphs', express.static(path.join(__dirname, 'pyth/graphs')));

app.get('/deribit', async (req, res) => {
    const cacheKey = 'python-script-response'; // Unique cache key for the Python script

    try {
        // Check if data is already cached
        const cachedResponse = await redis.get(cacheKey);

        if (cachedResponse) {
            console.log('Returning cached Python response');
            return res.json(JSON.parse(cachedResponse)); // Return cached response
        }

        // If not cached, execute the Python script
        const pythResponse = await PythonShell.run('./pyth/PortfolioUI.py');
        console.log({pythResponse});

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
        res.status(500).json({error: 'Something went wrong'});
    }
});

app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
    console.log('Checking env variables on docker and here: ', {
        port: process.env.PORT,
        redis: process.env.REDIS_PORT,
        env: process.env.DERIBIT_CLIENT_ID,
    })
});
