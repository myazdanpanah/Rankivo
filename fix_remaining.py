"""Fix remaining issues identified by code reviewer"""
import os

os.chdir('C:/Rankivo')

# Fix 1: api.py - verify build_article_prompt is properly imported
with open('api.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

changes = []
new_lines = []
for i, line in enumerate(lines):
    # Fix content_generator import to include build_article_prompt
    if 'from content_generator import' in line:
        if 'build_article_prompt' not in line:
            line = line.replace(
                'get_available_providers)',
                'get_available_providers, build_article_prompt)'
            )
            changes.append(f'Added build_article_prompt to import (line {i+1})')
    
    # Remove standalone "import content_generator"
    if line.strip() == 'import content_generator':
        changes.append(f'Removed redundant import (line {i+1})')
        continue
    
    new_lines.append(line)

with open('api.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

# Fix 2: Add chat history cleanup (bounded memory)
with open('api.py', 'r', encoding='utf-8') as f:
    content = f.read()

cleanup_code = '''
# Periodic chat history cleanup
_chat_last_cleanup = time.time()
_CHAT_CLEANUP_INTERVAL = 300  # 5 minutes
_CHAT_MAX_MESSAGES = 200  # max messages per session

def _cleanup_chat_history():
    global _chat_last_cleanup
    now = time.time()
    if now - _chat_last_cleanup < _CHAT_CLEANUP_INTERVAL:
        return
    _chat_last_cleanup = now
    stale_sessions = []
    for sid, msgs in _chat_history.items():
        if msgs and now - msgs[-1].get('timestamp', 0) > 3600:
            stale_sessions.append(sid)
        elif len(msgs) > _CHAT_MAX_MESSAGES:
            _chat_history[sid] = msgs[-_CHAT_MAX_MESSAGES:]
    for sid in stale_sessions:
        _chat_history.pop(sid, None)
'''

if '_cleanup_chat_history' not in content:
    # Add cleanup function and call it
    content = content.replace(
        'CHAT_MAX_HISTORY = 50',
        'CHAT_MAX_HISTORY = 50' + cleanup_code
    )
    # Call cleanup at start of chat endpoint
    content = content.replace(
        'if not message:\n        return jsonify({\"error\": \"Message is required\"}), 400',
        'if not message:\n        return jsonify({\"error\": \"Message is required\"}), 400\n\n    _cleanup_chat_history()'
    )
    changes.append('Added chat history cleanup')

with open('api.py', 'w', encoding='utf-8') as f:
    f.write(content)

for c in changes:
    print(c)
print(f'Total changes: {len(changes)}')
