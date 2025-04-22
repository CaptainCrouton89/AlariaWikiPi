# Plan for Implementing a Streaming Chat Page with OpenAI Agents SDK

## 1. Project Overview

- The AlariaWikiPi is a Flask-based wiki application that allows users to create, edit, and search markdown notes.
- We need to implement a chat page where users can interact with an AI agent that has tools for searching and creating notes.

## 2. Environment Setup

1. Install the required OpenAI Agents SDK:
   ```bash
   pip install openai-agents
   ```
2. Update the requirements.txt file to include the new dependency.

## 3. Backend Implementation

### 3.1 Create Agent Tool Functions

1. Create a new file `agent_tools.py` with the following tools:
   - `search_notes_tool`: Searches existing notes using the existing search functionality
   - `create_note_tool`: Creates a new note with a title and content

### 3.2 Set Up the Agent Configuration

1. Create a new file `agent_setup.py` that:
   - Configures the OpenAI Agent with the custom tools
   - Sets up the authentication and API keys
   - Defines prompt templates and agent behavior

### 3.3 Implement API Endpoints

1. Add new routes in `wiki.py`:
   - `/chat`: Renders the chat page
   - `/api/chat`: Endpoint for starting a new chat session
   - `/api/chat/stream`: WebSocket endpoint for streaming agent responses

## 4. Frontend Implementation

### 4.1 Create Chat Templates

1. Create a new template `chat.html` that extends the base template and includes:
   - Chat message display area
   - Input field for user messages
   - Send button
   - Loading indicator for streaming responses

### 4.2 Implement JavaScript Functionality

1. Create `static/js/chat.js` to:
   - Handle WebSocket connections for streaming responses
   - Manage the chat UI
   - Display typing indicators during streaming
   - Format and render tool usage in the chat interface

### 4.3 Style the Chat Interface

1. Add CSS styles in `static/css/chat.css` for:
   - Chat container
   - Message bubbles (user vs. agent)
   - Typing indicator
   - Tool usage displays

## 5. Integration with Existing Functionality

### 5.1 Nav Bar Integration

1. Add a "Chat" link to the navigation bar in `base.html`

### 5.2 Connect with Wiki Functions

1. Ensure the agent tools properly integrate with existing wiki functionality:
   - The search tool should use the existing search functionality
   - The create note tool should use the existing note creation functionality

## 6. Security & Error Handling

1. Implement proper error handling for API requests
2. Set up rate limiting to prevent abuse
3. Ensure security for user sessions

## 7. Testing

1. Test agent interactions with specific focus on:
   - Search functionality
   - Note creation
   - Response streaming
   - Error handling
   - UI responsiveness

## 8. Documentation

1. Add user documentation on how to use the chat feature
2. Document the agent's capabilities and limitations

## 9. Implementation Approach

1. Start with the backend implementation of agent tools
2. Create the basic chat UI
3. Implement the streaming functionality
4. Connect backend with frontend
5. Test and refine the implementation
6. Add styling and final touches

## 10. Future Enhancements

- Tool for editing existing notes
- Agent memory for conversation context
- Rich formatting options in created notes
- Additional analytics for chat usage
