// Chat UI JavaScript

document.addEventListener("DOMContentLoaded", function () {
  const chatForm = document.getElementById("chat-form");
  const chatInput = document.getElementById("chat-input");
  const chatMessages = document.getElementById("chat-messages");
  const typingIndicator = document.getElementById("typing-indicator");

  let chatHistory = [];
  let isProcessing = false;

  // Initialize chat
  initChat();

  // Handle form submission
  chatForm.addEventListener("submit", async function (e) {
    e.preventDefault();
    const message = chatInput.value.trim();

    if (message && !isProcessing) {
      sendMessage(message);
    }
  });

  // Make chat input expand as user types
  chatInput.addEventListener("input", function () {
    this.style.height = "auto";
    this.style.height = this.scrollHeight + "px";
  });

  // Initialize the chat
  function initChat() {
    scrollToBottom();

    // Focus the input field
    setTimeout(() => {
      chatInput.focus();
    }, 500);
  }

  // Send a message to the API
  async function sendMessage(message) {
    // Add user message to UI
    appendMessage("user", message);

    // Clear input and reset height
    chatInput.value = "";
    chatInput.style.height = "auto";

    // Scroll to bottom
    scrollToBottom();

    // Show typing indicator
    isProcessing = true;
    typingIndicator.classList.add("active");

    try {
      // Send request to chat API
      const response = await fetch("/api/chat/stream", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ message }),
      });

      // Handle streaming response
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let assistantMessage = "";
      let messageElement = null;

      while (true) {
        const { done, value } = await reader.read();

        if (done) {
          break;
        }

        // Decode the chunk
        const chunk = decoder.decode(value);

        try {
          // Parse the chunk as JSON
          const parsed = JSON.parse(chunk);

          if (parsed.type === "content") {
            // This is a content update
            if (!messageElement) {
              // First time, create the message container
              messageElement = createMessageElement("assistant", "");
              chatMessages.appendChild(messageElement);
            }

            // Update message content
            assistantMessage += parsed.content || "";
            updateMessageContent(messageElement, assistantMessage);
            scrollToBottom();
          } else if (parsed.type === "tool_call") {
            // This is a tool call
            handleToolCall(parsed.data);
          } else if (parsed.type === "tool_result") {
            // This is a tool result
            handleToolResult(parsed.data);
          }
        } catch (e) {
          console.error("Error parsing chunk:", e);
        }
      }

      // Ensure the final message is rendered correctly
      if (messageElement) {
        updateMessageContent(messageElement, assistantMessage);
      }
    } catch (error) {
      console.error("Error sending message:", error);
      appendMessage(
        "system",
        "Sorry, there was an error processing your request. Please try again."
      );
    } finally {
      // Hide typing indicator
      typingIndicator.classList.remove("active");
      isProcessing = false;

      // Focus the input field again
      chatInput.focus();

      // Scroll to bottom
      scrollToBottom();
    }
  }

  // Append a message to the chat
  function appendMessage(role, content) {
    const messageElement = createMessageElement(role, content);
    chatMessages.appendChild(messageElement);
    scrollToBottom();
  }

  // Create a new message element
  function createMessageElement(role, content) {
    const messageDiv = document.createElement("div");
    messageDiv.classList.add("message", role);

    const contentDiv = document.createElement("div");
    contentDiv.classList.add("message-content");

    messageDiv.appendChild(contentDiv);

    updateMessageContent(messageDiv, content);

    return messageDiv;
  }

  // Update message content with markdown rendering
  function updateMessageContent(messageElement, content) {
    const contentDiv = messageElement.querySelector(".message-content");
    contentDiv.innerHTML = marked.parse(content);

    // Make all links open in a new tab
    const links = contentDiv.querySelectorAll("a");
    links.forEach((link) => {
      link.setAttribute("target", "_blank");
      link.setAttribute("rel", "noopener noreferrer");
    });
  }

  // Handle a tool call
  function handleToolCall(toolCallData) {
    const toolCall = document.createElement("div");
    toolCall.classList.add("tool-call");

    let toolCallContent = `Using tool: <strong>${toolCallData.name}</strong>`;
    if (toolCallData.args) {
      toolCallContent += `<br>Arguments: <code>${JSON.stringify(
        toolCallData.args
      )}</code>`;
    }

    toolCall.innerHTML = toolCallContent;
    chatMessages.appendChild(toolCall);
    scrollToBottom();
  }

  // Handle a tool result
  function handleToolResult(resultData) {
    const toolResult = document.createElement("div");
    toolResult.classList.add("tool-result");

    // Format the result based on the tool type
    if (
      resultData.name === "search_notes" &&
      Array.isArray(resultData.result)
    ) {
      // Format search results as links
      if (resultData.result.length === 0) {
        toolResult.innerHTML = "No results found";
      } else {
        toolResult.innerHTML = `<strong>Found ${resultData.result.length} results:</strong>`;

        const resultList = document.createElement("div");
        resultList.classList.add("result-list");

        resultData.result.forEach((item) => {
          const resultLink = document.createElement("a");
          resultLink.classList.add("result-link");
          resultLink.href = item.url;
          resultLink.textContent = item.doc;
          resultList.appendChild(resultLink);
        });

        toolResult.appendChild(resultList);
      }
    } else if (resultData.name === "create_note" && resultData.result.success) {
      // Format note creation result
      const noteLink = document.createElement("a");
      noteLink.href = resultData.result.url;
      noteLink.textContent = resultData.result.title;
      noteLink.classList.add("result-link");

      toolResult.innerHTML = `<strong>Created note:</strong> `;
      toolResult.appendChild(noteLink);
    } else {
      // Generic result formatting
      toolResult.innerHTML = `<pre>${JSON.stringify(
        resultData.result,
        null,
        2
      )}</pre>`;
    }

    chatMessages.appendChild(toolResult);
    scrollToBottom();
  }

  // Scroll chat to bottom
  function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }
});
