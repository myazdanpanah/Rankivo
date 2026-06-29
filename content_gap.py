"""
SEO AI Tools - Content Gap Analysis Module
Finds topics/keywords competitors rank for that you don't.
Combines SERP analysis with on-page content extraction.
"""
import requests
import time
import random
import re
import ipaddress
from collections import Counter
from typing import Optional
from config import REQUEST_TIMEOUT, USER_AGENTS, _safe_print, suppress_output



def _random_ua() -> str:
    return random.choice(USER_AGENTS)

def _is_safe_url(url: str) -> bool:
    """Check if a URL is safe to fetch (blocks private IPs, localhost, metadata endpoints)."""
    from urllib.parse import urlparse
    try:
        parsed = urlparse(url)
        hostname = parsed.hostname or ""
        
        # Block localhost and common internal hostnames
        blocked_hostnames = [
            "localhost", "metadata.google", "metadata.google.internal",
            "metadata.aws.internal", "169.254.169.254",
        ]
        if hostname.lower() in blocked_hostnames:
            return False
        
        # Check if scheme is allowed
        if parsed.scheme not in ("http", "https"):
            return False
        
        # Parse IP and check if it's private/reserved
        try:
            ip = ipaddress.ip_address(hostname)
            if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast:
                return False
        except ValueError:
            pass  # hostname is not an IP, that's fine
        
        return True
    except Exception:
        return False



# ──────────────────────────────────────────────
# 1. SERP Scraping — find competitor URLs for a keyword
# ──────────────────────────────────────────────

def get_serp_competitors(keyword: str, num_results: int = 10) -> list[dict]:
    """
    Get top-ranking competitor URLs for a keyword from Google SERP.
    Returns list of {title, url, snippet}.
    """
    try:
        from googlesearch import search as gsearch
        results = []
        # Suppress googlesearch's internal stdout/stderr to avoid CP1252 crashes
        # The library captures sys.stdout at import time, so we must suppress
        # all output for the ENTIRE call including iteration
        with suppress_output():
            for r in gsearch(keyword, num_results=num_results, advanced=True):
                url = getattr(r, "url", "")
                if url and _is_safe_url(url):
                    results.append({
                        "title": getattr(r, "title", ""),
                        "url": url,
                        "snippet": getattr(r, "description", ""),
                    })
        return results
    except Exception as e:
        _safe_print(f"[content_gap] SERP search error for '{keyword}': {e}")
        return []


# ──────────────────────────────────────────────
# 2. Competitor Page Content Extraction
# ──────────────────────────────────────────────

def extract_page_content(url: str) -> dict:
    """
    Fetch a page and extract its content: title, meta description,
    headings (h1-h3), body text, and internal/external links.
    """
    if not _is_safe_url(url):
        return {"url": url, "success": False, "error": "URL blocked for safety (private IP or invalid scheme)"}

    try:
        from bs4 import BeautifulSoup
        headers = {"User-Agent": _random_ua()}
        resp = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT, allow_redirects=True)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")

        # Title
        title_tag = soup.find("title")
        title = title_tag.get_text(strip=True) if title_tag else ""

        # Meta description
        meta_desc = soup.find("meta", attrs={"name": "description"})
        description = meta_desc.get("content", "").strip() if meta_desc else ""

        # Headings
        headings = {}
        for level in ["h1", "h2", "h3"]:
            tags = soup.find_all(level)
            headings[level] = [t.get_text(strip=True) for t in tags if t.get_text(strip=True)]

        # Body text — extract from main content areas, skip nav/footer/scripts
        for tag in soup.find_all(["nav", "footer", "header", "script", "style", "noscript"]):
            tag.decompose()

        # Try to find main content area first
        main_content = soup.find("main") or soup.find("article") or soup.find("body")
        body_text = main_content.get_text(separator=" ", strip=True) if main_content else ""

        # Word count
        word_count = len(body_text.split())

        return {
            "url": url,
            "title": title,
            "description": description,
            "headings": headings,
            "body_text": body_text,
            "word_count": word_count,
            "success": True,
        }
    except Exception as e:
        _safe_print(f"[content_gap] Content extraction error for '{url}': {e}")
        return {"url": url, "success": False, "error": str(e)}


# ──────────────────────────────────────────────
# 3. Keyword Extraction from Text
# ──────────────────────────────────────────────

