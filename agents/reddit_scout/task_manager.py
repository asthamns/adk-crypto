class TaskManager:
    def __init__(self, agent):
        self.agent = agent

    async def process_task(self, message, context=None, session_id=None):
        # If your agent has an async method to process messages, use await
        if hasattr(self.agent, 'process_task') and callable(getattr(self.agent, 'process_task')):
            if hasattr(self.agent.process_task, '__call__') and hasattr(self.agent.process_task, '__code__') and self.agent.process_task.__code__.co_flags & 0x80:
                # async def
                return await self.agent.process_task(message, context, session_id)
            else:
                # sync def
                return self.agent.process_task(message, context, session_id)
        # Otherwise, just return a default response
        return {"message": f"Agent received: {message}", "data": {}, "status": "success"} 