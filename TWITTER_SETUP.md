# Twitter API Integration Setup Guide

This guide will help you set up the Twitter/X API integration for social media sentiment analysis in your crypto bot.

## Required Environment Variables

Add these to your `.env` file:

```bash
# Twitter API Credentials
TWITTER_API_KEY=your_twitter_api_key_here
TWITTER_API_SECRET=your_twitter_api_secret_here
TWITTER_BEARER_TOKEN=your_twitter_bearer_token_here
```

## Getting Twitter API Credentials

1. **Create a Twitter Developer Account**:
   - Go to [Twitter Developer Portal](https://developer.twitter.com/)
   - Sign in with your Twitter account
   - Apply for a developer account if you haven't already

2. **Create a New App**:
   - In the developer portal, click "Create App"
   - Fill in the required information
   - Select "Read" permissions (for searching tweets)

3. **Get Your Credentials**:
   - In your app dashboard, go to "Keys and Tokens"
   - Copy the following:
     - API Key (Consumer Key)
     - API Secret (Consumer Secret)
     - Bearer Token

## New Features Added

### 1. Social Media Sentiment Analysis (`get_crypto_sentiment`)
- Analyzes Twitter sentiment for any cryptocurrency
- Provides sentiment distribution (positive/negative/neutral percentages)
- Includes engagement metrics (likes, retweets, replies)
- Uses both VADER and TextBlob for accurate sentiment analysis

**Usage Examples**:
- "What's the sentiment around Bitcoin?"
- "How are people feeling about SOL?"
- "What's the social media mood for ETH?"

### 2. Trending Crypto News (`get_trending_crypto_news`)
- Identifies trending crypto topics on Twitter
- Groups discussions by cryptocurrency
- Provides engagement metrics and sample tweets
- Shows what's currently hot in the crypto space

**Usage Examples**:
- "What's trending in crypto right now?"
- "What are the hot topics in crypto?"
- "What's everyone talking about in crypto?"

### 3. Community Insights (`get_crypto_community_insights`)
- Analyzes what crypto communities are discussing
- Categorizes discussions by themes (price, technology, regulation, etc.)
- Identifies top influencers in the space
- Provides sentiment analysis for each discussion theme

**Usage Examples**:
- "What are people saying about crypto?"
- "What's the community talking about for Bitcoin?"
- "What are the main discussion themes around SOL?"

### 4. Rumors and News Scanner (`get_crypto_rumors_and_news`)
- Scans for crypto rumors, news, and potential market-moving information
- Calculates credibility scores based on account verification, followers, and engagement
- Identifies high-credibility vs low-credibility sources
- Provides sentiment analysis for each piece of news

**Usage Examples**:
- "What rumors are circulating about Bitcoin?"
- "What news is affecting SOL?"
- "What's the latest crypto news?"

## Installation

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set Environment Variables**:
   - Copy the example above to your `.env` file
   - Replace the placeholder values with your actual Twitter API credentials

3. **Test the Integration**:
   - Start your bot
   - Ask questions like:
     - "What's the sentiment around Bitcoin?"
     - "What's trending in crypto?"
     - "What are people saying about SOL?"

## Features Overview

The bot now provides comprehensive social media analysis:

- **Real-time sentiment analysis** for any cryptocurrency
- **Trending topic detection** in the crypto space
- **Community discussion analysis** with theme categorization
- **Rumor and news scanning** with credibility scoring
- **Influencer identification** in the crypto community
- **Engagement metrics** for social media posts

## Error Handling

The bot gracefully handles:
- Missing Twitter API credentials
- Rate limiting from Twitter API
- No recent tweets found for specific queries
- Network connectivity issues

If Twitter API is not configured, the bot will inform users and continue to provide other crypto data from CoinGecko.

## Rate Limits

Twitter API has rate limits:
- 450 requests per 15-minute window for search endpoints
- The bot includes automatic rate limit handling
- Consider upgrading to Twitter API v2 Academic Research access for higher limits

## Security Notes

- Never commit your `.env` file to version control
- Keep your Twitter API credentials secure
- Consider using environment-specific credentials for development/production 