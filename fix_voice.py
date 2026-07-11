"""Add voice input to chat.js and index.html"""
import os
os.chdir('C:/Rankivo')

# Fix 3: Add voice input to chat.js
with open('static/chat.js', 'r', encoding='utf-8') as f:
    c = f.read()

voice_fn = """

// Voice Input (Web Speech API)
let voiceRecognition = null;
let voiceListening = false;

function toggleVoiceInput() {
  const btn = document.getElementById('voiceBtn');
  if (!btn) return;
  
  if (voiceListening) {
    if (voiceRecognition) voiceRecognition.stop();
    voiceListening = false;
    btn.innerHTML = '<i class="fas fa-microphone"></i>';
    btn.classList.remove('btn-danger');
    btn.classList.add('btn-secondary');
    return;
  }
  
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    if (typeof showToast === 'function') showToast('Speech recognition not supported in this browser', 'warning');
    return;
  }
  
  voiceRecognition = new SpeechRecognition();
  voiceRecognition.continuous = false;
  voiceRecognition.interimResults = true;
  voiceRecognition.lang = navigator.language || 'en-US';
  
  voiceRecognition.onstart = function() {
    voiceListening = true;
    btn.innerHTML = '<i class="fas fa-microphone-slash"></i>';
    btn.classList.remove('btn-secondary');
    btn.classList.add('btn-danger');
  };
  
  voiceRecognition.onresult = function(event) {
    const input = document.getElementById('chatInput');
    if (!input) return;
    let transcript = '';
    for (let i = event.resultIndex; i < event.results.length; i++) {
      transcript += event.results[i][0].transcript;
    }
    input.value = transcript;
  };
  
  voiceRecognition.onend = function() {
    voiceListening = false;
    btn.innerHTML = '<i class="fas fa-microphone"></i>';
    btn.classList.remove('btn-danger');
    btn.classList.add('btn-secondary');
  };
  
  voiceRecognition.onerror = function(event) {
    voiceListening = false;
    btn.innerHTML = '<i class="fas fa-microphone"></i>';
    btn.classList.remove('btn-danger');
    btn.classList.add('btn-secondary');
    if (event.error !== 'no-speech' && typeof showToast === 'function') {
      showToast('Voice input error: ' + event.error, 'warning');
    }
  };
  
  voiceRecognition.start();
}
"""

if 'toggleVoiceInput' not in c:
    c = c.rstrip() + voice_fn
    print('Added voice input to chat.js')

with open('static/chat.js', 'w', encoding='utf-8') as f:
    f.write(c)

# Add voice button to index.html chat input area
with open('static/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

old_area = "<textarea id='chatInput'"
new_area = """<button class='btn btn-secondary' onclick='toggleVoiceInput()' id='voiceBtn' title='Voice input' style='height:48px;min-width:48px;'>
              <i class='fas fa-microphone'></i>
            </button>
            <textarea id='chatInput'"""

if "id='voiceBtn'" not in html and old_area in html:
    html = html.replace(old_area, new_area, 1)
    print('Added voice button to index.html')

with open('static/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('All voice input fixes done')
