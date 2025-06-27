# Naomi ADK Bot

This project is an advanced crypto research assistant powered by Google ADK and Nansen API.
It provides market data, smart money analytics (24h, 7d, 30d), trading patterns, and social sentiment for any token.

## Features
- CoinGecko integration for market data
- Nansen API for smart money flows and trading patterns (24h, 7d, 30d)
- Twitter/X sentiment analysis
- Modular agent design (Google ADK)

## Setup

1. **Clone the repo and create a `.env` file with your API keys:**
    ```
    NANSEN_API_KEY=your_nansen_key
    COINGECKO_API_KEY=your_coingecko_key
    # ...other keys as needed
    ```

2. **Install dependencies:**
    ```
    pip install -r requirements.txt
    ```

3. **Run the agent:**
    ```
    adk run reddit_scout
    ```

## License
Proprietary. All rights reserved.
