"""
SEO AI Tools - Keyword Research Module
Fetches keyword suggestions, search intent, and related terms using free sources.
"""
import requests
import json
import time
import random
from config import (
    REQUEST_TIMEOUT,
    USER_AGENTS,
    DEFAULT_NUM_SUGGESTIONS,
    DEFAULT_NUM_SERP_RESULTS,
)


def _random_ua() -> str:
    return random.choice(USER_AGENTS)


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
    headers = {"User-Agent": _random_ua()}
    try:
        resp = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        suggestions = json.loads(resp.text)[1]
        return suggestions[:num]
    except Exception as e:
        print(f"[keyword_research] Autocomplete error for '{seed_keyword}': {e}")
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


def modifier_expand(seed_keyword: str, modifier_type: str = "question") -> list[str]:
    """
    Expand seed keyword with common modifier prefixes (e.g. "how to ...", "best ...").
    """
    modifiers = _MODIFIERS.get(modifier_type, _MODIFIERS["question"])
    results = []
    for mod in modifiers:
        query = f"{mod} {seed_keyword}"
        suggestions = get_google_suggestions(query, num=5)
        results.extend(suggestions)
        time.sleep(random.uniform(0.3, 0.8))
    return sorted(set(results))


# ──────────────────────────────────────────────
# 3. SERP Analysis (People Also Ask, Related)
# ──────────────────────────────────────────────


def get_serp_results(query: str, num_results: int = DEFAULT_NUM_SERP_RESULTS) -> list[dict]:
    """
    Get Google search result titles and snippets via googlesearch-python.
    Returns list of dicts: {title, url, snippet}.
    """
    try:
        from googlesearch import search as gsearch

        results = []
        for r in gsearch(query, num_results=num_results, advanced=True):
            results.append({
                "title": getattr(r, "title", ""),
                "url": getattr(r, "url", ""),
                "snippet": getattr(r, "description", ""),
            })
        return results
    except Exception as e:
        print(f"[keyword_research] SERP search error: {e}")
        return []


def get_people_also_ask(query: str) -> list[str]:
    """
    Scrape 'People Also Ask' questions from Google search results page HTML.
    Uses BeautifulSoup to parse the PAA container.
    """
    try:
        from bs4 import BeautifulSoup

        headers = {"User-Agent": _random_ua()}
        resp = requests.get(
            f"https://www.google.com/search?q={query.replace(' ', '+')}",
            headers=headers,
            timeout=REQUEST_TIMEOUT,
        )
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")

        paa_questions = []
        # People Also Ask containers use data-sgrd or jsname attributes
        for el in soup.select("[data-sgrd], .related-question-pair"):
            text = el.get_text(strip=True)
            if text and len(text) > 10:
                paa_questions.append(text)

        # Fallback: look for jGNY2V class which is the PAA header
        if not paa_questions:
            for el in soup.select(".jGNY2V, .wDYxhc"):
                text = el.get_text(strip=True)
                if text and "?" in text and len(text) > 10:
                    paa_questions.append(text)

        return list(dict.fromkeys(paa_questions))  # dedupe preserving order
    except Exception as e:
        print(f"[keyword_research] PAA scrape error: {e}")
        return []


def get_related_searches(query: str) -> list[str]:
    """
    Scrape 'Related Searches' (bottom of Google results).
    """
    try:
        from bs4 import BeautifulSoup

        headers = {"User-Agent": _random_ua()}
        resp = requests.get(
            f"https://www.google.com/search?q={query.replace(' ', '+')}",
            headers=headers,
            timeout=REQUEST_TIMEOUT,
        )
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")

        related = []
        for el in soup.select(".s75EFd, .TQc2id, [data-q]"):
            text = el.get_text(strip=True)
            if text and len(text) > 3:
                related.append(text)

        return list(dict.fromkeys(related))
    except Exception as e:
        print(f"[keyword_research] Related searches error: {e}")
        return []


# ──────────────────────────────────────────────
# 4. Search Intent Classification
# ──────────────────────────────────────────────


def classify_intent(keyword: str) -> str:
    """
    Heuristic-based search intent classifier.
    Returns: 'informational', 'navigational', 'commercial', or 'transactional'.
    """
    kw = keyword.lower()

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

    # Default: informational
    informational_signals = ["how", "what", "why", "when", "where", "guide", "tutorial", "example", "meaning", "definition", "tips"]
    if any(s in kw for s in informational_signals):
        return "informational"

    return "informational"  # default


# ──────────────────────────────────────────────
# 5. Full Keyword Research Pipeline
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

    # 3. Related searches & PAA from SERP
    results["related_searches"] = get_related_searches(seed_keyword)
    results["people_also_ask"] = get_people_also_ask(seed_keyword)

    # 4. SERP results for competitive analysis
    results["serp_results"] = get_serp_results(seed_keyword)

    # 5. Classify intent for all keywords
    all_keywords = (
        results["suggestions"]
        + results["modifier_expanded"]
        + results["related_searches"]
        + results["people_also_ask"]
    )
    for kw in all_keywords:
        results["intent_map"][kw] = classify_intent(kw)

    return results
