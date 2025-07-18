import os
import random
import re
import traceback
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import nltk
import praw
import requests
import tweepy
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.tools import BaseTool as Tool
from nltk import word_tokenize
from nltk.corpus import stopwords
from nltk.probability import FreqDist
from praw.exceptions import PRAWException
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from pathlib import Path

# Use local nltk_data directory for cloud compatibility
nltk_data_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../nltk_data'))
if nltk_data_path not in nltk.data.path:
    nltk.data.path.append(nltk_data_path)

# Define the list of packages to ensure are downloaded
required_packages = ["punkt", "stopwords", "punkt_tab"]

for package in required_packages:
    try:
        # The resource names can sometimes differ from package names
        # We'll try to find common resource paths.
        if package == "punkt" or package == "punkt_tab":
             nltk.data.find(f"tokenizers/{package}")
        else:
             nltk.data.find(f"corpora/{package}")
    except LookupError:
        print(f"--- NLTK package '{package}' not found. Downloading... ---")
        nltk.download(package, download_dir=nltk_data_path)
# --- End NLTK Configuration ---

# Load environment variables from .env file
load_dotenv()


# ------------------------------------------------------------------------------
# Reddit Tools
# ------------------------------------------------------------------------------
def get_reddit_gamedev_news(subreddit: str, limit: int = 5) -> dict[str, list[str]]:
    """Fetches top post titles from a specified subreddit."""
    client_id = os.getenv("REDDIT_CLIENT_ID")
    client_secret = os.getenv("REDDIT_CLIENT_SECRET")
    user_agent = os.getenv("REDDIT_USER_AGENT")

    if not all([client_id, client_secret, user_agent]):
        return {subreddit: ["Error: Reddit API credentials not configured."]}

    try:
        reddit = praw.Reddit(
            client_id=client_id, client_secret=client_secret, user_agent=user_agent
        )
        sub = reddit.subreddit(subreddit)
        titles = [post.title for post in sub.hot(limit=limit)]
        return {subreddit: titles or [f"No recent hot posts found in r/{subreddit}."]}
    except PRAWException as e:
        return {
            subreddit: [
                f"Error accessing r/{subreddit}. It may be private or non-existent. Details: {e}"
            ]
        }
    except Exception as e:
        return {subreddit: [f"An unexpected error occurred: {e}"]}


# ------------------------------------------------------------------------------
# CoinGecko Tools
# ------------------------------------------------------------------------------
NANSEN_TO_COINGECKO_ID = {
    "ket": "rocket-pool-eth",
}

def search_coin_id(query: str) -> Optional[str]:
    """Searches CoinGecko for a coin ID, with a fallback for known symbol discrepancies."""
    api_key = os.getenv("COINGECKO_API_KEY")

    # Check for custom mapping first
    if query.lower() in NANSEN_TO_COINGECKO_ID:
        return NANSEN_TO_COINGECKO_ID[query.lower()]

    url = "https://pro-api.coingecko.com/api/v3/search"
    headers = {"x-cg-pro-api-key": api_key} if api_key else {}
    
    try:
        response = requests.get(url, params={"query": query}, headers=headers)
        response.raise_for_status()
        coins = response.json().get("coins", [])

        if not coins:
            return None

        # Look for an exact symbol match first
        query_lower = query.lower()
        for coin in coins:
            if coin.get("symbol", "").lower() == query_lower:
                return coin.get("id")

        # If no exact symbol match, return the first result (which is often a name match)
        return coins[0].get("id")
    except Exception:
        return None


