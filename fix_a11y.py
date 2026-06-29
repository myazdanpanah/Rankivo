"""Fix accessibility: add for/id associations to labels and inputs."""
import re

content = open("static/index.html", "r", encoding="utf-8").read()
original = content

# Map of data-i18n -> id prefix for generating unique IDs
i18n_to_id = {
    "seedKeyword": "seedKeyword",
    "depth": "kwDepth",
    "similarityThreshold": "clusterThreshold",
    "contentGapSeedLabel": "gapSeedKeyword",
    "contentGapCompetitorsLabel": "gapCompetitors",
    "contentGapMyKeywordsLabel": "gapMyKeywords",
    "topic": "articleTopic",
    "targetKeywords": "articleKeywords",
    "aiProvider": "articleProvider",
    "articleLanguage": "articleLanguage",
    "wordCount": "articleWordCount",
    "tone": "articleTone",
    "style": "articleStyle",
    "urlToAudit": "auditUrl",
    "focusKeyword": "auditKeyword",
    "pageType": "auditPageType",
    "uploadCsv": "batchCsv",
    "keywords": "trendsKeywords",
    "timeframe": "trendsTimeframe",
    "geo": "trendsGeo",
    "urlToCheck": "bingUrl",
    "currentPassword": "changeOldPassword",
    "newPassword": "changeNewPassword",
    "username": "adminNewUsername",
    "password": "adminNewPassword",
    "role": "adminNewRole",
    "defaultLanguage": "settingsLang",
    "defaultAiProvider": "settingsAiProvider",
    "theme": "settingsTheme",
    "loginUsername": "loginUsername",
    "loginPassword": "loginPassword",
}

fixes = 0
for i18n, id_val in i18n_to_id.items():
    # Find label with this data-i18n that lacks 'for'
    pattern = re.compile(
        r'(<label\s+class="form-label"\s+data-i18n="' + re.escape(i18n) + r'")'
    )
    m = pattern.search(content)
    if not m:
        # Try alternate order (data-i18n before class)
        pattern2 = re.compile(
            r'(<label\s+data-i18n="' + re.escape(i18n) + r'"\s+class="form-label")'
        )
        m = pattern2.search(content)
    if m:
        # Add for= attribute
        new_label = m.group(1) + f' for="{id_val}"'
        content = content[:m.start()] + new_label + content[m.end():]
        fixes += 1

        # Now find the next input/select/textarea after this label and add id if missing
        after = content[m.start():]
        # Find next input/select/textarea
        inp_pattern = re.compile(r'<(input|select|textarea)([^>]*?)(/?)>')
        inp_m = inp_pattern.search(after)
        if inp_m:
            full = inp_m.group(0)
            if f'id="{id_val}"' not in full:
                # Add id to the element
                tag = inp_m.group(1)
                attrs = inp_m.group(2)
                close = inp_m.group(3)
                if ' id=' not in attrs:
                    new_elem = f'<{tag} id="{id_val}"{attrs}{close}>'
                    pos = m.start() + inp_m.start()
                    content = content[:pos] + new_elem + content[pos + len(full):]

print(f"Fixed {fixes} labels with for/id associations")

# Verify
remaining_nofor = len(re.findall(r'<label\s+class="form-label"\s+(?!.*for=)', content))
# Count labels without for more carefully
all_form_labels = list(re.finditer(r'<label\s+class="form-label"[^>]*>', content))
still_missing = 0
for m in all_form_labels:
    if 'for=' not in m.group():
        still_missing += 1
print(f"Labels without 'for' after fix: {still_missing}")

open("static/index.html", "w", encoding="utf-8").write(content)
print("Saved static/index.html")
