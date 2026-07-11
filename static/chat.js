/**
 * Rankivo AI Chat — Real-time streaming chat with SEO context
 */

let chatMessages = [];
let chatStreaming = false;

function initChat() {
  // Initialize session ID if not set
  if (!localStorage.getItem('session_id')) {
    localStorage.setItem('session_id', 'sess_' + Date.now() + '_' + Math.random().toString(36).slice(2, 8));
  }
  const input = document.getElementById('chatInput');
  const sendBtn = document.getElementById('chatSendBtn');
  const clearBtn = document.getElementById('chatClearBtn');
  
  if (input) {
    input.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendChatMessage();
      }
    });
    input.focus();
  }
  
  if (sendBtn) sendBtn.addEventListener('click', sendChatMessage);
  if (clearBtn) clearBtn.addEventListener('click', clearChat);
  
  // Load existing history
  loadChatHistory();
  
  // Show welcome message
  if (chatMessages.length === 0) {
    addSystemMessage('Welcome to Rankivo AI! I\'m your SEO assistant. Ask me anything about SEO, keyword research, content optimization, or technical SEO. I have access to your current audit data and keyword research from your session.');
  }
}

function escH(s) {
  const d = document.createElement('div');
  d.textContent = s;
  return d.innerHTML;
}

function renderMarkdown(text) {
  // Simple markdown to HTML conversion
  let html = escH(text);
  
  // Code blocks
  html = html.replace(/```(\w*)\n([\s\S]*?)```/g, '<pre class="chat-code"><code>$2</code></pre>');
  
  // Inline code
  html = html.replace(/`([^`]+)`/g, '<code class="chat-inline-code">$1</code>');
  
  // Bold
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
  
  // Italic
  html = html.replace(/\*(.+?)\*/g, '<em>$1</em>');
  
  // Headers
  html = html.replace(/^### (.+)$/gm, '<h4 class="chat-h">$1</h4>');
  html = html.replace(/^## (.+)$/gm, '<h3 class="chat-h">$1</h3>');
  html = html.replace(/^# (.+)$/gm, '<h2 class="chat-h">$1</h2>');
  
  // Unordered lists
  html = html.replace(/^- (.+)$/gm, '<li>$1</li>');
  html = html.replace(/(<li>.*<\/li>\n?)+/g, '<ul class="chat-list">$&</ul>');
  
  // Ordered lists
  html = html.replace(/^\d+\. (.+)$/gm, '<li>$1</li>');
  
  // Links
  html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" class="chat-link">$1</a>');
  
  // Line breaks
  html = html.replace(/\n/g, '<br>');
  
  return html;
}

function addMessage(role, content) {
  chatMessages.push({ role, content, timestamp: Date.now() });
  renderChatMessages();
}

function addSystemMessage(content) {
  addMessage('system', content);
}

function addAssistantMessage(content) {
  addMessage('assistant', content);
}

function addUserMessage(content) {
  addMessage('user', content);
}

function renderChatMessages() {
  const container = document.getElementById('chatMessages');
  if (!container) return;
  
  container.innerHTML = chatMessages.map(msg => {
    const cls = msg.role === 'user' ? 'chat-msg-user' : 
                msg.role === 'assistant' ? 'chat-msg-assistant' : 'chat-msg-system';
    const icon = msg.role === 'user' ? 'fa-user' : 
                 msg.role === 'assistant' ? 'fa-robot' : 'fa-info-circle';
    const label = msg.role === 'user' ? 'You' : 
                  msg.role === 'assistant' ? 'Rankivo AI' : 'System';
    
    return `<div class="chat-msg ${cls}">
      <div class="chat-msg-header">
        <i class="fas ${icon}"></i>
        <span class="chat-msg-label">${label}</span>
      </div>
      <div class="chat-msg-content">${renderMarkdown(msg.content)}</div>
    </div>`;
  }).join('');
  
  container.scrollTop = container.scrollHeight;
}

async function sendChatMessage() {
  if (chatStreaming) return;
  
  const input = document.getElementById('chatInput');
  const sendBtn = document.getElementById('chatSendBtn');
  if (!input || !sendBtn) return;
  
  const message = input.value.trim();
  if (!message) return;
  
  input.value = '';
  sendBtn.disabled = true;
  chatStreaming = true;
  
  addUserMessage(message);
  
  // Add placeholder for streaming response
  chatMessages.push({ role: 'assistant', content: '', timestamp: Date.now(), streaming: true });
  renderChatMessages();
  
  try {
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + (localStorage.getItem('token') || ''),
        'X-Session-ID': localStorage.getItem('session_id') || 'default',
      },
      body: JSON.stringify({ message, provider: getSelectedProvider() }),
    });
    
    if (!response.ok) {
      throw new Error('Chat request failed');
    }
    
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';
    
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      
      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';
      
      for (const line of lines) {
        if (!line.trim()) continue;
        try {
          const event = JSON.parse(line);
          
          if (event.type === 'chunk') {
            const lastMsg = chatMessages[chatMessages.length - 1];
            if (lastMsg && lastMsg.streaming) {
              lastMsg.content += event.content;
              renderChatMessages();
            }
          } else if (event.type === 'done') {
            const lastMsg = chatMessages[chatMessages.length - 1];
            if (lastMsg) {
              lastMsg.streaming = false;
            }
          } else if (event.type === 'error') {
            const lastMsg = chatMessages[chatMessages.length - 1];
            if (lastMsg && lastMsg.streaming) {
              lastMsg.content = 'Error: ' + event.message;
              lastMsg.streaming = false;
            }
          }
        } catch (e) {
          // Ignore parse errors
        }
      }
    }
  } catch (err) {
    const lastMsg = chatMessages[chatMessages.length - 1];
    if (lastMsg && lastMsg.streaming) {
      lastMsg.content = 'Error: ' + err.message;
      lastMsg.streaming = false;
    }
    renderChatMessages();
  } finally {
    chatStreaming = false;
    sendBtn.disabled = false;
    input.focus();
  }
}

async function clearChat() {
  try {
    await fetch('/api/chat/clear', {
      method: 'POST',
      headers: {
        'Authorization': 'Bearer ' + (localStorage.getItem('token') || ''),
        'X-Session-ID': localStorage.getItem('session_id') || 'default',
      },
    });
  } catch (e) {}
  
  chatMessages = [];
  renderChatMessages();
  addSystemMessage('Chat cleared. How can I help you with SEO?');
}

async function loadChatHistory() {
  try {
    const resp = await fetch('/api/chat/history', {
      headers: {
        'Authorization': 'Bearer ' + (localStorage.getItem('token') || ''),
        'X-Session-ID': localStorage.getItem('session_id') || 'default',
      },
    });
    if (resp.ok) {
      const data = await resp.json();
      if (data.history && data.history.length > 0) {
        chatMessages = data.history.map(m => ({ ...m, streaming: false }));
        renderChatMessages();
      }
    }
  } catch (e) {}
}

function getSelectedProvider() {
  const el = document.getElementById('chatProvider');
  return el ? el.value : 'ollama';
}

// Quick prompts for SEO
const chatQuickPrompts = [
  { label: 'Audit my site', prompt: 'Based on my current audit data, what are the top 3 things I should fix first?' },
  { label: 'Keyword strategy', prompt: 'Analyze my current keyword research and suggest a content strategy.' },
  { label: 'Technical SEO', prompt: 'What technical SEO issues should I prioritize for my website?' },
  { label: 'Content plan', prompt: 'Create a content calendar plan based on my keyword research.' },
  { label: 'Competitor tips', prompt: 'How can I outrank my competitors for my target keywords?' },
];

function setChatPrompt(prompt) {
  const input = document.getElementById('chatInput');
  if (input) {
    input.value = prompt;
    input.focus();
  }
}
