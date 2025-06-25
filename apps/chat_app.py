"""
ADK Agent Chat Application
==========================

This Streamlit application provides a chat interface for interacting with any ADK agent.
It allows users to select different agents, create sessions, and have text-based conversations.

Features:
---------
- Agent selection dropdown
- Session management
- Text-based chat interface
- Cloud deployment support
- Configurable API endpoints

Requirements:
------------
- ADK API Server running (local or cloud)
- Agents registered and available in the ADK
- Streamlit and related packages installed

Usage:
------
1. Start the ADK API Server: `adk api_server` (local) or use cloud endpoint
2. Ensure agents are registered and working
3. Run this Streamlit app: `streamlit run apps/chat_app.py`
4. Select an agent and create a session
5. Start chatting with the selected agent

Architecture:
------------
- Session Management: Creates and manages ADK sessions for stateful conversations
- Message Handling: Sends user messages to the ADK API and processes responses
- Agent Selection: Allows users to choose different agents
- Cloud Support: Configurable API endpoints for local or cloud deployment

API Assumptions:
--------------
1. ADK API Server runs on configurable endpoint (default: localhost:8000)
2. Agents are registered with their respective app_names
3. Responses follow the ADK event structure with model outputs
4. Cloud deployment uses the same API structure as local deployment
"""

import streamlit as st
import requests
import json
import uuid
import time
import re
from typing import Optional, Dict, Any

# Set page config
st.set_page_config(
    page_title="ADK Agent Chat",
    page_icon="🤖",
    layout="wide"
)

# Constants
DEFAULT_API_BASE_URL = "http://localhost:8000"

# Available agents configuration
AVAILABLE_AGENTS = {
    "agents.reddit_scout": {
        "name": "Crypto Market Analyst",
        "description": "AI-powered crypto research assistant with market data, smart money flow, and social media analysis",
        "icon": "🔍"
    }
}

# Initialize session state variables
if "user_id" not in st.session_state:
    st.session_state.user_id = f"user-{uuid.uuid4()}"
    
if "session_id" not in st.session_state:
    st.session_state.session_id = None
    
if "messages" not in st.session_state:
    st.session_state.messages = []
    
if "selected_agent" not in st.session_state:
    st.session_state.selected_agent = None
    
if "api_base_url" not in st.session_state:
    st.session_state.api_base_url = DEFAULT_API_BASE_URL

# Helper to strip markdown and HTML tags
def strip_markdown_and_html(text):
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Remove Markdown bold/italics/code
    text = re.sub(r'[_*`]', '', text)
    return text

def create_session(agent_name: str) -> bool:
    """
    Create a new session with the selected agent.
    
    Args:
        agent_name (str): The name of the agent to create a session with
        
    Returns:
        bool: True if session was created successfully, False otherwise
    """
    session_id = f"session-{int(time.time())}"
    url = f"{st.session_state.api_base_url}/apps/{agent_name}/users/{st.session_state.user_id}/sessions/{session_id}"
    
    try:
        response = requests.post(
            url,
            headers={"Content-Type": "application/json"},
            data=json.dumps({}),
            timeout=90
        )
        
        if response.status_code == 200:
            st.session_state.session_id = session_id
            st.session_state.selected_agent = agent_name
            st.session_state.messages = []
            return True
        else:
            st.error(f"Failed to create session: {response.status_code} - {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        st.error(f"Connection error: {str(e)}")
        return False

def send_message(message: str) -> bool:
    """
    Send a message to the selected agent and process the response.
    
    Args:
        message (str): The user's message to send to the agent
        
    Returns:
        bool: True if message was sent and processed successfully, False otherwise
    """
    if not st.session_state.session_id or not st.session_state.selected_agent:
        st.error("No active session. Please create a session first.")
        return False
    
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": message})
    
    # Prepare request payload
    payload = {
        "app_name": st.session_state.selected_agent,
        "user_id": st.session_state.user_id,
        "session_id": st.session_state.session_id,
        "new_message": {
            "role": "user",
            "parts": [{"text": message}]
        }
    }
    try:
        response = requests.post(
            f"{st.session_state.api_base_url}/run",
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload),
            timeout=90
        )
        if response.status_code != 200:
            st.error(f"Error: {response.status_code} - {response.text}")
            return False
        events = response.json()
        # Add all events to chat history, labeled by type
        for event in events:
            content = event.get("content", {})
            role = content.get("role", "event")
            # Tool call (function_call)
            if "function_call" in content.get("parts", [{}])[0]:
                call = content["parts"][0]["function_call"]
                fn = call.get("name", "tool_call")
                args = call.get("args", {})
                # Markdown-only formatting
                arg_lines = []
                for k, v in args.items():
                    arg_lines.append(f"    - **{k}**: `{v}`")
                pretty_args = "\n".join(arg_lines) if arg_lines else "    - _No arguments_"
                st.session_state.messages.append({
                    "role": "tool_call",
                    "content": f"🔧 **Tool Call:** `{fn}`\n{pretty_args}"
                })
            # Tool response (function_response)
            elif "function_response" in content.get("parts", [{}])[0]:
                resp = content["parts"][0]["function_response"]
                fn = resp.get("name", "tool_response")
                result = resp.get("response", {})
                # Try to show only the main result if present
                main_result = result.get("result") if isinstance(result, dict) and "result" in result else result
                if isinstance(main_result, dict) or isinstance(main_result, list):
                    main_result_str = json.dumps(main_result, indent=2)
                else:
                    main_result_str = str(main_result)
                st.session_state.messages.append({
                    "role": "tool_response",
                    "content": f"🟢 **Tool Response:** `{fn}`\n{main_result_str}"
                })
            # Model/assistant message
            elif role == "model" and "text" in content.get("parts", [{}])[0]:
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": content["parts"][0]["text"]
                })
            # User message (should already be handled)
            elif role == "user" and "text" in content.get("parts", [{}])[0]:
                continue
            # Other event types
            else:
                continue  # Hide all other event types for minimalism
        return True
    except requests.exceptions.RequestException as e:
        st.error(f"Connection error: {str(e)}")
        return False