def get_coin_details(coin_id: str) -> dict:
    """
    Fetches detailed cryptocurrency data from CoinGecko. It determines if the
    asset is a native currency or a token with a contract address on a supported
    chain.

    Args:
        coin_id: The official CoinGecko ID of the cryptocurrency.

    Returns:
        A dictionary detailing market data and asset type (native or token).
    """
    if not coin_id:
        return {
            "status": "error",
            "result": "Lame. You forgot the coin_id. Can't do much without that.",
        }

    api_key = os.getenv("COINGECKO_API_KEY")
    headers = {"x-cg-pro-api-key": api_key} if api_key else {}
    base_url = (
        "https://pro-api.coingecko.com/api/v3"
        if api_key
        else "https://api.coingecko.com/api/v3"
    )
    url = f"{base_url}/coins/{coin_id}"

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()

        market_data = data.get("market_data", {})
        current_price = market_data.get("current_price", {}).get("usd", "N/A")
        market_cap = market_data.get("market_cap", {}).get("usd", "N/A")
        total_volume = market_data.get("total_volume", {}).get("usd", "N/A")
        high_24h = market_data.get("high_24h", {}).get("usd", "N/A")
        low_24h = market_data.get("low_24h", {}).get("usd", "N/A")

        # Determine asset type
        asset_platform_id = data.get("asset_platform_id")
        is_native = not asset_platform_id and data.get("id") in [
            "solana",
            "ethereum",
            "binancecoin",
            "avalanche-2",
        ]
        
        found_chain = None
        contract_address = None
        
        if is_native:
            found_chain = data.get("id")
        else:
            supported_chains = ["solana", "ethereum", "arbitrum", "polygon", "avalanche", "base", "bnb"]
            platforms = data.get("platforms", {})
            for chain in supported_chains:
                if platforms.get(chain):
                    found_chain = chain
                    contract_address = platforms[chain]
                    break
        
        result_summary = (
            f"Okay, here's the tea on {data.get('name', 'this coin')}. "
            f"Right now, it's trading at ${current_price:,.2f}. "
            f"Total market cap is a hefty ${market_cap:,.0f}."
        )

        return {
            "status": "success",
            "coin_id": coin_id,
            "is_native_asset": is_native,
            "chain": found_chain,
            "contract_address": contract_address,
            "result": result_summary,
        }

    except requests.exceptions.HTTPError as e:
        return {"status": "error", "result": f"CoinGecko API error: {e.response.status_code}"}
    except requests.exceptions.RequestException as e:
        return {"status": "error", "result": f"Network error: {e}"}


# ------------------------------------------------------------------------------
# Twitter/X Tools
# ------------------------------------------------------------------------------
def get_twitter_client():
    """Initializes and returns a Tweepy client."""
    api_key = os.getenv("TWITTER_API_KEY")
    api_secret = os.getenv("TWITTER_API_SECRET")
    bearer_token = os.getenv("TWITTER_BEARER_TOKEN")
    if not all([api_key, api_secret, bearer_token]):
        return None
    try:
        return tweepy.Client(
            bearer_token=bearer_token,
            consumer_key=api_key,
            consumer_secret=api_secret,
            wait_on_rate_limit=True,
        )
    except Exception:
        return None


def get_crypto_community_insights(
    coin_name: str, coin_symbol: Optional[str] = None
) -> dict:
    """Provides a summary of community sentiment on Twitter."""
    client = get_twitter_client()
    if not client:
        return {
            "status": "error",
            "result": "Could not initialize Twitter client. Please check API credentials.",
        }

    query = f'"{coin_name}" OR "{coin_symbol}"' if coin_symbol else f'"{coin_name}"'
    query += " lang:en -is:retweet"

    try:
        response = client.search_recent_tweets(
            query, tweet_fields=["text"], max_results=100
        )
        tweets = response.data
        if not tweets:
            return {
                "status": "no_data",
                "result": "No recent community discussion found on Twitter for this coin.",
            }

        text = " ".join([tweet.text for tweet in tweets])
        analyzer = SentimentIntensityAnalyzer()
        sentiment = analyzer.polarity_scores(text)["compound"]
        assessment = (
            "Positive" if sentiment >= 0.05 else "Negative" if sentiment <= -0.05 else "Neutral"
        )
        
        stop_words = set(stopwords.words("english"))
        words = [w.lower() for w in word_tokenize(text) if w.isalpha() and w.lower() not in stop_words]
        themes = ", ".join([w for w, _ in FreqDist(words).most_common(5)])
        themes_summary = f"Key discussion themes: {themes}." if themes else ""

        return {
            "status": "success",
            "result": f"Overall sentiment is {assessment}. {themes_summary}",
        }
    except Exception as e:
        return {
            "status": "error",
            "result": f"An unexpected error occurred. Details: {traceback.format_exc()}",
        }


