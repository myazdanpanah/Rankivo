"""Find and fix JS syntax errors in index.html that prevent doLogin from being defined."""
import sys, re
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open('static/index.html', 'r', encoding='utf-8') as f:
    c = f.read()

# Find doLogin definition
dologin_idx = c.find('async function doLogin')
if dologin_idx < 0:
    print("ERROR: doLogin not found!")
    sys.exit(1)
dologin_line = c[:dologin_idx].count('\n') + 1
print(f"doLogin defined at line {dologin_line}")

# Extract all JS between <script> tags
script_pattern = re.compile(r'<script>(.*?)</script>', re.DOTALL)
scripts = script_pattern.findall(c)
print(f"Found {len(scripts)} script blocks")

# Check each script block for syntax issues
for i, script in enumerate(scripts):
    lines = script.split('\n')
    print(f"\nScript block {i}: {len(lines)} lines")
    
    # Check brace balance
    opens = script.count('{')
    closes = script.count('}')
    if opens != closes:
        print(f"  BRACE MISMATCH: {{ = {opens}, }} = {closes} (diff = {opens - closes})")
    
    # Check for unescaped single quotes in HTML attribute strings inside JS
    # Pattern: onclick="something('word')" inside a single-quoted JS string
    issues = []
    for j, line in enumerate(lines):
        s = line.strip()
        
        # Check for getAttribute(' inside a JS string (not in HTML)
        if "getAttribute('" in s and ('onclick' in s or 'function' not in s):
            # This might be a quote nesting issue
            if s.startswith('html +=') or s.startswith("html +="):
                issues.append((j, "getAttribute quote issue", s[:150]))
        
        # Check for odd number of single quotes in JS string assignments
        if ("= '" in s or "= \"" in s) and s.count("'") % 2 != 0:
            if 'getAttribute' in s:
                issues.append((j, "Odd quotes with getAttribute", s[:150]))
    
    if issues:
        print(f"  Found {len(issues)} potential issues:")
        for line_num, desc, snippet in issues:
            print(f"    Line {line_num}: {desc}")
            print(f"      {snippet}")
    else:
        print("  No obvious quote nesting issues found")

# Also check for the specific error at line 5532
lines = c.split('\n')
if len(lines) >= 5532:
    line5532 = lines[5531]
    print(f"\nLine 5532: {line5532[:200]}")
    if "getAttribute('" in line5532:
        print("  STILL HAS UNESCAPED QUOTES!")
    elif "getAttribute(&quot;" in line5532:
        print("  Quotes are properly escaped")

# Find ALL lines with getAttribute in JS context (onclick handlers in JS strings)
print("\nAll lines with getAttribute in JS strings:")
for i, line in enumerate(lines):
    if 'getAttribute' in line and ('html +=' in line or 'onclick' in line):
        print(f"  Line {i+1}: {line.strip()[:200]}")
