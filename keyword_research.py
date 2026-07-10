"""
SEO AI Tools - Keyword Research Module
Fetches keyword suggestions, search intent, and related terms using free sources.
Includes anti-detection measures and multi-engine fallbacks (Google → DuckDuckGo → Bing).
"""
import os
import requests
import json
import time
import random
import re
from config import (
    random_ua,
    REQUEST_TIMEOUT,
    USER_AGENTS,
    DEFAULT_NUM_SUGGESTIONS,
    DEFAULT_NUM_SERP_RESULTS,
    _safe_print,
    suppress_output,
)




def _get_session():
    """Create a requests session with persistent headers to look like a real browser."""
    s = requests.Session()
    ua = random_ua()
    s.headers.update({
        "User-Agent": ua,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9,fa;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0",
    })
    return s


# ──────────────────────────────────────────────
# 1. Google Autocomplete Suggestions
# ──────────────────────────────────────────────

def get_google_suggestions(seed_keyword: str, num: int = DEFAULT_NUM_SUGGESTIONS) -> list[str]:
    """
    Fetch autocomplete suggestions from Google's undocumented suggest endpoint.
    Returns a list of suggested keyword strings.
    """
    query = seed_keyword.replace(" ", "+")
    url = f"http://suggestqueries.google.com/complete/search?output=firefox&q={query}"
    headers = {"User-Agent": random_ua()}
    try:
        resp = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        suggestions = json.loads(resp.text)[1]
        return suggestions[:num]
    except Exception as e:
        _safe_print(f"[keyword_research] Autocomplete error for '{seed_keyword}': {e}")
        return []


def expand_keywords(seed_keyword: str, depth: int = 1) -> list[str]:
    """
    Recursively expand a seed keyword by feeding each suggestion back
    into the autocomplete API. `depth` controls how many levels deep.
    """
    all_keywords = set()
    current_layer = [seed_keyword]

    for _ in range(depth):
        next_layer = []
        for kw in current_layer:
            suggestions = get_google_suggestions(kw)
            for s in suggestions:
                if s not in all_keywords:
                    next_layer.append(s)
                    all_keywords.add(s)
            time.sleep(random.uniform(0.3, 0.8))
        current_layer = next_layer

    return sorted(all_keywords)


# ──────────────────────────────────────────────
# 2. Alphabet / Modifier Expansion
# ──────────────────────────────────────────────


_MODIFIERS = {
    "question": ["how", "what", "why", "when", "where", "who", "which"],
    "commercial": ["best", "top", "review", "vs", "alternative", "cheap", "affordable"],
    "navigational": ["login", "official", "website", "app"],
    "informational": ["guide", "tutorial", "example", "definition", "meaning", "list"],
}

# Persian modifiers for Persian keyword expansion
_MODIFIERS_FA = {
    "question": ["چگونه", "چطور", "نحوه", "چیست", "چرا", "کجا", "کی"],
    "commercial": ["بهترین", "ارزان", "قیمت", "خرید", "مقایسه", "بررسی"],
    "navigational": ["ورود", "سایت رسمی", "اپلیکیشن", "اپ"],
    "informational": ["آموزش", "راهنما", "معرفی", "تعریف", "نکات", "لیست"],
}


def modifier_expand(seed_keyword: str, modifier_type: str = "question") -> list[str]:
    """
    Expand seed keyword with common modifier prefixes (e.g. "how to ...", "best ...").
    Automatically detects Persian keywords and uses Persian modifiers.
    """
    # Detect if keyword is Persian
    is_persian = any("\u0600" <= c <= "\u06FF" for c in seed_keyword)
    modifiers_fa = _MODIFIERS_FA.get(modifier_type, _MODIFIERS_FA["question"])
    modifiers_en = _MODIFIERS.get(modifier_type, _MODIFIERS["question"])

    results = []
    # Use Persian modifiers for Persian keywords, English for English
    mods = modifiers_fa if is_persian else modifiers_en
    for mod in mods:
        query = f"{mod} {seed_keyword}"
        suggestions = get_google_suggestions(query, num=5)
        results.extend(suggestions)
        time.sleep(random.uniform(0.3, 0.8))
    return sorted(set(results))


