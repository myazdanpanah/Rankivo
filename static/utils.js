/**
 * Rankivo Shared Utilities
 * Functions used across chat.js and index.html
 */

function escH(s) {
  const d = document.createElement('div');
  d.textContent = s;
  return d.innerHTML;
}

function renderMarkdown(text) {
  if (!text) return '';
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
  
  // Links (XSS-safe: only allow http/https)
  html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, function(m, text, url) {
    if (url.match(/^https?:\/\//i)) {
      return '<a href="' + url + '" target="_blank" class="chat-link">' + text + '</a>';
    }
    return '[' + text + '](' + url + ')';
  });
  
  // Line breaks
  html = html.replace(/\n/g, '<br>');
  
  return html;
}

function getSelectedProvider() {
  const el = document.getElementById('chatProvider');
  return el ? el.value : 'ollama';
}

function getSelectedModel() {
  const el = document.getElementById('chatModel');
  return el ? el.value : '';
}
