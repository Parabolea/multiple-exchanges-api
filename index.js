import {fileURLToPath} from 'url'
import express from 'express';
import Redis from 'ioredis';
import cors from 'cors'
import {PythonShell} from 'python-shell';
import {convertToJsonObject} from "./src/lib/utils.js";
import * as path from "node:path";
import dotenv from "dotenv"
import http from "http";
import {WebSocketServer} from 'ws'
import winston from "winston";
import moment from 'moment-timezone'

dotenv.config()

const logger = winston.createLogger({
    defaultMeta: {
        service: 'db-api-parabolea'
    },
    level: 'info',
    format: winston.format.combine(
        winston.format.timestamp({
            format: () => moment().tz('Asia/Singapore').format('YYYY-MM-DD HH:mm:ss'),
        })
    ),
    transports: [
        new winston.transports.Console({format: winston.format.simple()}),
    ]
})

const __filename = fileURLToPath(import.meta.url);

const __dirname = path.dirname(__filename);

const DEMO = process.env.DEMO || false

// Set cache expiry time in seconds (15 minutes = 900 seconds)
const CACHE_EXPIRY = 900;

const app = express();
const PORT = process.env.PORT || 8080

const server = http.createServer(app);

const wss = new WebSocketServer({server, path: '/vol-scanner'});
wss.on('connection', (socket) => {
    console.log('WebSocket connection started');

    // Handle incoming messages
    socket.on('message', async (message) => {
        console.log('Received message', message.toString());
        if (message.toString() === 'scan') {
            // initialize a local variable
            let localData = []
            console.log('scan event triggered, now running!')
            const storedTickers = await redis.get('vol-scanner/stock-tickers');
            const arrayedStoredTickers = JSON.parse(storedTickers)

            const pyCall = new PythonShell('./pyth/ATM_Vol_Dashboard.py', {
                args: arrayedStoredTickers,
                mode: 'json',
                pythonOptions: ['-u']
            })
            pyCall.on('message', async (message) => {
                const parsedMessage = typeof message === 'object' ? JSON.stringify(message) : message;
                if (parsedMessage.includes('end_of_scan')) {
                    console.log('End of scan, stopping now')
                    // save
                    socket.send('end_of_scan')
                    return
                }
                console.log('Parsed message:', parsedMessage);
                // Append the parsed message to the local variable
                localData.push(JSON.parse(parsedMessage));
                await redis.set('vol-scanner/scanned', JSON.stringify(localData));
                // Send the serialized message to the client
                socket.send(parsedMessage);
            })
        }
    });
});

// Initialize Redis client
const redis = Redis.createClient(process.env.REDIS_PORT || 6379, process.env.REDIS_HOST || 'localhost', {
    connectTimeout: 10000,
    keepAlive: true
});

redis.on('connect', () => console.log('Connected to Redis'));
redis.on('error', (err) => console.error('Redis connection error:', err));

app.use(cors());
app.use(express.json());

const errors = ['SyntaxError', 'TypeError', 'ReferenceError', 'TimeoutError', 'ConnectionRefusedError', 'Error', 'Failed'];