# ──────────────────────────────────────────────
# 3. SERP Analysis — Multi-engine with fallbacks
# ──────────────────────────────────────────────

def get_serp_results(query: str, num_results: int = DEFAULT_NUM_SERP_RESULTS) -> list[dict]:
    """
    Get search results using multiple engines with fallback:
    1. Google (googlesearch-python)
    2. DuckDuckGo (duckduckgo_search)
    3. Bing (direct HTML scraping)
    """
    # Try Google first
    results = _get_serp_google(query, num_results)
    if results:
        return results

    # Fallback: DuckDuckGo
    _safe_print(f"[keyword_research] Google blocked, trying DuckDuckGo...")
    results = _get_serp_duckduckgo(query, num_results)
    if results:
        return results

    # Fallback: Bing
    _safe_print(f"[keyword_research] Trying Bing...")
    results = _get_serp_bing(query, num_results)
    return results


def _get_serp_google(query: str, num_results: int) -> list[dict]:
    """Try Google search via googlesearch-python."""
    try:
        from googlesearch import search as gsearch
        results = []
        with suppress_output():
            for r in gsearch(query, num_results=num_results, advanced=True):
                results.append({
                    "title": getattr(r, "title", ""),
                    "url": getattr(r, "url", ""),
                    "snippet": getattr(r, "description", ""),
                    "source": "google",
                })
        return results
    except Exception as e:
        _safe_print(f"[keyword_research] Google SERP error: {e}")
        return []


def _get_serp_duckduckgo(query: str, num_results: int) -> list[dict]:
    """Try DuckDuckGo search as fallback."""
    try:
        from duckduckgo_search import DDGS
        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=num_results):
                results.append({
                    "title": r.get("title", ""),
                    "url": r.get("href", ""),
                    "snippet": r.get("body", ""),
                    "source": "duckduckgo",
                })
        return results
    except Exception as e:
        _safe_print(f"[keyword_research] DuckDuckGo error: {e}")
        return []


def _get_serp_bing(query: str, num_results: int) -> list[dict]:
    """Scrape Bing search results as last fallback."""
    try:
        from bs4 import BeautifulSoup
        session = _get_session()
        resp = session.get(
            f"https://www.bing.com/search?q={query.replace(' ', '+')}&count={num_results}",
            timeout=REQUEST_TIMEOUT,
        )
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")

        results = []
        for li in soup.select("#b_results > li.b_algo"):
            title_tag = li.select_one("h2 a")
            snippet_tag = li.select_one(".b_caption p")
            if title_tag:
                results.append({
                    "title": title_tag.get_text(strip=True),
                    "url": title_tag.get("href", ""),
                    "snippet": snippet_tag.get_text(strip=True) if snippet_tag else "",
                    "source": "bing",
                })
        return results[:num_results]
    except Exception as e:
        _safe_print(f"[keyword_research] Bing SERP error: {e}")
        return []


def get_people_also_ask(query: str) -> list[str]:
    """
    Get 'People Also Ask' questions using multiple engines:
    1. Google SERP HTML scraping
    2. DuckDuckGo related questions
    3. Google Autocomplete question expansion
    """
    # Try Google PAA first
    questions = _get_paa_google(query)
    if questions:
        return questions

    # Fallback: DuckDuckGo
    _safe_print(f"[keyword_research] Google PAA blocked, trying DuckDuckGo...")
    questions = _get_paa_duckduckgo(query)
    if questions:
        return questions

    # Fallback: generate from autocomplete
    _safe_print(f"[keyword_research] Using autocomplete expansion for PAA...")
    return _get_paa_autocomplete(query)


