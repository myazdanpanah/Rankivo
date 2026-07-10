"""Add the missing /api/intent-training endpoint to api.py"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open('api.py', 'r', encoding='utf-8') as f:
    content = f.read()

if '/api/intent-training' in content:
    print('/api/intent-training already exists')
    sys.exit(0)

endpoint_code = """
# ──────────────────────────────────────────────
# Intent Training Data Management
# ──────────────────────────────────────────────

_intent_training_data = {}  # intent -> list of {word, language}


@require_auth
@app.route("/api/intent-training", methods=["GET"])
def api_intent_training_get():
    total = sum(len(v) for v in _intent_training_data.values())
    return jsonify({"training_data": _intent_training_data, "total": total})


@require_auth
@app.route("/api/intent-training", methods=["POST"])
def api_intent_training_add():
    data = request.json or {}
    word = data.get("word", "").strip()
    intent = data.get("intent", "informational")
    if not word:
        return jsonify({"error": "Word is required"}), 400
    if intent not in _intent_training_data:
        _intent_training_data[intent] = []
    existing = [
        e for e in _intent_training_data[intent]
        if (e.get("word") if isinstance(e, dict) else e) == word
    ]
    if existing:
        return jsonify({"error": f"Word '{word}' already exists in {intent}"}), 409
    _intent_training_data[intent].append({
        "word": word,
        "language": data.get("language", "auto"),
    })
    return jsonify({"success": True, "word": word, "intent": intent})


@require_auth
@app.route("/api/intent-training", methods=["DELETE"])
def api_intent_training_delete():
    data = request.json or {}
    word = data.get("word", "").strip()
    intent = data.get("intent", "")
    if not word or not intent:
        return jsonify({"error": "Word and intent are required"}), 400
    if intent in _intent_training_data:
        before = len(_intent_training_data[intent])
        _intent_training_data[intent] = [
            e for e in _intent_training_data[intent]
            if (e.get("word") if isinstance(e, dict) else e) != word
        ]
        if len(_intent_training_data[intent]) < before:
            return jsonify({"success": True, "removed": word})
    return jsonify({"error": f"Word '{word}' not found in {intent}"}), 404


"""

insert_point = content.rfind('if __name__')
if insert_point > 0:
    content = content[:insert_point] + endpoint_code + content[insert_point:]
    with open('api.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('Added /api/intent-training endpoint to api.py')
else:
    print('ERROR: Could not find insert point in api.py')
