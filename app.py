"""
Rankivo — SEO AI Tools
Entry point: Run `python app.py` to start the Web UI.
"""
import os
import sys

# Load .env file if present (python-dotenv)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Force UTF-8 stdout/stderr to prevent CP1252 crashes with Persian/Arabic text.
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

# Set stdout encoding before importing modules that print Unicode (e.g. Persian/Arabic text)
from api import app
from config import PORT

debug_mode = os.getenv("FLASK_DEBUG", "0") == "1"

if __name__ == "__main__":
    print(f"Rankivo Web UI starting at http://localhost:{PORT}")
    app.run(debug=debug_mode, host="0.0.0.0", port=PORT)