def extract_keywords_from_text(text: str, top_n: int = 30) -> list[dict]:
    """
    Extract top keywords/phrases from text using RAKE or TF-IDF fallback.
    Returns list of {keyword, score, count}.
    """
    if not text or len(text.split()) < 10:
        return []

    # Try RAKE first
    try:
        from rake_nltk import Rake
        r = Rake(min_length=1, max_length=4, include_repeated_phrases=False)
        r.extract_keywords_from_text(text)
        ranked = r.get_ranked_phrases_with_scores()
        results = []
        for score, phrase in ranked[:top_n]:
            # Clean up the phrase
            phrase = phrase.strip().lower()
            if len(phrase) > 2 and not phrase.isdigit():
                results.append({"keyword": phrase, "score": round(score, 2), "count": 1})
        return results
    except ImportError:
        pass

    # Fallback: simple TF-IDF-like extraction using word frequency
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        # Split text into sentences for TF-IDF
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if len(s.strip().split()) > 3]

        if len(sentences) < 2:
            # Not enough sentences, use word frequency instead
            return _extract_keywords_frequency(text, top_n)

        vectorizer = TfidfVectorizer(
            max_features=200,
            ngram_range=(1, 3),
            stop_words="english",
            min_df=1,
            max_df=0.9,
        )
        tfidf_matrix = vectorizer.fit_transform(sentences)
        feature_names = vectorizer.get_feature_names_out()

        # Get average TF-IDF score across all sentences
        import numpy as np
        avg_scores = np.asarray(tfidf_matrix.mean(axis=0)).flatten()
        top_indices = avg_scores.argsort()[::-1][:top_n]

        results = []
        for idx in top_indices:
            keyword = feature_names[idx]
            score = float(avg_scores[idx])
            if len(keyword) > 2 and not keyword.isdigit():
                results.append({"keyword": keyword, "score": round(score, 4), "count": 1})
        return results
    except ImportError:
        return _extract_keywords_frequency(text, top_n)


def _extract_keywords_frequency(text: str, top_n: int = 30) -> list[dict]:
    """Simple word/n-gram frequency extraction as fallback."""
    # Common English stop words
    stop_words = {
        "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
        "of", "with", "by", "from", "is", "are", "was", "were", "be", "been",
        "being", "have", "has", "had", "do", "does", "did", "will", "would",
        "could", "should", "may", "might", "shall", "can", "this", "that",
        "these", "those", "it", "its", "not", "no", "nor", "so", "if", "then",
        "than", "too", "very", "just", "about", "above", "after", "again",
        "all", "also", "any", "as", "because", "before", "between", "both",
        "each", "few", "more", "most", "other", "some", "such", "into",
        "over", "own", "same", "through", "under", "until", "up", "while",
        "you", "your", "we", "our", "they", "their", "he", "she", "him",
        "her", "his", "my", "me", "what", "which", "who", "whom", "where",
        "when", "how", "why", "here", "there", "now", "only", "than",
    }

    words = re.findall(r'[a-z]+', text.lower())

    # Unigrams
    word_freq = Counter(w for w in words if w not in stop_words and len(w) > 2)

    # Bigrams
    bigrams = [f"{words[i]} {words[i+1]}" for i in range(len(words)-1)]
    bigram_freq = Counter(
        bg for bg in bigrams
        if not any(w in stop_words for w in bg.split())
        and len(bg) > 4
    )

    # Trigrams
    trigrams = [f"{words[i]} {words[i+1]} {words[i+2]}" for i in range(len(words)-2)]
    trigram_freq = Counter(
        tg for tg in trigrams
        if not all(w in stop_words for w in tg.split())
        and len(tg) > 6
    )

    # Combine and rank
    all_phrases = {}
    for phrase, count in trigram_freq.most_common(top_n):
        all_phrases[phrase] = {"keyword": phrase, "score": count * 3, "count": count}
    for phrase, count in bigram_freq.most_common(top_n):
        if phrase not in all_phrases:
            all_phrases[phrase] = {"keyword": phrase, "score": count * 2, "count": count}
    for word, count in word_freq.most_common(top_n):
        if word not in all_phrases:
            all_phrases[word] = {"keyword": word, "score": count, "count": count}

    results = sorted(all_phrases.values(), key=lambda x: x["score"], reverse=True)
    return results[:top_n]


# ──────────────────────────────────────────────
# 4. Gap Calculation
# ──────────────────────────────────────────────

