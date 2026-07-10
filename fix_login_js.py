"""Fix JavaScript syntax errors in static/index.html caused by unescaped quotes."""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open('static/index.html', 'r', encoding='utf-8') as f:
    c = f.read()

changes = 0

# Fix 1: removeIntentWord onclick has unescaped single quotes inside a single-quoted JS string
# Original: onclick="removeIntentWord(this.getAttribute('data-word'),this.getAttribute('data-intent'))"
# The single quotes in getAttribute('data-word') break the outer single-quoted JS string
old1 = "onclick=\"removeIntentWord(this.getAttribute('data-word'),this.getAttribute('data-intent'))\""
new1 = 'onclick="removeIntentWord(this.getAttribute(&quot;data-word&quot;),this.getAttribute(&quot;data-intent&quot;))"'
if old1 in c:
    c = c.replace(old1, new1, 1)
    changes += 1
    print("Fixed: removeIntentWord onclick quotes")

# Fix 2: Check for any other getAttribute('...') inside onclick handlers within JS strings
import re
# Find all onclick="..." patterns inside JS strings that contain getAttribute('...')
pattern = r"onclick=\\\"(\w+)\(this\.getAttribute\('([^']+)'\)(?:,this\.getAttribute\('([^']+)'\))?\)\\\""
for match in re.finditer(pattern, c):
    full = match.group(0)
    fixed = full.replace("getAttribute('", 'getAttribute(&quot;').replace("')", '&quot;)')
    if full != fixed:
        c = c.replace(full, fixed, 1)
        changes += 1
        print(f"Fixed: {match.group(1)} onclick quotes")

# Fix 3: Check for any remaining unescaped single quotes in JS strings inside HTML attributes
# Look for patterns like: '... onclick="...something with 'quotes'..."'
# These would be inside inject_new_modules.py generated code

if changes > 0:
    with open('static/index.html', 'w', encoding='utf-8') as f:
        f.write(c)
    print(f"\nTotal fixes: {changes}")
else:
    print("No matching patterns found - checking line 5532 directly...")
    lines = c.split('\n')
    if len(lines) >= 5532:
        line = lines[5531]
        print(f"Line 5532: {line[:300]}")
        # Try a more aggressive fix: find any getAttribute(' in JS context and escape
        if "getAttribute('" in line:
            line = line.replace("getAttribute('", 'getAttribute(&quot;').replace("')", '&quot;)')
            lines[5531] = line
            c = '\n'.join(lines)
            with open('static/index.html', 'w', encoding='utf-8') as f:
                f.write(c)
            print("Fixed line 5532 via direct replacement")
            changes += 1
    if changes == 0:
        print("WARNING: Could not find or fix the syntax error")