def get_crypto_rumors_and_news(
    coin_name: str, coin_symbol: Optional[str] = None
) -> dict:
    """Looks for rumors and breaking news on Twitter."""
    client = get_twitter_client()
    if not client:
        return {
            "status": "error",
            "result": "Could not initialize Twitter client. Please check API credentials.",
        }
    
    q_part = f'"{coin_name}" OR "{coin_symbol}"' if coin_symbol else f'"{coin_name}"'
    query = f"({q_part}) (rumor OR news OR announcement OR leak OR speculation) lang:en -is:retweet"

    try:
        tweets = client.search_recent_tweets(query=query, max_results=10, tweet_fields=["text"])
        if not tweets.data:
            return {
                "status": "no_data",
                "result": f"Couldn't find any recent rumors or news about {coin_name}.",
            }
        
        summary = "Found some chatter. Here's a top tweet: " + tweets.data[0].text
        return {"status": "success", "result": summary}
    except Exception:
        return {
            "status": "error",
            "result": f"An unexpected error occurred. Details: {traceback.format_exc()}",
        }


# ------------------------------------------------------------------------------
# Nansen Tools
# ------------------------------------------------------------------------------
def _fetch_nansen_flow_intelligence(chain: str, token_address: str, timeframe: str = "1d") -> dict:
    """Helper to fetch and process smart money flow from Nansen using flow-intelligence for a given timeframe."""
    api_key = os.getenv("NANSEN_API_KEY")
    if not api_key:
        print("[DEBUG] Nansen API key is missing.")
        return {"status": "error", "result": "Nansen API key is missing."}

    url = "https://api.nansen.ai/api/beta/tgm/flow-intelligence"
    headers = {"apiKey": api_key, "Content-Type": "application/json"}
    
    payload = {
        "parameters": {
            "chain": chain.lower(),
            "tokenAddress": token_address,
            "timeframe": timeframe,
        }
    }

    print(f"[DEBUG] Fetching Nansen smart money flow for chain: {chain}, token_address: {token_address}, timeframe: {timeframe}")
    print(f"[DEBUG] Payload: {payload}")

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        print(f"[DEBUG] Nansen API status code: {response.status_code}")
        print(f"[DEBUG] Nansen API raw response: {response.text}")
        response.raise_for_status()
        data = response.json()

        if not isinstance(data, list) or not data:
            print("[DEBUG] No recent smart money data was found.")
            return {"status": "success", "result": "No recent smart money data was found."}
        
        latest_entry = data[0]
        netflow_usd = float(latest_entry.get("smartTraderFlow") or 0)

        # Format the output string
        if abs(netflow_usd) >= 1_000_000:
            flow_str = f"${netflow_usd / 1_000_000:,.2f}M"
        elif abs(netflow_usd) >= 1_000:
            flow_str = f"${netflow_usd / 1_000:,.2f}K"
        else:
            flow_str = f"${netflow_usd:,.2f}"

        return {"status": "success", "result": flow_str, "raw": latest_entry}

    except requests.exceptions.HTTPError as e:
        print(f"[DEBUG] Nansen API HTTP error: {e.response.status_code} - {e.response.text}")
        if e.response.status_code == 404:
            return {"status": "error", "result": "Unsupported chain or token for Nansen smart money flow."}
        return {"status": "error", "result": f"Nansen API returned an error: {e.response.status_code} - {e.response.text}"}
    except requests.exceptions.RequestException as e:
        print(f"[DEBUG] Network error connecting to Nansen: {e}")
        return {"status": "error", "result": f"Network error connecting to Nansen: {e}"}