def _get_paa_google(query: str) -> list[str]:
    """Scrape PAA from Google search HTML."""
    try:
        from bs4 import BeautifulSoup
        session = _get_session()
        resp = session.get(
            f"https://www.google.com/search?q={query.replace(' ', '+')}",
            timeout=REQUEST_TIMEOUT,
        )
        resp.raise_for_status()

        # Check if we got blocked (CAPTCHA page)
        if "captcha" in resp.text.lower() or "unusual traffic" in resp.text.lower():
            _safe_print("[keyword_research] Google CAPTCHA detected")
            return []

        soup = BeautifulSoup(resp.text, "lxml")
        paa_questions = []

        # People Also Ask containers
        for el in soup.select("[data-sgrd], .related-question-pair"):
            text = el.get_text(strip=True)
            if text and len(text) > 10:
                paa_questions.append(text)

        if not paa_questions:
            for el in soup.select(".jGNY2V, .wDYxhc, [data-q]"):
                text = el.get_text(strip=True)
                if text and "?" in text and len(text) > 10:
                    paa_questions.append(text)

        return list(dict.fromkeys(paa_questions))
    except Exception as e:
        _safe_print(f"[keyword_research] Google PAA error: {e}")
        return []


def _get_paa_duckduckgo(query: str) -> list[str]:
    """Get related questions from DuckDuckGo."""
    try:
        from duckduckgo_search import DDGS
        questions = []
        with DDGS() as ddgs:
            for r in ddgs.text(f"{query} questions", max_results=10):
                title = r.get("title", "")
                if "?" in title or title.lower().startswith(("how", "what", "why", "when", "where", "who")):
                    questions.append(title)
        return list(dict.fromkeys(questions))[:10]
    except Exception as e:
        _safe_print(f"[keyword_research] DuckDuckGo PAA error: {e}")
        return []


def _get_paa_autocomplete(query: str) -> list[str]:
    """Generate PAA-style questions from autocomplete suggestions."""
    question_prefixes = ["how to", "what is", "why", "when to", "where to", "which"]
    questions = []
    for prefix in question_prefixes:
        suggestions = get_google_suggestions(f"{prefix} {query}", num=3)
        for s in suggestions:
            if not s.lower().startswith(prefix.split()[0]):
                s = f"{prefix} {s}"
            if s not in questions:
                questions.append(s)
        time.sleep(0.3)
    return questions[:10]


def get_related_searches(query: str) -> list[str]:
    """
    Get related searches using multiple engines:
    1. Google SERP HTML
    2. DuckDuckGo
    3. Bing
    """
    # Try Google first
    related = _get_related_google(query)
    if related:
        return related

    # Fallback: DuckDuckGo
    _safe_print(f"[keyword_research] Google related blocked, trying DuckDuckGo...")
    related = _get_related_duckduckgo(query)
    if related:
        return related

    # Fallback: Bing
    _safe_print(f"[keyword_research] Trying Bing related...")
    return _get_related_bing(query)


def _get_related_google(query: str) -> list[str]:
    """Scrape related searches from Google HTML."""
    try:
        from bs4 import BeautifulSoup
        session = _get_session()
        resp = session.get(
            f"https://www.google.com/search?q={query.replace(' ', '+')}",
            timeout=REQUEST_TIMEOUT,
        )
        resp.raise_for_status()

        if "captcha" in resp.text.lower() or "unusual traffic" in resp.text.lower():
            return []

        soup = BeautifulSoup(resp.text, "lxml")
        related = []
        for el in soup.select(".s75EFd, .TQc2id, [data-q]"):
            text = el.get_text(strip=True)
            if text and len(text) > 3:
                related.append(text)
        return list(dict.fromkeys(related))
    except Exception as e:
        _safe_print(f"[keyword_research] Google related error: {e}")
        return []


def _get_related_duckduckgo(query: str) -> list[str]:
    """Get related searches from DuckDuckGo."""
    try:
        from duckduckgo_search import DDGS
        related = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=10):
                title = r.get("title", "")
                if title and len(title) > 3 and title != query:
                    related.append(title)
        return list(dict.fromkeys(related))[:10]
    except Exception as e:
        _safe_print(f"[keyword_research] DuckDuckGo related error: {e}")
        return []