def clear_chat():
    """Clear the chat history."""
    st.session_state.messages = []

# UI Components
st.title("🤖 ADK Agent Chat")

# Sidebar for configuration
with st.sidebar:
    st.header("Configuration")
    
    # API Base URL configuration
    st.subheader("API Endpoint")
    api_url = st.text_input(
        "API Base URL",
        value=st.session_state.api_base_url,
        help="Enter the API server URL (e.g., http://localhost:8000 or https://your-cloud-domain.com)"
    )
    
    if api_url != st.session_state.api_base_url:
        st.session_state.api_base_url = api_url
        st.session_state.session_id = None  # Reset session when URL changes
        st.rerun()
    
    st.divider()
    
    # Agent selection
    st.subheader("Agent Selection")
    agent_options = {f"{agent_info['icon']} {agent_info['name']}": agent_id 
                    for agent_id, agent_info in AVAILABLE_AGENTS.items()}
    
    selected_agent_display = st.selectbox(
        "Choose an Agent",
        options=list(agent_options.keys()),
        help="Select the agent you want to chat with"
    )
    
    selected_agent_id = agent_options[selected_agent_display]
    
    # Show agent description
    if selected_agent_id in AVAILABLE_AGENTS:
        agent_info = AVAILABLE_AGENTS[selected_agent_id]
        st.info(f"**{agent_info['name']}**: {agent_info['description']}")
    
    st.divider()
    
    # Session management
    st.subheader("Session Management")
    
    if st.session_state.session_id and st.session_state.selected_agent == selected_agent_id:
        st.success(f"Active session: {st.session_state.session_id}")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 New Session"):
                create_session(selected_agent_id)
                st.rerun()
        with col2:
            if st.button("🗑️ Clear Chat"):
                clear_chat()
                st.rerun()
    else:
        st.warning("No active session")
        if st.button("➕ Create Session"):
            create_session(selected_agent_id)
            st.rerun()
    
    st.divider()
    
    # Connection status
    st.subheader("Connection Status")
    try:
        health_response = requests.get(f"{st.session_state.api_base_url}/docs", timeout=5)
        if health_response.status_code == 200:
            st.success("✅ Connected to API Server")
        else:
            st.warning("⚠️ API Server responding but may have issues")
    except:
        st.error("❌ Cannot connect to API Server")
    
    st.caption(f"User ID: {st.session_state.user_id}")

# Main chat interface
st.subheader("Conversation")

# Display messages
chat_container = st.container()

with chat_container:
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.chat_message("user").write(msg["content"])
        elif msg["role"] == "assistant":
            clean_content = strip_markdown_and_html(msg["content"])
            st.chat_message("assistant").write(clean_content)
        elif msg["role"] == "tool_call":
            st.chat_message("assistant").markdown(msg["content"])
        elif msg["role"] == "tool_response":
            st.chat_message("assistant").markdown(msg["content"])
        else:
            continue

# Input for new messages
if st.session_state.session_id and st.session_state.selected_agent == selected_agent_id:
    user_input = st.chat_input("Type your message...")
    if user_input:
        with st.spinner("Sending message..."):
            success = send_message(user_input)
            if success:
                st.rerun()
else:
    st.info("👈 Select an agent and create a session to start chatting")

# Footer
st.divider()
st.caption("Built with ADK Made Simple - [GitHub Repository](https://github.com/chongdashu/adk-made-simple)") 