const DEFAULT_TICKERS = [
    'AAPL', 'NVDA', 'MSFT', 'AVGO', 'META', 'AMZN', 'TSLA', 'COST', 'GOOG',
    'NFLX', 'TMUS', 'AMD', 'PEP', 'LIN', 'CSCO', 'ADBE', 'QCOM', 'TXN', 'ISRG',
    'COIN', 'MSTR', 'YINN', 'USO', 'GDX', 'ARM', 'MU', 'TSM', 'JPM', 'UNH',
    'XOM', 'V', 'MA', 'HD', 'PG', 'JNJ', 'ABBV', 'CRM',
    'GOOGL', 'LLY', 'WMT', 'BAC', 'ORCL', 'CVX', 'WFC', 'MRK', 'KO',
    'ACN', 'NOW', 'DIS', 'MCD', 'IBM', 'PM', 'ABT', 'TMO', 'GE', 'CAT', 'GS',
    'VZ', 'INTU', 'BKNG', 'AXP', 'SPGI', 'CMCSA', 'MS', 'T', 'NEE', 'RTX',
    'DHR', 'LOW', 'PGR', 'UBER', 'AMAT', 'HON', 'AMGN', 'ETN', 'UNP', 'PFE',
    'TJX', 'BLK', 'COP', 'C', 'BX', 'PLTR', 'SYK', 'BSX', 'PANW', 'FI', 'ADP',
    'SCHW', 'BMY', 'VRTX', 'DE', 'GILD', 'SBUX', 'MMC', 'BA', 'MDT', 'ADI',
    'LMT', 'CB', 'KKR', 'PLD', 'ANET', 'LRCX', 'INTC', 'UPS', 'MELI', 'APP',
    'CTAS', 'PYPL', 'KLAC', 'MDLZ', 'SNPS', 'CDNS', 'MAR', 'REGN', 'CRWD',
    'MRVL', 'CEG', 'FTNT', 'ORLY', 'CSX', 'DASH', 'ASML', 'PDD', 'ADSK', 'PCAR',
    'CPRT', 'ROP', 'ABNB', 'NXPI', 'TTD', 'CHTR', 'MNST', 'WDAY', 'AEP', 'PAYX',
    'FANG', 'ROST', 'ODFL', 'FAST', 'DDOG', 'KDP', 'BKR', 'EA', 'TEAM', 'VRSK',
    'XEL', 'CTSH', 'EXC', 'AZN', 'KHC', 'GEHC', 'LULU', 'MCHP', 'CCEP', 'IDXX',
    'CSGP', 'TTWO', 'DXCM', 'ZS', 'ANSS', 'ON', 'WBD', 'GFS', 'MDB', 'CDW',
    'BIIB', 'ILMN', 'SMCI'
]; // Default tickers

async function initializeStockTickers() {
    try {
        // Check if tickers are already stored in Redis
        let storedTickers = await redis.get('vol-scanner/stock-tickers'); // Fetch tickers as a string

        if (!storedTickers) {
            console.log('No tickers found in Redis. Storing default tickers...');

            // If tickers are not in Redis, set the default tickers
            await redis.set('vol-scanner/stock-tickers', JSON.stringify(DEFAULT_TICKERS));
            storedTickers = JSON.stringify(DEFAULT_TICKERS);
        }

        const stockTickers = JSON.parse(storedTickers); // Parse Redis data into an array
        console.log('Stock tickers:', stockTickers);

        return stockTickers; // Use this array in your app logic
    } catch (error) {
        console.error('Error initializing tickers:', error);
        return DEFAULT_TICKERS; // Fallback to default tickers
    }
}

app.use('/graphs', express.static(path.join(__dirname, 'pyth/graphs')));