def calculate_content_gaps(
    my_keywords: list[str],
    competitor_data: list[dict],
    min_score: float = 0.01,
) -> dict:
    """
    Compare user's keywords against competitor extracted keywords to find gaps.

    Args:
        my_keywords: User's existing keywords (from keyword research).
        competitor_data: List of {url, keywords: [{keyword, score}]} per competitor.
        min_score: Minimum keyword score threshold.

    Returns:
        Dict with gap_analysis (list of gap keywords), competitor_summary, and stats.
    """
    # Normalize user keywords to a set of lowercased terms
    my_kw_lower = set()
    for kw in my_keywords:
        my_kw_lower.add(kw.lower().strip())
        # Also add individual words from multi-word keywords
        for word in kw.lower().split():
            if len(word) > 2:
                my_kw_lower.add(word)

    # Aggregate competitor keywords with frequency tracking
    competitor_keyword_freq = Counter()
    competitor_keyword_scores = {}
    competitor_urls = []

    for comp in competitor_data:
        if not comp.get("success", False):
            continue
        competitor_urls.append(comp["url"])
        for kw_info in comp.get("keywords", []):
            keyword = kw_info["keyword"].lower().strip()
            score = kw_info.get("score", 1)
            competitor_keyword_freq[keyword] += 1
            # Keep the highest score seen
            if keyword not in competitor_keyword_scores or score > competitor_keyword_scores[keyword]:
                competitor_keyword_scores[keyword] = score

    # Find gaps: competitor keywords NOT in user's keywords
    gap_keywords = []
    for keyword, freq in competitor_keyword_freq.items():
        # Check if this keyword overlaps with any user keyword
        is_covered = False
        for my_kw in my_kw_lower:
            if keyword in my_kw or my_kw in keyword:
                is_covered = True
                break
            # Fuzzy match: if >70% word overlap
            kw_words = set(keyword.split())
            my_words = set(my_kw.split())
            if kw_words and my_words:
                overlap = len(kw_words & my_words) / max(len(kw_words | my_words), 1)
                if overlap > 0.6:
                    is_covered = True
                    break

        if not is_covered and competitor_keyword_scores.get(keyword, 0) >= min_score:
            gap_keywords.append({
                "keyword": keyword,
                "score": round(competitor_keyword_scores[keyword], 4),
                "competitor_frequency": freq,
                "competitors_using": freq,
                "total_competitors": len(competitor_urls),
                "opportunity_score": round(
                    (competitor_keyword_scores[keyword] * 0.4) +
                    (freq / max(len(competitor_urls), 1) * 0.6),
                    4,
                ),
            })

    # Sort by opportunity score
    gap_keywords.sort(key=lambda x: x["opportunity_score"], reverse=True)

    # Stats
    total_competitor_kw = len(competitor_keyword_freq)
    total_covered = total_competitor_kw - len(gap_keywords)

    return {
        "gap_keywords": gap_keywords,
        "total_gaps": len(gap_keywords),
        "total_competitor_keywords": total_competitor_kw,
        "total_covered": total_covered,
        "coverage_percentage": round(
            (total_covered / max(total_competitor_kw, 1)) * 100, 1
        ),
        "competitor_urls": competitor_urls,
        "stats": {
            "competitors_analyzed": len(competitor_urls),
            "total_gaps": len(gap_keywords),
            "high_opportunity": sum(1 for g in gap_keywords if g["opportunity_score"] > 0.5),
            "medium_opportunity": sum(1 for g in gap_keywords if 0.2 <= g["opportunity_score"] <= 0.5),
            "low_opportunity": sum(1 for g in gap_keywords if g["opportunity_score"] < 0.2),
        },
    }


# ──────────────────────────────────────────────
# 5. Full Content Gap Analysis Pipeline
# ──────────────────────────────────────────────


def extract_competitor_text(page_data: dict) -> str:
    """Combine page data into a single text string for keyword extraction."""
    return " ".join(filter(None, [
        page_data.get("title", ""),
        page_data.get("description", ""),
        " ".join(page_data.get("headings", {}).get("h1", [])),
        " ".join(page_data.get("headings", {}).get("h2", [])),
        " ".join(page_data.get("headings", {}).get("h3", [])),
        page_data.get("body_text", ""),
    ]))

