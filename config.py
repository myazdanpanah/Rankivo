"""
SEO AI Tools - Configuration
Central config for API keys, model defaults, and settings.
"""
import os
import sys

# --- AI Provider Settings ---
# Set your API keys via environment variables or in a .env file
# The tool will auto-detect which providers are available


# --- Default Provider ---
# The new preferred local LLM stack provider (Ollama)
DEFAULT_PROVIDER = "ollama" 
DEFAULT_MODEL = "gemma4:latest"

# Overwrite or set default models
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma4:latest") # <-- Set to gemma4:latest

# Fallbacks (optional)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

# --- Default Provider ---
# Which AI provider to use by default: "ollama", "openai", "anthropic", "gemini"
DEFAULT_AI_PROVIDER = os.getenv("DEFAULT_AI_PROVIDER", "ollama")

# --- Scraper Settings ---
DEFAULT_NUM_SUGGESTIONS = 15
DEFAULT_NUM_SERP_RESULTS = 10
REQUEST_TIMEOUT = 10
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0",
]

# --- Content Generation Defaults ---
DEFAULT_ARTICLE_WORD_COUNT = 1500
DEFAULT_ARTICLE_TONE = "informative, authoritative"
DEFAULT_ARTICLE_STYLE = "blog post"

# --- Database Settings ---
# Set DATABASE_URL for PostgreSQL. Leave empty for SQLite (local file).
# Example: postgresql://user:password@localhost:5432/rankivo
DATABASE_URL = os.getenv("DATABASE_URL", "")

# --- Notification Settings ---
SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_PORT = os.getenv("SMTP_PORT", "587")
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM = os.getenv("SMTP_FROM", "")
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", "")
NOTIFICATION_DAYS_BEFORE = int(os.getenv("NOTIFICATION_DAYS_BEFORE", "3"))

# --- Server Settings ---
PORT = int(os.getenv("PORT", "5500"))

# --- Bing API Settings ---
# SECURITY: If you previously used a Bing API key in .env.example, it was exposed
# in git history. Rotate it immediately at https://www.bing.com/webmasters
BING_API_KEY = os.getenv("BING_API_KEY", "")

# --- PageSpeed Insights API Settings ---
# Optional. Get a key at https://developers.google.com/speed/docs/insights/v5/get-started
# Without a key, requests are rate-limited to ~1 per minute.
PAGESPEED_API_KEY = os.getenv("PAGESPEED_API_KEY", "")

# --- Google Trends Settings ---
GOOGLE_TRENDS_HL = os.getenv("GOOGLE_TRENDS_HL", "en-US")
GOOGLE_TRENDS_TZ = int(os.getenv("GOOGLE_TRENDS_TZ", "360"))

# --- Language / Locale Settings ---
DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "en")
# Supported languages: en (English), fa (Persian/Farsi)
SUPPORTED_LANGUAGES = {
    "en": "English",
    "fa": "فارسی (Persian)",
}

# --- Serper API Settings (Optional — for enhanced keyword difficulty) ---
# Get a free key at https://serper.dev (2500 queries/mo free)
SERPER_API_KEY = os.getenv("SERPER_API_KEY", "")

# --- LLM Keyword Intelligence Settings ---
# Embedding model for semantic clustering (via Ollama)
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")
# Max keywords to estimate difficulty for (to limit API calls)
DIFFICULTY_SAMPLE_SIZE = int(os.getenv("DIFFICULTY_SAMPLE_SIZE", "5"))
# Use LLM for intent classification (set to "0" to disable and use heuristic fallback)
LLM_INTENT_CLASSIFICATION = os.getenv("LLM_INTENT_CLASSIFICATION", "1") == "1"
# Use semantic embeddings for clustering (set to "0" to use word-overlap fallback)
SEMANTIC_CLUSTERING = os.getenv("SEMANTIC_CLUSTERING", "1") == "1"

# --- Auth Settings ---
# Set ADMIN_USERNAME and ADMIN_PASSWORD in .env to enable login protection.
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin12345")
SECRET_KEY = os.getenv("SECRET_KEY", "rankivo-change-me-in-production")


# ──────────────────────────────────────────────
# Shared Utilities
# ──────────────────────────────────────────────


def _safe_print(msg):
    """Print that handles Unicode on Windows (CP1252) without crashing."""
    try:
        print(msg)
    except UnicodeEncodeError:
        try:
            sys.stdout.buffer.write((str(msg) + '\n').encode('utf-8'))
        except Exception:
            pass


class _NullWriter:
    """Discards all writes silently."""
    def write(self, s): pass
    def flush(self): pass
    @property
    def buffer(self):
        return self


class suppress_output:
    """Context manager that suppresses both stdout and stderr.
    Use around third-party library calls (e.g. googlesearch) that may
    print non-ASCII text and crash on Windows CP1252."""
    def __enter__(self):
        self._orig_stdout = sys.stdout
        self._orig_stderr = sys.stderr
        self._null = _NullWriter()
        sys.stdout = self._null
        sys.stderr = self._null
        return self

    def __exit__(self, *args):
        sys.stdout = self._orig_stdout
        sys.stderr = self._orig_stderr

import random as _random

def random_ua() -> str:
    """Return a random User-Agent string from the shared pool."""
    return _random.choice(USER_AGENTS)