app.get('/deribit', async (req, res) => {
    logger.info('TRIGGERED: /deribit')
    const cacheKey = 'python-script-response'; // Unique cache key for the Python script

    try {
        if (DEMO) {
            console.info('Successfully returned mock data for deribit endpoint')
            return res.json({
                "status": 200,
                "statusText": "OK",
                "results": {
                    "portfolio": {
                        "btc": {
                            "equity": "33.6984723",
                            "margin": "0.0",
                            "delta": "0.0",
                            "vega": "0.0",
                            "theta": "0.0",
                            "pnl": "0.0",
                            "upnl": "0.0"
                        },
                        "eth": {
                            "equity": "710.395758",
                            "margin": "0.0",
                            "delta": "0.0",
                            "vega": "0.0",
                            "theta": "0.0",
                            "pnl": "0.0",
                            "upnl": "0.0"
                        }
                    }, "positions": {
                        "btc": [], "eth": [
                            {
                                "instrument_name": "BTC-PERPETUAL",
                                "size": "0.5",
                                "direction": "long",
                                "avg_price": "35000",
                                "avg_price_usd": "35000",
                                "delta": "0.5",
                                "theta": "-0.01",
                                "vega": "0.02",
                                "pnl": "150",
                                "current_price": "35500",
                                "mark_price": "35450",
                                "itm": "true",
                            },
                            {
                                "instrument_name": "ETH-PERPETUAL",
                                "size": "1.2",
                                "direction": "short",
                                "avg_price": "2000",
                                "avg_price_usd": "2000",
                                "delta": "-1.2",
                                "theta": "-0.03",
                                "vega": "-0.01",
                                "pnl": "-75",
                                "current_price": "2025",
                                "mark_price": "2020",
                                "itm": "false",
                            },
                            {
                                "instrument_name": "SOL-DEC2024",
                                "size": "100",
                                "direction": "long",
                                "avg_price": "35",
                                "avg_price_usd": "35",
                                "delta": "100",
                                "theta": "-0.5",
                                "vega": "0.1",
                                "pnl": "500",
                                "current_price": "40",
                                "mark_price": "39.5",
                                "itm": "true",
                            },
                            {
                                "instrument_name": "ADA-MAR2025",
                                "size": "500",
                                "direction": "short",
                                "avg_price": "0.35",
                                "avg_price_usd": "0.35",
                                "delta": "-500",
                                "theta": "-0.02",
                                "vega": "-0.03",
                                "pnl": "-250",
                                "current_price": "0.37",
                                "mark_price": "0.368",
                                "itm": "false",
                            },
                        ]
                    }
                }
            })

        }        // Check if data is already cached
        const cachedResponse = await redis.get(cacheKey);

        if (cachedResponse) {
            console.log('Returning cached Python response');
            return res.json(JSON.parse(cachedResponse)); // Return cached response
        }

        // If not cached, execute the Python script
        const pythResponse = await PythonShell.run('./pyth/PortfolioUI.py',);
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

app.get('/vol-scanner/tickers', async (req, res) => {
    logger.info('TRIGGERED: /vol-scanner/tickers')
    let storedTickers = await redis.get('vol-scanner/stock-tickers');
    if (!storedTickers) {
        await initializeStockTickers()
        storedTickers = await redis.get('vol-scanner/stock-tickers')
    }
    res.status(200).json({
        data: JSON.parse(storedTickers)
    })
})

app.post('/vol-scanner/clear-cache', async (req, res) => {
    logger.info('TRIGGERED: /vol-scanner/clear-cache')
    try {
        await redis.del('vol-scanner/stock-tickers')
        await redis.del('vol-scanner/scanned')
        await redis.del('ibkr-portfolio/cached')
        await redis.del('calendar_events')
        res.status(200).json({
            message: 'Clearing redis cache successful'
        })
    } catch (e) {
        res.status(500).json({message: 'Something went wrong with deleting caches'});
    }
})

app.post('/vol-scanner/add-ticker', async (req, res) => {
    logger.info('TRIGGERED: /vol-scanner/add-ticker')
    try {
        const {body} = req
        const storedTickers = await redis.get('vol-scanner/stock-tickers');
        const arrayStoredTickers = JSON.parse(storedTickers)

        if (arrayStoredTickers.includes(body?.ticker)) throw new Error('Ticker already exists')
        arrayStoredTickers.push(body?.ticker?.toUpperCase())
        await redis.set('vol-scanner/stock-tickers', JSON.stringify(arrayStoredTickers));
        res.status(200).json({
            message: 'success',
            data: arrayStoredTickers
        });
    } catch (e) {
        res.status(500).json({error: e instanceof Error ? e.message : e});
    }
})

app.post('/vol-scanner/delete-ticker', async (req, res) => {
    logger.info('TRIGGERED: /vol-scanner/delete-ticker')
    try {
        const {ticker} = req.body
        const storedTickers = await redis.get('vol-scanner/stock-tickers');
        const arrayStoredTickers = JSON.parse(storedTickers)

        console.log({arrayStoredTickers, ticker})
        if (ticker && !arrayStoredTickers.find(item => item.toLowerCase() === ticker.toLowerCase())) {
            console.error('Ticker you wish to delete is not on the list');
            res.status(400).json({error: 'Ticker you wish to delete is not on the list'});
        }
        const deletedList = arrayStoredTickers.filter(item => item.toLowerCase() !== ticker.toLowerCase())
        await redis.set('vol-scanner/stock-tickers', JSON.stringify(deletedList));

        res.status(200).json({
            message: 'deleted',
            data: deletedList
        })
    } catch (e) {
        res.status(500).json({error: e instanceof Error ? e.message : e});
    }
})

app.get('/vol-scanner/scan', async (req, res) => {
    logger.info('TRIGGERED: /vol-scanner/scan')
    console.log('Clearing past scanned data...')
    await redis.del('vol-scanner/scanned')
    console.log('Cleared!')
    console.log('Now scanning from the TWS app...')
    try {
        const storedTickers = await redis.get('vol-scanner/stock-tickers');
        const arrayedStoredTickers = JSON.parse(storedTickers)
        // const response = (await PythonShell.run('./pyth/ATM_Vol_Dashboard.py', { args: arrayedStoredTickers, mode: 'json' }))[0]
        const pyCall = new PythonShell('./pyth/ATM_Vol_Dashboard.py', {
            args: arrayedStoredTickers,
            mode: 'json',
            pythonOptions: ['-u']
        })
        await pyCall.on('message', async (message) => {
            console.log('Received message', message)
        })
        // const response = (await )[0]
        // console.log(`Tickers successfully scanned: ${JSON.stringify(response)}`)
        // await redis.set('vol-scanner/scanned', JSON.stringify(response))
        // await sleep(3000)
        // const mockResponse = arrayedStoredTickers.map(ticker => ({
        //     symbol: ticker,
        //     impliedVolatility: getRandomNumber()
        // }))
        // res.status
        // (200).json({
        //     message: 'success',
        //     data: response
        // })
        // res.status(200).json(response)
    } catch (e) {
        res.status(500).json({error: e instanceof Error ? e.message : e});
    }
})

app.get('/vol-scanner/scanned', async (req, res) => {
    logger.info('TRIGGERED: /vol-scanner/scanned')
    try {
        const scanned = await redis.get('vol-scanner/scanned')
        if (scanned) {
            return res.status(200).json({
                data: JSON.parse(scanned)
            })
        } else return res.status(200).json({data: []})
    } catch (e) {
        res.status(500).json({error: e instanceof Error ? e.message : e});
    }
})

app.get('/ibkr-portfolio', async (req, res) => {
    logger.info('TRIGGERED: /ibkr-portfolio')
    let response
    try {
        const response = await (await PythonShell.run('./pyth/IBKR_UIDisplay.py'))[0]
        if (errors.some(error => response.includes(error))) {
            logger.error(response)
            throw new Error(response)
        } else {
            await redis.set('ibkr-portfolio/cached', response)
            console.log(`response stored on redis: ${response}`)
            return res.status(200).json(JSON.parse(response))
        }
    } catch (e) {
        console.error(e)
        return res.status(500).json({error: e instanceof Error ? e.message : e});
    }
})

app.get('/ibkr-portfolio/cached', async (req, res) => {
    logger.info('TRIGGERED: /ibkr-portfolio/cached')
    try {
        const cached = await redis.get('ibkr-portfolio/cached')
        if (cached) {
            console.log(`data existing: ${cached}`)
            return res.status(200).json(JSON.parse(cached))
        } else return res.status(200).json({})
    } catch (e) {
        console.error(e)
        return res.status(500).json({error: e instanceof Error ? e.message : e});
    }
})

app.post('/ibkr-portfolio/force-cache', async (req, res) => {
    logger.info('TRIGGERED: /ibkr-portfolio/force-cache')
    try {
        await redis.set('ibkr-portfolio/cached', JSON.stringify(req.body))
    } catch (e) {
        logger.error(e instanceof Error ? e.message : e);
    }
    return res.status(200).json({message: 'success'})
})

app.post('/vol-scanner/force-cache', async (req, res) => {
    logger.info('TRIGGERED: /vol-scanner/force-cache')
    try {
        await redis.set('vol-scanner/scanned', JSON.stringify(req.body))
    } catch (e) {
        logger.error(e instanceof Error ? e.message : e);
    }
    return res.status(200).json({message: 'success'})
})

// interface will be { Date: string, Date: string }
app.get('/earnings-calendar/points', async (req, res) => {
    const {startDate, endDate} = req.query;

    const startTimestamp = new Date(startDate).getTime();
    const endTimestamp = new Date(endDate).getTime();

    if (isNaN(startTimestamp) || isNaN(endTimestamp)) {
        return res.status(400).json({error: "Invalid date format"});
    }

    try {
        // Get event IDs within the date range
        const eventIds = await redis.zrangebyscore("calendar_events", startTimestamp, endTimestamp);

        if (eventIds.length === 0) {
            return res.json({events: []}); // No events found
        }

        // Fetch event details for each event ID
        const eventDetails = await Promise.all(
            eventIds.map(async (id) => {
                const details = await redis.hgetall(id);
                return {id, ...details};
            })
        );

        res.json(eventDetails);
    } catch (error) {
        res.status(500).json({error: error.message});
    }
});

app.get('/earnings-calendar/points/cached', async (req, res) => {
    const cachedData = await redis.get('earnings-calendar/points')
    if (!cachedData) return res.status(404).json({error: "No cached data"});
    return res.status(200).json(JSON.parse(cachedData))
})

app.post('/earnings-calendar/points/new', async (req, res) => {
    logger.info('TRIGGERED: /earnings-calendar/points/new')

    const {tickers, range} = req.body;
    console.log({tickers, range})
    try {
        const pyCall = await PythonShell.run('./pyth/Earnings_Cal.py', {
            args: [
                JSON.stringify(DEFAULT_TICKERS),
                range
            ],
            mode: 'text',
            pythonOptions: ['-u'],
        })

        // pyCall.on("message", message => {
        //     console.log('shell message: ', message)
        // })
        //
        // pyCall.end((err, code, signal) => {
        //     if (err) console.error('Python Script Error:', err);
        //     console.log('Python script finished with exit code:', code);
        // })
        await redis.set('earnings-calendar/points', pyCall[0])
        return res.status(200).json(JSON.parse(pyCall[0]))
    }
    catch (error) {
        res.status(500).json({error: error.message});
    }
})

app.post('/earnings-calendar/add/point', async (req, res) => {
    const events = await redis.zrangebyscore("calendar_events", "-inf", "+inf", "WITHSCORES");
    console.log({events});

    const {event, startDate, endDate} = req.body;
    if (!event || !startDate || !endDate) {
        return res.status(400).json({error: "One of the required fields is missing"});
    }

    // Convert startDate to a timestamp for sorting
    const startTimestamp = new Date(startDate).getTime();
    const endTimestamp = new Date(endDate).getTime();

    if (isNaN(startTimestamp) || isNaN(endTimestamp)) {
        return res.status(400).json({error: "Invalid date format"});
    }

    // Generate a unique event ID
    const eventId = `event:${startTimestamp}-${Math.random().toString(36).substring(2, 8)}`;

    try {
        // Store event in Sorted Set (using startDate as score)
        await redis.zadd("calendar_events", startTimestamp, eventId);

        // Store event details in Redis Hash
        await redis.hset(eventId, {
            event,
            startDate,
            endDate
        });

        res.json({message: "Event added successfully!", id: eventId});
    } catch (error) {
        res.status(500).json({error: error.message});
    }
});

app.post('/earnings-calendar/delete/point', async (req, res) => {
    const {id} = req.body;

    if (!id) {
        return res.status(400).json({error: "Event ID is required"});
    }

    try {
        // Check if event exists in Redis
        const eventExists = await redis.exists(id);
        if (!eventExists) {
            return res.status(404).json({error: "Event not found"});
        }

        // Remove event from Sorted Set
        await redis.zrem("calendar_events", id);

        // Delete event details from Hash
        await redis.del(id);

        res.json({message: "Event deleted successfully!"});
    } catch (error) {
        res.status(500).json({error: error.message});
    }
});

initializeStockTickers().then(() => {
    server.listen(PORT, () => {
        console.log(`Server is running on http://localhost:${PORT}`);
        console.log('Checking env variables on docker and here: ', {
            port: process.env.PORT,
            redis: process.env.REDIS_PORT,
            env: process.env.DERIBIT_CLIENT_ID,
        })
        if (DEMO) console.info('APP IS IN DEMO MODE')
    })
});