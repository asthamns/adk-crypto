"""
Entrypoint for the Reddit Scout (Crypto Market Analyst) agent API server.
This script creates the FastAPI app and starts the server on the correct port for Render.
"""

import os
import uvicorn
from dotenv import load_dotenv
from common.a2a_server import create_agent_server
from .agent import root_agent  # Should be an async coroutine or instance
from .agent import TaskManager  # If TaskManager is defined in agent.py
import asyncio

# Load environment variables from .env if present
print("[DEBUG] Loading environment variables...")
load_dotenv()
print("[DEBUG] Environment variables loaded.")

async def main():
    print("[DEBUG] Starting main()...")
    # If root_agent is a coroutine, await it; otherwise, use directly
    try:
        print("[DEBUG] Loading agent instance...")
        agent_instance = await root_agent if asyncio.iscoroutine(root_agent) else root_agent
        print(f"[DEBUG] Agent instance loaded: {getattr(agent_instance, 'name', str(agent_instance))}")
    except Exception as e:
        print(f"[ERROR] Failed to load agent instance: {e}")
        raise
    try:
        print("[DEBUG] Creating TaskManager...")
        task_manager = TaskManager(agent=agent_instance)
        print("[DEBUG] TaskManager created.")
    except Exception as e:
        print(f"[ERROR] Failed to create TaskManager: {e}")
        raise
    try:
        print("[DEBUG] Creating FastAPI app...")
        app = create_agent_server(
            name=getattr(agent_instance, 'name', 'RedditScout'),
            description=getattr(agent_instance, 'description', 'Crypto Market Analyst agent.'),
            task_manager=task_manager
        )
        print("[DEBUG] FastAPI app created.")
    except Exception as e:
        print(f"[ERROR] Failed to create FastAPI app: {e}")
        raise
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    print(f"[DEBUG] Starting server on {host}:{port}...")
    try:
        config = uvicorn.Config(app, host=host, port=port, log_level="info")
        server = uvicorn.Server(config)
        await server.serve()
        print("[DEBUG] Server started and running.")
    except Exception as e:
        print(f"[ERROR] Failed to start server: {e}")
        raise

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Reddit Scout agent server stopped by user.")
    except Exception as e:
        print(f"Error during server startup: {e}") 