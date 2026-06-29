"""One-off script to find accessibility issues in index.html labels/inputs."""
import re

content = open("static/index.html", "r", encoding="utf-8").read()

# Find all labels without 'for' attribute
nofor = list(re.finditer(r'<label(?! *for=)[^>]*>', content))
print(f"Labels WITHOUT 'for': {len(nofor)}")
for i, m in enumerate(nofor):
    ctx = content[max(0, m.start()-80):m.end()+120]
    print(f"\n--- #{i+1} pos {m.start()} ---")
    print(ctx.replace("\n", " ")[:250])

# Find all inputs without 'id' attribute
noid = list(re.finditer(r'<input[^>]*(?!.*\bid=)[^>]*>', content))
print(f"\nInputs WITHOUT 'id': {len(noid)}")
for i, m in enumerate(noid):
    ctx = content[max(0, m.start()-40):m.end()+40]
    print(f"\n--- #{i+1} pos {m.start()} ---")
    print(ctx.replace("\n", " ")[:250])