def _get_related_bing(query: str) -> list[str]:
    """Get related searches from Bing HTML."""
    try:
        from bs4 import BeautifulSoup
        session = _get_session()
        resp = session.get(
            f"https://www.bing.com/search?q={query.replace(' ', '+')}",
            timeout=REQUEST_TIMEOUT,
        )
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")
        related = []
        for el in soup.select(".b_rs a, .b_algoSlug"):
            text = el.get_text(strip=True)
            if text and len(text) > 3:
                related.append(text)
        return list(dict.fromkeys(related))[:10]
    except Exception as e:
        _safe_print(f"[keyword_research] Bing related error: {e}")
        return []


# ──────────────────────────────────────────────
# 4. Search Intent Classification
# ──────────────────────────────────────────────

def classify_intent(keyword: str) -> str:
    """
    Heuristic-based search intent classifier.
    Supports both English and Persian keywords.
    Returns: 'informational', 'navigational', 'commercial', or 'transactional'.
    """
    kw = keyword.lower()

    # Check if Persian
    is_persian = any("\u0600" <= c <= "\u06FF" for c in keyword)

    if is_persian:
        return _classify_intent_persian(kw)

    # Transactional
    transactional_signals = ["buy", "price", "cost", "cheap", "deal", "discount", "order", "purchase", "subscribe", "download free"]
    if any(s in kw for s in transactional_signals):
        return "transactional"

    # Navigational
    navigational_signals = ["login", "sign in", "official", "website", "app", "homepage"]
    if any(s in kw for s in navigational_signals):
        return "navigational"

    # Commercial investigation
    commercial_signals = ["best", "top", "review", "vs", "comparison", "alternative", "recommend", "compare", "which"]
    if any(s in kw for s in commercial_signals):
        return "commercial"

    return "informational"


def _classify_intent_persian(kw: str) -> str:
    """Classify intent for Persian keywords."""
    # Transactional
    if any(s in kw for s in ["خرید", "قیمت", "ارزان", "سفارش", "تخفیف", "دانلود", "پرداخت", "فروش"]):
        return "transactional"
    # Navigational
    if any(s in kw for s in ["ورود", "لاگین", "سایت رسمی", "اپلیکیشن", "حساب کاربری"]):
        return "navigational"
    # Commercial
    if any(s in kw for s in ["بهترین", "مقایسه", "بررسی", "تفاوت", "جایگزین", "لیست"]):
        return "commercial"
    return "informational"


# ──────────────────────────────────────────────
# 5. User Intent Training — custom word patterns
# ──────────────────────────────────────────────

# In-memory custom intent patterns (persisted via JSON file)
import os

_INTENT_TRAINING_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "data", "intent_training.json"
)


