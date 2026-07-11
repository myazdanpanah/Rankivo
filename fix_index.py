"""Fix index.html: add utils.js, model selector, and update streaming"""
import os
os.chdir('C:/Rankivo')

with open('static/index.html', 'r', encoding='utf-8') as f:
    c = f.read()

changes = []

# 1. Add utils.js script before chat.js
if 'utils.js' not in c:
    marker = '<script src="chat.js"></script>'
    idx = c.find(marker)
    if idx > 0:
        c = c[:idx] + '<script src="utils.js"></script>\n' + c[idx:]
        changes.append('Added utils.js before chat.js')

# 2. Add model selector after provider select in AI Chat page
# Find the chatProvider select and add chatModel after it
if 'chatModel' not in c:
    # Find the closing </select> after chatProvider options
    provider_idx = c.find("id='chatProvider'")
    if provider_idx < 0:
        provider_idx = c.find('id="chatProvider"')
    if provider_idx > 0:
        # Find the </select> after this
        close_select = c.find('</select>', provider_idx)
        if close_select > 0:
            close_select += len('</select>')
            model_html = """
            <select id='chatModel' class='input' style='width:auto;font-size:0.8rem;'>
              <option value=''>Default Model</option>
              <option value='gemma4:latest'>Gemma 4</option>
              <option value='llama3'>Llama 3</option>
              <option value='qwen2.5'>Qwen 2.5</option>
            </select>"""
            c = c[:close_select] + model_html + c[close_select:]
            changes.append('Added model selector')

# 3. Update generateArticleStream to use getSelectedModel
if 'getSelectedModel' not in c:
    old_body = 'body: JSON.stringify({ topic, keywords: keywords.length ? keywords : [topic], provider, word_count: wordCount, tone, style, language })'
    new_body = "body: JSON.stringify({ topic, keywords: keywords.length ? keywords : [topic], provider, word_count: wordCount, tone, style, language, model: typeof getSelectedModel === 'function' ? getSelectedModel() : '' })"
    if old_body in c:
        c = c.replace(old_body, new_body, 1)
        changes.append('Added model to streaming request')

with open('static/index.html', 'w', encoding='utf-8') as f:
    f.write(c)

for ch in changes:
    print(ch)
print(f'Total: {len(changes)} changes')