def _fetch_nansen_trading_patterns(chain: str, token_address: str) -> dict:
    """Fetch trading patterns for a token from Nansen (example endpoint, adjust as needed)."""
    api_key = os.getenv("NANSEN_API_KEY")
    if not api_key:
        return {"status": "error", "result": "Nansen API key is missing."}
    # This endpoint is illustrative; adjust to the actual Nansen endpoint for trading patterns
    url = f"https://api.nansen.ai/api/beta/tgm/trading-patterns"
    headers = {"apiKey": api_key, "Content-Type": "application/json"}
    payload = {
        "parameters": {
            "chain": chain.lower(),
            "tokenAddress": token_address,
        }
    }
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        return {"status": "success", "result": data}
    except Exception as e:
        return {"status": "error", "result": str(e)}

def get_token_smart_money_flow(chain: str, token_address: str) -> dict:
    """
    Fetches smart money flow data from Nansen for a specific TOKEN for 24h, 7d, 30d, and trading patterns.
    """
    if not all([chain, token_address]):
        return {"status": "error", "result": "Missing chain or token address."}

    timeframes = {"24h": "1d", "7d": "7d", "30d": "30d"}
    flows = {}
    for label, tf in timeframes.items():
        flows[label] = _fetch_nansen_flow_intelligence(chain, token_address, tf)
    trading_patterns = _fetch_nansen_trading_patterns(chain, token_address)

    # Build summary
    summary = []
    for label in ["24h", "7d", "30d"]:
        if flows[label]["status"] == "success":
            summary.append(f"Net smart money flow ({label}): {flows[label]['result']}")
        else:
            summary.append(f"Net smart money flow ({label}): Error: {flows[label]['result']}")
    if trading_patterns["status"] == "success":
        summary.append(f"Trading patterns: {trading_patterns['result']}")
    else:
        summary.append(f"Trading patterns: Error: {trading_patterns['result']}")
    return {"status": "success", "result": "\n".join(summary), "flows": flows, "trading_patterns": trading_patterns}

def get_native_asset_smart_money_flow(chain: str) -> dict:
    """
    Fetches smart money flow data from Nansen for a NATIVE asset (e.g., SOL, ETH).

    Args:
        chain: The blockchain name (e.g., 'solana', 'ethereum').

    Returns:
        A dictionary with a summary of smart money inflows/outflows for the chain.
    """
    if not chain:
        return {"status": "error", "result": "Missing chain name."}
        
    native_asset_addresses = {
        "solana": "So11111111111111111111111111111111111111112",
        "ethereum": "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",
    }
    token_address = native_asset_addresses.get(chain.lower())
    if not token_address:
        return {"status": "error", "result": f"Smart money flow not supported for native asset on '{chain}'."}

    return _fetch_nansen_flow_intelligence(chain, token_address)


# ------------------------------------------------------------------------------
# Agent Definition
# ------------------------------------------------------------------------------
class RedditScout(Agent):
    """A scout that that can get posts from subreddits."""

    def __init__(self, **kwargs):
        super().__init__(
            name="reddit_scout",
            description="A crypto research assistant that combines market data with social media analysis and smart money insights.",
            model="gemini-2.5-flash",
            instruction="""
You are Naomi, a sharp-witted, Gen Z crypto market analyst. You are confident and you ALWAYS back up your sass with hard data. Follow this workflow precisely.

1.  **Get Coin ID**: Use `search_coin_id` to get the CoinGecko ID.

2.  **Get Coin Details**: Use `get_coin_details` with the ID. This will tell you if it's a native asset or a token.

3.  **Get Smart Money Flow**:
    *   If `is_native_asset` was true, call `get_native_asset_smart_money_flow` using the `chain` from the previous step.
    *   If `is_native_asset` was false and you have a `contract_address`, call `get_token_smart_money_flow` with the `chain` and `contract_address`.
    *   If you couldn't get smart money data for any reason, just move on.

4.  **Get Social Sentiment**: Use `get_crypto_community_insights`.

5.  **Synthesize Report**: Combine the results from all tools into a final summary. Give your take on what the data means in your signature style.
""",
            tools=[
                search_coin_id,
                get_coin_details,
                get_crypto_community_insights,
                get_token_smart_money_flow,
                get_native_asset_smart_money_flow,
            ],
            **kwargs,
        )

root_agent = RedditScout()
agent = root_agent  # Compatibility alias