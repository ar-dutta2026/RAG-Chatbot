// ================================
// State & DOM References
// ================================

// Conversation history stored as an array of message objects
let history = [];

// DOM elements for UI interaction
const chatWindow = document.getElementById('chat-window');
const queryInput = document.getElementById('query');
const sendBtn = document.getElementById('send-btn');

// ================================
// Input State Handling
// ================================

// Toggle Send button on input change
function toggleSendButton() {
  sendBtn.disabled = queryInput.value.trim().length === 0;
}
queryInput.addEventListener('input', toggleSendButton);

// ================================
// Assistant Typing Effect
// ================================

/**
 * Simulates a typewriter effect for assistant messages.
 * @param {HTMLElement} el - The message container element
 * @param {string} text - The message content to type
 * @param {function} [callback] - Optional callback after typing completes
 */
function typeWriter(el, text, callback) {
  let i = 0;
  const cursor = document.createElement('span');
  cursor.className = 'typing-cursor';
  el.appendChild(cursor);

  function type() {
    if (i < text.length) {
      cursor.insertAdjacentText('beforebegin', text.charAt(i));
      i++;
      chatWindow.scrollTop = chatWindow.scrollHeight;
      setTimeout(type, 30);
    } else {
      cursor.remove();
      if (callback) callback();
    }
  }

  type();
}

// ================================
// Message Handling
// ================================

/**
 * Adds a user or assistant message to the chat window.
 * @param {'user' | 'assistant'} role - The role of the sender
 * @param {string} text - The message content
 */
function addMessage(role, text) {
  history.push({ role, content: text });
  const el = document.createElement('div');
  el.className = `message ${role}`;
  chatWindow.appendChild(el);
  el.style.animationDelay = '0s';

  if (role === 'assistant') {
    typeWriter(el, text);
  } else {
    el.textContent = text;
    el.style.opacity = '1';
  }
}

// ================================
// Message Submission
// ================================

/**
 * Sends the user's message to the backend and handles the assistant's response.
 */
async function send() {
  const query = queryInput.value.trim();
  if (!query) return;

  // Disable send button and show loading state
  sendBtn.disabled = true;
  sendBtn.textContent = 'Sending…';

  // Add user message
  addMessage('user', query);
  queryInput.value = '';
  toggleSendButton();

  try {
    // Send message to backend API
    const res = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ history, query })
    });

    // Parse response and display assistant message
    const json = await res.json();
    addMessage('assistant', json.response);
  } catch (err) {
    // Handle network or server errors
    addMessage('assistant', 'Error: ' + err.message);
  } finally {
    // Re-enable send button
    sendBtn.textContent = 'Send';
    toggleSendButton();
  }
}

// ================================
// Event Listeners
// ================================

// Send message on button click
sendBtn.addEventListener('click', send);

// Send message on Enter key
queryInput.addEventListener('keyup', e => {
  if (e.key === 'Enter') send();
});

// ================================
// Initial State
// ================================

// Add greeting from assistant on page load
window.addEventListener('load', () => {
  const greeting = 'Hello! How can I assist you today?';
  addMessage('assistant', greeting);
});
