import logging
import os
from typing import Any, AsyncGenerator, Dict, List, Optional

from agent_tools import create_note, search_notes
from agents import Agent
from agents.run import Runner
from openai import OpenAI

logger = logging.getLogger(__name__)

def get_api_key() -> str:
    """
    Get the OpenAI API key from environment variables
    
    Returns:
        OpenAI API key as string
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        logger.warning("OPENAI_API_KEY not found in environment variables. Agent functionality may be limited.")
    return api_key

def create_agent(api_key: Optional[str] = None) -> Agent:
    """
    Create an OpenAI Agent configured with custom tools
    
    This uses the agents package which is the official SDK for OpenAI Assistants API
    
    Args:
        api_key: OpenAI API key (optional, will use environment variable if not provided)
        
    Returns:
        Configured Agent instance
    """
    if not api_key:
        api_key = get_api_key()
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key
    
    # Configure the agent with our custom tools
    agent = Agent(
        name="AlariaWikiAssistant",
        instructions="""You are an AI assistant for Alaria Wiki, a markdown-based wiki system.
        You can help users search for notes and create new notes.
        When searching, provide helpful summaries of what you found.
        When creating notes, use proper markdown formatting.
        Respond conversationally and be helpful.
        """,
        tools=[search_notes, create_note],
        model="gpt-4-turbo",
    )
    return agent

async def process_user_message(
    agent: Agent, 
    message: str, 
    chat_history: List[Dict[str, Any]] = None
) -> AsyncGenerator[Dict[str, Any], None]:
    """
    Process a user message and stream the agent's response
    
    Uses the Runner from the agents SDK to run the agent in streaming mode
    
    Args:
        agent: The Agent instance
        message: The user's message
        chat_history: Optional chat history for context
        
    Yields:
        Chunks of the agent's response for streaming (type: "content", content: string)
    """
    if not chat_history:
        chat_history = []
    
    # Add user message to history
    chat_history.append({"role": "user", "content": message})
    
    # Create a streaming result
    result = Runner.run_streamed(agent, message)
    
    # Stream the response
    response_text = ""
    async for event in result.stream_events():
        if hasattr(event, 'name') and event.name == "message_output_created":
            for content_part in event.item.raw_item.content:
                if content_part.type == "output_text":
                    yield {"type": "content", "content": content_part.text}
                    response_text += content_part.text
    
    # Add assistant response to history
    if response_text:
        chat_history.append({"role": "assistant", "content": response_text})
    elif result.final_output:
        chat_history.append({"role": "assistant", "content": result.final_output})
    
    # In an async generator, we don't return a value at the end
    # The chat_history is modified in place 