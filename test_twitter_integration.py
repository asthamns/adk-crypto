#!/usr/bin/env python3
"""
Test script for Twitter API integration.
This script tests the new Twitter functions without requiring the full bot setup.
"""

import os
import sys
from dotenv import load_dotenv

# Add the agents directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'agents'))

# Load environment variables
load_dotenv()

def test_twitter_credentials():
    """Test if Twitter credentials are properly configured."""
    print("Testing Twitter API credentials...")
    
    required_vars = ['TWITTER_API_KEY', 'TWITTER_API_SECRET', 'TWITTER_BEARER_TOKEN']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing Twitter API credentials: {', '.join(missing_vars)}")
        print("Please add them to your .env file:")
        print("TWITTER_API_KEY=your_api_key_here")
        print("TWITTER_API_SECRET=your_api_secret_here")
        print("TWITTER_BEARER_TOKEN=your_bearer_token_here")
        return False
    
    print("✅ Twitter API credentials found")
    return True

def test_twitter_client():
    """Test Twitter client initialization."""
    print("\nTesting Twitter client initialization...")
    
    try:
        from agents.reddit_scout.agent import get_twitter_client
        client = get_twitter_client()
        
        if client:
            print("✅ Twitter client initialized successfully")
            return True
        else:
            print("❌ Failed to initialize Twitter client")
            return False
    except Exception as e:
        print(f"❌ Error initializing Twitter client: {e}")
        return False

def test_sentiment_analysis():
    """Test sentiment analysis function."""
    print("\nTesting sentiment analysis...")
    
    try:
        from agents.reddit_scout.agent import analyze_sentiment
        
        # Test with positive text
        positive_text = "Bitcoin is amazing and going to the moon! 🚀"
        sentiment = analyze_sentiment(positive_text)
        print(f"Positive text sentiment: {sentiment['sentiment']}")
        
        # Test with negative text
        negative_text = "This crypto crash is terrible and I'm losing money"
        sentiment = analyze_sentiment(negative_text)
        print(f"Negative text sentiment: {sentiment['sentiment']}")
        
        # Test with neutral text
        neutral_text = "Bitcoin price is currently at $50,000"
        sentiment = analyze_sentiment(neutral_text)
        print(f"Neutral text sentiment: {sentiment['sentiment']}")
        
        print("✅ Sentiment analysis working correctly")
        return True
    except Exception as e:
        print(f"❌ Error in sentiment analysis: {e}")
        return False

def test_twitter_functions():
    """Test Twitter API functions (requires valid credentials)."""
    print("\nTesting Twitter API functions...")
    
    if not test_twitter_credentials():
        print("Skipping Twitter API tests due to missing credentials")
        return False
    
    try:
        from agents.reddit_scout.agent import get_trending_crypto_news, get_crypto_community_insights
        
        # Test trending crypto news (should work even with limited data)
        print("Testing get_trending_crypto_news...")
        trending_result = get_trending_crypto_news(limit=3)
        if 'error' in trending_result:
            print(f"⚠️  Trending news test: {trending_result['error']}")
        else:
            print(f"✅ Trending news test: Found {trending_result.get('total_topics_found', 0)} topics")
        
        # Test community insights (should work even with limited data)
        print("Testing get_crypto_community_insights...")
        community_result = get_crypto_community_insights(limit=10)
        if 'error' in community_result:
            print(f"⚠️  Community insights test: {community_result['error']}")
        else:
            print(f"✅ Community insights test: Analyzed {community_result.get('total_tweets_analyzed', 0)} tweets")
        
        return True
    except Exception as e:
        print(f"❌ Error testing Twitter functions: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Testing Twitter API Integration")
    print("=" * 50)
    
    tests = [
        test_twitter_credentials,
        test_twitter_client,
        test_sentiment_analysis,
        test_twitter_functions
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Twitter integration is ready to use.")
    elif passed >= 2:
        print("⚠️  Some tests passed. Check the setup guide for missing credentials.")
    else:
        print("❌ Most tests failed. Please check your setup and credentials.")
    
    print("\nNext steps:")
    print("1. Add your Twitter API credentials to .env file")
    print("2. Test with your bot by asking questions like:")
    print("   - 'What's the sentiment around Bitcoin?'")
    print("   - 'What's trending in crypto?'")
    print("   - 'What are people saying about SOL?'")

if __name__ == "__main__":
    main() 