"""
Rankivo — SEO AI Tools
Entry point: Run `python app.py` to start the Web UI on port 5000.
"""
from api import app

if __name__ == "__main__":
    print("🚀 Rankivo Web UI starting at http://localhost:5000")
    app.run(debug=True, host="0.0.0.0", port=5000)