def _load_intent_training() -> dict:
    """Load custom intent training data from file."""
    try:
        with open(_INTENT_TRAINING_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {
            "transactional": [],
            "navigational": [],
            "commercial": [],
            "informational": [],
        }


def _save_intent_training(data: dict) -> None:
    """Save custom intent training data to file."""
    os.makedirs(os.path.dirname(_INTENT_TRAINING_FILE), exist_ok=True)
    with open(_INTENT_TRAINING_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def add_intent_training_word(word: str, intent: str, language: str = "auto") -> dict:
    """
    Add a custom word/phrase to the intent training data.
    The AI will use this to better classify similar keywords.

    Args:
        word: The word or phrase to add (e.g. "cost calculator" → transactional)
        intent: One of: 'transactional', 'navigational', 'commercial', 'informational'
        language: 'en', 'fa', or 'auto' (detect from text)

    Returns:
        dict with status and updated counts
    """
    valid_intents = ["transactional", "navigational", "commercial", "informational"]
    if intent not in valid_intents:
        return {"error": f"Invalid intent. Must be one of: {valid_intents}"}

    word = word.strip()
    if not word:
        return {"error": "Word cannot be empty"}

    # Auto-detect language
    if language == "auto":
        language = "fa" if any("\u0600" <= c <= "\u06FF" for c in word) else "en"

    training = _load_intent_training()

    # Add word with language tag
    entry = {"word": word, "language": language, "added_at": time.time()}
    if word not in [e["word"] if isinstance(e, dict) else e for e in training[intent]]:
        # Handle both old format (string) and new format (dict)
        existing = training[intent]
        if existing and isinstance(existing[0], str):
            # Convert old format
            training[intent] = [{"word": w, "language": "auto"} for w in existing]
        training[intent].append(entry)
        _save_intent_training(training)

    # Count totals
    counts = {k: len(v) for k, v in training.items()}
    return {
        "success": True,
        "word": word,
        "intent": intent,
        "language": language,
        "total_words": counts,
    }


def remove_intent_training_word(word: str, intent: str) -> dict:
    """Remove a custom word from intent training data."""
    training = _load_intent_training()
    if intent not in training:
        return {"error": f"Intent '{intent}' not found"}

    before = len(training[intent])
    training[intent] = [
        e for e in training[intent]
        if (e["word"] if isinstance(e, dict) else e) != word
    ]
    after = len(training[intent])

    if before == after:
        return {"error": f"Word '{word}' not found in {intent}"}

    _save_intent_training(training)
    return {"success": True, "word": word, "removed_from": intent}


def get_intent_training_data() -> dict:
    """Get all custom intent training data."""
    training = _load_intent_training()
    counts = {k: len(v) for k, v in training.items()}
    return {
        "training_data": training,
        "counts": counts,
        "total": sum(counts.values()),
    }


# ──────────────────────────────────────────────
# 6. Full Keyword Research Pipeline
# ──────────────────────────────────────────────

def run_keyword_research(seed_keyword: str, depth: int = 1, expand_with_modifiers: bool = True) -> dict:
    """
    Run a complete keyword research pipeline.
    Returns a dict with all keyword data.
    """
    results = {
        "seed": seed_keyword,
        "suggestions": [],
        "modifier_expanded": [],
        "alphabet_expanded": [],
        "related_searches": [],
        "people_also_ask": [],
        "serp_results": [],
        "intent_map": {},
    }

    # 1. Autocomplete suggestions
    results["suggestions"] = expand_keywords(seed_keyword, depth=depth)

    # 2. Modifier expansion
    if expand_with_modifiers:
        for mod_type in ["question", "commercial", "informational"]:
            results["modifier_expanded"].extend(modifier_expand(seed_keyword, modifier_type=mod_type))
        results["modifier_expanded"] = sorted(set(results["modifier_expanded"]))

    # 3. Related searches & PAA from SERP (with multi-engine fallbacks)
    results["related_searches"] = get_related_searches(seed_keyword)
    results["people_also_ask"] = get_people_also_ask(seed_keyword)

    # 4. SERP results for competitive analysis
    results["serp_results"] = get_serp_results(seed_keyword)

    # 5. Classify intent for all keywords (using custom training data)
    training = _load_intent_training()
    all_keywords = (
        results["suggestions"]
        + results["modifier_expanded"]
        + results["related_searches"]
        + results["people_also_ask"]
    )
    for kw in all_keywords:
        results["intent_map"][kw] = classify_intent_with_training(kw, training)

    return results


def classify_intent_with_training(keyword: str, training: dict = None) -> str:
    """
    Classify intent using both heuristic rules AND custom training data.
    Training data takes priority when there's a direct match.
    """
    if training is None:
        training = _load_intent_training()

    kw_lower = keyword.lower()

    # Check custom training data first (exact match)
    for intent, entries in training.items():
        for entry in entries:
            word = entry["word"] if isinstance(entry, dict) else entry
            if word.lower() in kw_lower or kw_lower in word.lower():
                return intent

    # Fall back to heuristic classification
    return classify_intent(keyword)
