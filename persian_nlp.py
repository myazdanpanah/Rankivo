"""
Rankivo — Persian (Farsi) NLP Utilities
Uses parsivar for normalization, tokenization, and stemming.
Falls back to basic regex-based processing if parsivar is unavailable.
"""
import re
import sys


def _ensure_utf8():
    """Ensure stdout can handle Persian/Arabic Unicode on Windows."""
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


# ── Parsivar-backed implementations ──────────────────────

_normalizer = None
_tokenizer = None
_stemmer = None


def _get_parsivar():
    """Lazy-load parsivar components (import once)."""
    global _normalizer, _tokenizer, _stemmer
    if _normalizer is None:
        from parsivar import Normalizer, Tokenizer, FindStems
        _normalizer = Normalizer()
        _tokenizer = Tokenizer()
        _stemmer = FindStems()
    return _normalizer, _tokenizer, _stemmer


def normalize_persian(text: str) -> str:
    """Normalize Persian text: fix characters, remove kashida, normalize whitespace."""
    try:
        normalizer, _, _ = _get_parsivar()
        return normalizer.normalize(text)
    except ImportError:
        return _normalize_fallback(text)
    except Exception:
        return _normalize_fallback(text)


def tokenize_words(text: str) -> list[str]:
    """Tokenize Persian text into words."""
    try:
        _, tokenizer, _ = _get_parsivar()
        return tokenizer.tokenize_words(text)
    except ImportError:
        return _tokenize_fallback(text)
    except Exception:
        return _tokenize_fallback(text)


def tokenize_sentences(text: str) -> list[str]:
    """Tokenize Persian text into sentences."""
    try:
        _, tokenizer, _ = _get_parsivar()
        return tokenizer.tokenize_sentences(text)
    except ImportError:
        return _sentence_tokenize_fallback(text)
    except Exception:
        return _sentence_tokenize_fallback(text)


def stem_word(word: str) -> str:
    """Get the stem of a Persian word."""
    try:
        _, _, stemmer = _get_parsivar()
        return stemmer.convert_to_stem(word)
    except ImportError:
        return word
    except Exception:
        return word


def stem_words(words: list[str]) -> list[str]:
    """Get stems for a list of Persian words."""
    return [stem_word(w) for w in words]


def extract_keywords_persian(text: str, top_n: int = 20) -> list[tuple[str, int]]:
    """
    Extract keywords from Persian text using tokenization + frequency analysis.
    Returns list of (keyword, count) tuples sorted by frequency.
    """
    words = tokenize_words(text)
    # Filter out stop words and short tokens
    stop_words = {
        "و", "در", "به", "از", "که", "این", "را", "با", "است", "برای",
        "آن", "یک", "خود", "تا", "کرد", "بر", "هم", "نیز", "گفت", "می",
        "شود", "شده", "بود", "دارد", "ها", "های", "شد", "یا", "اما",
        "باید", "پس", "اگر", "وقتی", "آنکه", "می‌شود", "می‌کند",
        "the", "a", "an", "is", "are", "was", "were", "in", "on", "at",
        "to", "for", "of", "with", "by", "from", "and", "or", "but",
    }
    freq = {}
    for w in words:
        w_lower = w.strip(".,!?;:\"'«»()[]{}|/\\").lower()
        if len(w_lower) < 2 or w_lower in stop_words:
            continue
        freq[w_lower] = freq.get(w_lower, 0) + 1
    return sorted(freq.items(), key=lambda x: x[1], reverse=True)[:top_n]


# ── Fallback implementations (no parsivar) ──────────────


def _normalize_fallback(text: str) -> str:
    """Basic Persian normalization without parsivar."""
    # Arabic Yeh/Keh → Persian variants
    text = text.replace("ي", "ی").replace("ك", "ک")
    text = text.replace("ؤ", "و").replace("إ", "ا").replace("أ", "ا")
    text = text.replace("ٱ", "ا")
    # Remove tatweel (kashida)
    text = text.replace("\u0640", "")
    # Arabic numerals → ASCII
    arabic_digits = "\u0660\u0661\u0662\u0663\u0664\u0665\u0666\u0667\u0668\u0669"
    for i, d in enumerate(arabic_digits):
        text = text.replace(d, str(i))
    # Persian numerals → ASCII
    persian_digits = "\u06f0\u06f1\u06f2\u06f3\u06f4\u06f5\u06f6\u06f7\u06f8\u06f9"
    for i, d in enumerate(persian_digits):
        text = text.replace(d, str(i))
    # Normalize whitespace
    text = " ".join(text.split())
    return text


def _tokenize_fallback(text: str) -> list[str]:
    """Basic word tokenization using regex."""
    text = _normalize_fallback(text)
    # Split on whitespace and non-word characters (keep Persian/Arabic chars)
    tokens = re.findall(r"[\w\u0600-\u06FF\uFB50-\uFDFF\uFE70-\uFEFF]+", text)
    return [t for t in tokens if len(t) > 1]


def _sentence_tokenize_fallback(text: str) -> list[str]:
    """Basic sentence tokenization using regex."""
    # Split on sentence-ending punctuation
    sentences = re.split(r"[.!؟!]+", text)
    return [s.strip() for s in sentences if s.strip()]


# ── Utility ──────────────────────────────────────────────


def is_persian_text(text: str) -> bool:
    """Check if text is predominantly Persian/Arabic."""
    persian_range = range(0x0600, 0x06FF + 1)
    arabic_range = range(0xFB50, 0xFDFF + 1)
    extended_arabic = range(0xFE70, 0xFEFF + 1)
    persian_count = sum(
        1 for c in text
        if ord(c) in persian_range or ord(c) in arabic_range or ord(c) in extended_arabic
    )
    return persian_count > len(text) * 0.3


def get_nlp_status() -> dict:
    """Check which Persian NLP capabilities are available."""
    try:
        from parsivar import Normalizer, Tokenizer, FindStems
        return {
            "parsivar": True,
            "normalization": True,
            "tokenization": True,
            "stemming": True,
        }
    except ImportError:
        return {
            "parsivar": False,
            "normalization": True,  # fallback available
            "tokenization": True,  # fallback available
            "stemming": False,  # no fallback
        }
