import asyncio
import logging
import os

from agents.run import Runner

from agent_setup import create_agent, process_user_message

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_agent():
    # Make sure we have an API key
    if not os.environ.get("OPENAI_API_KEY"):
        print("Please set the OPENAI_API_KEY environment variable")
        return
    
    # Create the agent
    agent = create_agent()
    
    # Test a simple message
    print("\nTesting agent with a simple message...")
    message = "Hello! Can you help me search for notes about Python?"
    
    print(f"\nUser: {message}")
    print("Assistant: ", end="")
    
    # Process the message and collect the response
    response_text = ""
    async for chunk in process_user_message(agent, message):
        if chunk.get("type") == "content" and chunk.get("content"):
            content = chunk.get("content")
            print(content, end="", flush=True)
            response_text += content
    
    print("\n\nTest completed!")
    
if __name__ == "__main__":
    asyncio.run(test_agent()) 