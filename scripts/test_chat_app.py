#!/usr/bin/env python3
"""
Test script for the ADK Chat Application
========================================

This script helps test the chat application by sending test messages to different agents
and verifying the responses. It can be used to test both local and cloud deployments.

Usage:
------
python scripts/test_chat_app.py [--url API_URL] [--agent AGENT_NAME] [--message "Your message"]

Examples:
--------
# Test local deployment with reddit_scout agent
python scripts/test_chat_app.py --agent reddit_scout --message "Tell me about Bitcoin"

# Test cloud deployment
python scripts/test_chat_app.py --url https://your-cloud-domain.com --agent speaker --message "Hello world"

# Interactive mode
python scripts/test_chat_app.py --interactive
"""

import argparse
import requests
import json
import uuid
import time
import sys
from typing import Optional, Dict, Any

def test_api_connection(base_url: str) -> bool:
    """Test if the API server is reachable."""
    try:
        response = requests.get(f"{base_url}/docs", timeout=5)
        return response.status_code == 200
    except:
        return False

def create_session(base_url: str, agent_name: str, user_id: str) -> Optional[str]:
    """Create a new session with the specified agent."""
    session_id = f"test-session-{int(time.time())}"
    url = f"{base_url}/apps/{agent_name}/users/{user_id}/sessions/{session_id}"
    
    try:
        response = requests.post(
            url,
            headers={"Content-Type": "application/json"},
            data=json.dumps({}),
            timeout=10
        )
        
        if response.status_code == 200:
            return session_id
        else:
            print(f"Failed to create session: {response.status_code} - {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Connection error: {str(e)}")
        return None

def send_message(base_url: str, agent_name: str, user_id: str, session_id: str, message: str) -> Optional[str]:
    """Send a message to the agent and return the response."""
    payload = {
        "app_name": agent_name,
        "user_id": user_id,
        "session_id": session_id,
        "new_message": {
            "role": "user",
            "parts": [{"text": message}]
        }
    }
    
    try:
        response = requests.post(
            f"{base_url}/run",
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload),
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"Error: {response.status_code} - {response.text}")
            return None
        
        # Process the response
        events = response.json()
        
        # Extract assistant's text response
        for event in events:
            if (event.get("content", {}).get("role") == "model" and 
                "text" in event.get("content", {}).get("parts", [{}])[0]):
                return event["content"]["parts"][0]["text"]
        
        # If no clear text response, return raw events
        return f"Raw response: {json.dumps(events, indent=2)}"
        
    except requests.exceptions.RequestException as e:
        print(f"Connection error: {str(e)}")
        return None

def interactive_mode(base_url: str, agent_name: str):
    """Run in interactive mode for testing."""
    user_id = f"test-user-{uuid.uuid4()}"
    
    print(f"🤖 Testing {agent_name} agent at {base_url}")
    print(f"👤 User ID: {user_id}")
    print("=" * 50)
    
    # Test connection
    if not test_api_connection(base_url):
        print("❌ Cannot connect to API server")
        return
    
    print("✅ Connected to API server")
    
    # Create session
    session_id = create_session(base_url, agent_name, user_id)
    if not session_id:
        print("❌ Failed to create session")
        return
    
    print(f"✅ Created session: {session_id}")
    print("\n💬 Interactive mode - type 'quit' to exit")
    print("-" * 50)
    
    while True:
        try:
            message = input("You: ").strip()
            if message.lower() in ['quit', 'exit', 'q']:
                break
            
            if not message:
                continue
            
            print("🤔 Thinking...")
            response = send_message(base_url, agent_name, user_id, session_id, message)
            
            if response:
                print(f"🤖 {agent_name}: {response}")
            else:
                print("❌ No response received")
            
            print("-" * 50)
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break

def main():
    parser = argparse.ArgumentParser(description="Test the ADK Chat Application")
    parser.add_argument("--url", default="http://localhost:8000", 
                       help="API base URL (default: http://localhost:8000)")
    parser.add_argument("--agent", default="reddit_scout",
                       help="Agent name to test (default: reddit_scout)")
    parser.add_argument("--message", 
                       help="Message to send (if not provided, runs in interactive mode)")
    parser.add_argument("--interactive", action="store_true",
                       help="Run in interactive mode")
    
    args = parser.parse_args()
    
    # Validate agent name
    valid_agents = ["reddit_scout", "speaker", "summarizer", "coordinator"]
    if args.agent not in valid_agents:
        print(f"❌ Invalid agent name. Valid options: {', '.join(valid_agents)}")
        sys.exit(1)
    
    # Run interactive mode if no message provided or --interactive flag used
    if args.interactive or not args.message:
        interactive_mode(args.url, args.agent)
        return
    
    # Single message test
    user_id = f"test-user-{uuid.uuid4()}"
    
    print(f"🤖 Testing {args.agent} agent at {args.url}")
    print(f"💬 Message: {args.message}")
    print("=" * 50)
    
    # Test connection
    if not test_api_connection(args.url):
        print("❌ Cannot connect to API server")
        sys.exit(1)
    
    print("✅ Connected to API server")
    
    # Create session
    session_id = create_session(args.url, args.agent, user_id)
    if not session_id:
        print("❌ Failed to create session")
        sys.exit(1)
    
    print(f"✅ Created session: {session_id}")
    
    # Send message
    print("🤔 Sending message...")
    response = send_message(args.url, args.agent, user_id, session_id, args.message)
    
    if response:
        print(f"✅ Response received:")
        print(f"🤖 {args.agent}: {response}")
    else:
        print("❌ No response received")
        sys.exit(1)

if __name__ == "__main__":
    main() 