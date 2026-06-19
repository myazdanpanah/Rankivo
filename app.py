"""
Rankivo — SEO AI Tools
Entry point: Run `python app.py` to start the Web UI.
"""
from api import app
from config import PORT

if __name__ == "__main__":
    print(f"Rankivo Web UI starting at http://localhost:{PORT}")
    app.run(debug=True, host="0.0.0.0", port=PORT)