def run_content_gap_analysis(
    seed_keyword: str,
    my_keywords: list[str] = None,
    competitor_urls: list[str] = None,
    num_serp_results: int = 5,
    max_competitors: int = 5,
    language: str = "en",
) -> dict:
    """
    Full content gap analysis pipeline.

    1. If no competitor URLs provided, discover them from SERP results.
    2. Crawl each competitor page and extract content/keywords.
    3. Compare against user's keywords to find gaps.
    4. Return comprehensive gap analysis with opportunities.

    Args:
        seed_keyword: The main keyword to analyze gaps for.
        my_keywords: User's existing keywords. If None, will be empty.
        competitor_urls: Specific competitor URLs. If None, auto-discover from SERP.
        num_serp_results: Number of SERP results to fetch for competitor discovery.
        max_competitors: Max competitor pages to analyze.

    Returns:
        Full gap analysis result dict.
    """
    if my_keywords is None:
        my_keywords = []

    result = {
        "seed": seed_keyword,
        "my_keywords_count": len(my_keywords),
        "competitors": [],
        "competitor_keywords": [],
        "gap_analysis": {},
        "errors": [],
    }

    # Step 1: Discover competitor URLs (or use provided ones)
    if not competitor_urls:
        _safe_print(f"[content_gap] Discovering competitors...")
        serp_results = get_serp_competitors(seed_keyword, num_results=num_serp_results)
        competitor_urls = [r["url"] for r in serp_results if r.get("url")][:max_competitors]
        result["serp_results"] = serp_results

    if not competitor_urls:
        result["errors"].append("No competitor URLs found")
        return result

    # Step 2: Crawl each competitor and extract keywords
    competitor_data = []
    for i, url in enumerate(competitor_urls):
        _safe_print(f"[content_gap] Analyzing competitor {i+1}/{len(competitor_urls)}: {url}")
        page_data = extract_page_content(url)

        if page_data.get("success"):
            # Extract keywords from combined content
            text_parts = [
                page_data.get("title", ""),
                page_data.get("description", ""),
                " ".join(page_data.get("headings", {}).get("h1", [])),
                " ".join(page_data.get("headings", {}).get("h2", [])),
                " ".join(page_data.get("headings", {}).get("h3", [])),
                page_data.get("body_text", ""),
            ]
            combined_text = " ".join(text_parts)

            keywords = extract_keywords_from_text(combined_text, top_n=30)

            competitor_entry = {
                "url": url,
                "success": True,
                "title": page_data.get("title", ""),
                "description": page_data.get("description", ""),
                "word_count": page_data.get("word_count", 0),
                "headings_count": sum(len(v) for v in page_data.get("headings", {}).values()),
                "keywords": keywords,
            }
            competitor_data.append(competitor_entry)
            result["competitors"].append({
                "url": url,
                "title": page_data.get("title", ""),
                "word_count": page_data.get("word_count", 0),
                "keywords_found": len(keywords),
            })

            # Rate limiting between requests
            if i < len(competitor_urls) - 1:
                time.sleep(random.uniform(1.0, 2.0))
        else:
            result["errors"].append(f"Failed to fetch {url}: {page_data.get('error', 'unknown')}")
            competitor_data.append({"url": url, "success": False, "keywords": []})

    # Step 3: Calculate content gaps
    _safe_print(f"[content_gap] Calculating gaps across {len(competitor_data)} competitors...")
    gap_result = calculate_content_gaps(my_keywords, competitor_data)
    result["gap_analysis"] = gap_result

    # Combine all competitor keywords for display
    all_competitor_kw = []
    for comp in competitor_data:
        if comp.get("success"):
            for kw in comp.get("keywords", []):
                kw["source_url"] = comp["url"]
                all_competitor_kw.append(kw)
    result["competitor_keywords"] = sorted(
        all_competitor_kw, key=lambda x: x.get("score", 0), reverse=True
    )[:50]

    # Summary stats
    result["summary"] = {
        "seed": seed_keyword,
        "competitors_analyzed": len([c for c in competitor_data if c.get("success")]),
        "total_competitor_keywords": gap_result.get("total_competitor_keywords", 0),
        "total_gaps": gap_result.get("total_gaps", 0),
        "coverage_percentage": gap_result.get("coverage_percentage", 0),
        "high_opportunity_gaps": gap_result.get("stats", {}).get("high_opportunity", 0),
    }

    return result
