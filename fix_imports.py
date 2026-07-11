"""Fix script for api.py imports and index.html initChat"""
import os

os.chdir('C:/Rankivo')

# Fix 1: api.py - add build_article_prompt to imports and remove redundant import
with open('api.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
seen_import = False
for i, line in enumerate(lines):
    # Fix the content_generator import to include build_article_prompt
    if 'from content_generator import' in line and 'build_article_prompt' not in line:
        line = line.replace(
            'get_available_providers',
            'get_available_providers, build_article_prompt'
        )
        seen_import = True
        print(f'Fixed import on line {i+1}')
    
    # Remove standalone "import content_generator" (redundant)
    if line.strip() == 'import content_generator':
        print(f'Removed redundant import on line {i+1}')
        continue
    
    new_lines.append(line)

with open('api.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
print('api.py fixed')

# Fix 2: index.html - add initChat to navigate function
with open('static/index.html', 'r', encoding='utf-8') as f:
    c = f.read()

if 'initChat' not in c:
    nav_idx = c.find('function navigate(')
    if nav_idx > 0:
        sp = c.find('showPage(page)', nav_idx)
        if sp > 0:
            insert_after = sp + len('showPage(page)')
            init_line = "\n    if (page === 'ai-chat') initChat();"
            c = c[:insert_after] + init_line + c[insert_after:]
            print('Added initChat to navigate')
        else:
            print('WARN: showPage not found')
    else:
        print('WARN: navigate not found')
else:
    print('initChat already present')

with open('static/index.html', 'w', encoding='utf-8') as f:
    f.write(c)
print('index.html fixed')

# Fix 3: chat.js - add session_id initialization
with open('static/chat.js', 'r', encoding='utf-8') as f:
    c = f.read()

if 'localStorage.getItem' not in c or "'sess_' + Date.now()" not in c:
    old_init = 'function initChat() {'
    new_init = """function initChat() {
  // Initialize session ID if not set
  if (!localStorage.getItem('session_id')) {
    localStorage.setItem('session_id', 'sess_' + Date.now() + '_' + Math.random().toString(36).slice(2, 8));
  }"""
    c = c.replace(old_init, new_init, 1)
    print('Added session_id initialization')

with open('static/chat.js', 'w', encoding='utf-8') as f:
    f.write(c)
print('chat.js fixed')
print('All fixes applied!')
