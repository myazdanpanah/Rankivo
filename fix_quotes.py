"""Fix JS quote nesting issues in index.html."""
import sys, re, subprocess
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open('static/index.html', 'r', encoding='utf-8') as f:
    c = f.read()

fixes = 0

# The broken text literally in the file is (as raw bytes):
# onclick="deleteUser('"+u.username+"')"
# We need to change the single quotes to &quot;

# Build the search/replace strings carefully
search_chars = list("onclick=\"deleteUser('\"+u.username+\"')\"")
search = ''.join(search_chars)
replace_chars = list('onclick="deleteUser(&quot;"+u.username+"&quot;)"')
replace = ''.join(replace_chars)

if search in c:
    c = c.replace(search, replace)
    fixes += 1
    print("Fixed deleteUser onclick quotes")
else:
    print("Pattern not found, trying line-by-line...")
    lines = c.split('\n')
    for i, line in enumerate(lines):
        if 'deleteUser' in line and 'onclick' in line:
            print(f"  Line {i+1}: {line.strip()[:200]}")

with open('static/index.html', 'w', encoding='utf-8') as f:
    f.write(c)

print(f"Applied {fixes} fixes")

# Verify with Node.js
m = re.findall(r'<script>(.*?)</script>', c, re.DOTALL)
if m:
    js = m[1] if len(m) > 1 else m[0]
    with open('script_check.js', 'w', encoding='utf-8') as f:
        f.write(js)
    result = subprocess.run(['node', '--check', 'script_check.js'], capture_output=True, text=True)
    if result.returncode == 0:
        print("JS syntax check: PASSED")
    else:
        print(f"JS syntax check: FAILED\n{result.stderr[:500]}")
