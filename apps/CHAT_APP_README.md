# ADK Chat Application

A modern, text-based chat interface for interacting with ADK (Agent Development Kit) agents. This application provides a user-friendly way to chat with different AI agents, whether they're running locally or deployed in the cloud.

## Features

- 🤖 **Multi-Agent Support**: Chat with different ADK agents (Reddit Scout, Speaker, Summarizer, Coordinator)
- 🌐 **Cloud Deployment Ready**: Works with both local and cloud-deployed ADK API servers
- 💬 **Real-time Chat Interface**: Modern chat UI with message history
- 🔧 **Configurable Endpoints**: Easy switching between different API servers
- 📱 **Responsive Design**: Works on desktop and mobile devices
- 🔄 **Session Management**: Create new sessions and manage conversation state
- 📊 **Connection Status**: Real-time monitoring of API server connectivity

## Quick Start

### 1. Prerequisites

- Python 3.8+ with virtual environment
- ADK API Server running (local or cloud)
- Required packages installed: `pip install -r requirements.txt`

### 2. Run the Chat Application

```bash
# From the project root
streamlit run apps/chat_app.py
```

The application will open in your browser at `http://localhost:8501`.

### 3. Configure and Connect

1. **Set API Endpoint**: In the sidebar, enter your API server URL:
   - Local: `http://localhost:8000`
   - Cloud: `https://your-cloud-domain.com`

2. **Select Agent**: Choose from available agents:
   - 🔍 **Reddit Scout**: Crypto research with market data
   - 🔊 **Speaker Agent**: Text-to-speech capabilities
   - 📰 **Summarizer**: News analysis and summarization
   - 🎯 **Coordinator**: Multi-agent task coordination

3. **Create Session**: Click "Create Session" to start chatting

## Usage

### Local Deployment

1. **Start ADK API Server**:
   ```bash
   cd agents
   adk api_server
   ```

2. **Run Chat App**:
   ```bash
   streamlit run apps/chat_app.py
   ```

3. **Configure**:
   - API URL: `http://localhost:8000`
   - Select your preferred agent
   - Create a session and start chatting

### Cloud Deployment

1. **Deploy your ADK agents** to your cloud platform
2. **Run Chat App locally**:
   ```bash
   streamlit run apps/chat_app.py
   ```

3. **Configure**:
   - API URL: Your cloud endpoint (e.g., `https://your-app.herokuapp.com`)
   - Select agent and create session

### Testing

Use the provided test script to verify your setup:

```bash
# Test local deployment
python scripts/test_chat_app.py --agent reddit_scout --message "Tell me about Bitcoin"

# Test cloud deployment
python scripts/test_chat_app.py --url https://your-cloud-domain.com --agent speaker --message "Hello world"

# Interactive testing mode
python scripts/test_chat_app.py --interactive
```

## Configuration

### Environment Variables

The chat application uses the following environment variables (if needed):

```bash
# Optional: Set default API URL
DEFAULT_API_URL=http://localhost:8000

# Optional: Set Streamlit configuration
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
```

### Customizing Agents

To add or modify agents, edit the `AVAILABLE_AGENTS` dictionary in `apps/chat_app.py`:

```python
AVAILABLE_AGENTS = {
    "your_agent": {
        "name": "Your Agent Name",
        "description": "Description of what your agent does",
        "icon": "🎯"
    },
    # ... existing agents
}
```

## API Requirements

The chat application expects the ADK API server to provide:

1. **Session Management**:
   ```
   POST /apps/{app_name}/users/{user_id}/sessions/{session_id}
   ```

2. **Message Processing**:
   ```
   POST /run
   ```

3. **Health Check**:
   ```
   GET /docs
   ```

### Request Format

```json
{
  "app_name": "agent_name",
  "user_id": "user_id",
  "session_id": "session_id",
  "new_message": {
    "role": "user",
    "parts": [{"text": "Your message"}]
  }
}
```

### Response Format

The application expects ADK event format:

```json
[
  {
    "content": {
      "role": "model",
      "parts": [{"text": "Agent response"}]
    }
  }
]
```

## Troubleshooting

### Common Issues

1. **"Cannot connect to API Server"**
   - Verify the API server is running
   - Check the API URL in the sidebar
   - Ensure no firewall blocking the connection

2. **"Failed to create session"**
   - Verify the agent name is correct
   - Check if the agent is registered in the ADK
   - Review API server logs for errors

3. **"No response received"**
   - Check if the agent has proper API keys configured
   - Review agent-specific error messages
   - Verify the agent is functioning correctly

4. **"Response received but couldn't extract text"**
   - The agent may be returning a non-standard response format
   - Check the raw response for debugging
   - Verify the agent is properly configured

### Debug Mode

Enable debug mode by setting the environment variable:

```bash
export STREAMLIT_LOGGER_LEVEL=debug
streamlit run apps/chat_app.py
```

### Logs

Check Streamlit logs for detailed error information:

```bash
# View Streamlit logs
streamlit run apps/chat_app.py --logger.level debug
```

## Development

### Project Structure

```
apps/
├── chat_app.py              # Main chat application
├── speaker_app.py           # Speaker-specific app
├── a2a_speaker_app.py       # A2A speaker app
└── CHAT_APP_README.md       # This file

scripts/
└── test_chat_app.py         # Testing script
```

### Adding New Features

1. **New Agent Types**: Add to `AVAILABLE_AGENTS` dictionary
2. **Custom UI Elements**: Modify the Streamlit components
3. **Enhanced Error Handling**: Add specific error cases
4. **Additional Configuration**: Extend the sidebar options

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Support

- **GitHub Issues**: Report bugs and feature requests
- **Documentation**: Check the main [README.md](../README.md)
- **Community**: Join discussions in the repository

## License

This project is part of the [ADK Made Simple](https://github.com/chongdashu/adk-made-simple) repository.

---

**Built with ❤️ using [Streamlit](https://streamlit.io) and [Google ADK](https://ai.google.dev/agents)** 