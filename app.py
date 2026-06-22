"""
Rankivo — SEO AI Tools
Entry point: Run `python app.py` to start the Web UI.
"""
import os
from api import app
from config import PORT

debug_mode = os.getenv("FLASK_DEBUG", "0") == "1"

if __name__ == "__main__":
    print(f"Rankivo Web UI starting at http://localhost:{PORT}")
    app.run(debug=debug_mode, host="0.0.0.0", port=PORT)
