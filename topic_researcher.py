"""
Rankivo — Topic Researcher
Searches the internet, extracts content from top-ranking pages,
and compiles research insights to feed into article generation.
"""
import time
import random
import re
import requests
from collections import Counter
from config import REQUEST_TIMEOUT, USER_AGENTS, _safe_print, suppress_output, random_ua




# ──────────────────────────────────────────────
# Research Cache (avoids re-fetching same topic)
# ──────────────────────────────────────────────

_research_cache: dict[str, dict] = {}
_MAX_CACHE_SIZE = 50


def get_cached_research(topic: str) -> dict | None:
    """Get cached research for a topic, or None if not cached."""
    return _research_cache.get(topic.lower().strip())


def _cache_research(topic: str, result: dict) -> None:
    """Cache a research result."""
    key = topic.lower().strip()
    if len(_research_cache) >= _MAX_CACHE_SIZE:
        oldest_key = next(iter(_research_cache))
        _research_cache.pop(oldest_key, None)
    _research_cache[key] = result


def clear_research_cache() -> None:
    """Clear the research cache."""
    _research_cache.clear()


# ──────────────────────────────────────────────
# 1. SERP Search — find top results for a topic
# ──────────────────────────────────────────────

def search_google(query: str, num_results: int = 8) -> list[dict]:
    """Search Google and return top results with titles, URLs, and snippets."""
    try:
        from googlesearch import search as gsearch
        results = []
        with suppress_output():
            for r in gsearch(query, num_results=num_results, advanced=True):
                url = getattr(r, "url", "")
                if url and not any(blocked in url for blocked in [
                    "google.com/search", "youtube.com/results",
                    "pinterest.com", "facebook.com", "twitter.com",
                    "instagram.com", "tiktok.com",
                ]):
                    results.append({
                        "title": getattr(r, "title", ""),
                        "url": url,
                        "snippet": getattr(r, "description", ""),
                    })
        return results
    except Exception as e:
        _safe_print(f"[topic_researcher] Google search error: {e}")
        return []


# ──────────────────────────────────────────────
# 2. Page Content Extraction
# ──────────────────────────────────────────────

def extract_page_content(url: str) -> dict:
    """Fetch a page and extract structured content."""
    try:
        headers = {"User-Agent": random_ua()}
        resp = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT, allow_redirects=True)
        resp.raise_for_status()

        from bs4 import BeautifulSoup
        soup = BeautifulSoup(resp.text, "lxml")

        title_tag = soup.find("title")
        title = title_tag.get_text(strip=True) if title_tag else ""

        meta_desc = soup.find("meta", attrs={"name": "description"})
        description = meta_desc.get("content", "").strip() if meta_desc else ""

        headings = {}
        for level in ["h1", "h2", "h3", "h4"]:
            tags = soup.find_all(level)
            headings[level] = [t.get_text(strip=True) for t in tags if t.get_text(strip=True)]

        for tag in soup.find_all(["nav", "footer", "header", "script", "style", "noscript", "aside"]):
            tag.decompose()

        main_content = soup.find("main") or soup.find("article") or soup.find("body")
        body_text = main_content.get_text(separator=" ", strip=True) if main_content else ""

        lists = []
        if main_content:
            for li in main_content.find_all(["ol", "ul"]):
                items = [li.get_text(strip=True) for li in li.find_all("li") if li.get_text(strip=True)]
                if items:
                    lists.append(items[:10])

        tables = []
        if main_content:
            for table in main_content.find_all("table")[:3]:
                rows = []
                for tr in table.find_all("tr")[:10]:
                    cells = [td.get_text(strip=True) for td in tr.find_all(["td", "th"])]
                    if cells:
                        rows.append(cells)
                if rows:
                    tables.append(rows)

        word_count = len(body_text.split())

        return {
            "url": url,
            "title": title,
            "description": description,
            "headings": headings,
            "body_text": body_text[:15000],
            "word_count": word_count,
            "lists": lists,
            "tables": tables,
            "success": True,
        }
    except Exception as e:
        _safe_print(f"[topic_researcher] Extract error for {url}: {e}")
        return {"url": url, "success": False, "error": str(e)}


# ──────────────────────────────────────────────
# 3. Key Facts & Statistics Extraction
# ──────────────────────────────────────────────

def extract_key_facts(text: str) -> list[str]:
    """Extract factual statements, statistics, and key claims from text."""
    facts = []
    patterns = [
        r'\d+[\.,]?\d*\s*(?:%|percent|million|billion|thousand|trillion)',
        r'(?:according to|research shows|studies show|data indicates|reports show)[^.]*\.',
        r'(?:is defined as|refers to|means that)[^.]*\.',
        r'(?:benefit|advantage|feature|reason|cause|effect)[^.]*\.',
        r'(?:must|should|need to|important to|essential to)[^.]*\.',
        r'(?:in \d{4}|since \d{4}|by \d{4})[^.]*\.',
        r'(?:price|cost|revenue|growth|increase|decrease)[^.]*\.',
    ]
    sentences = re.split(r'(?<=[.!?])\s+', text)
    for sent in sentences:
        sent = sent.strip()
        if len(sent) < 20 or len(sent) > 300:
            continue
        for pattern in patterns:
            if re.search(pattern, sent, re.IGNORECASE):
                facts.append(sent)
                break
    seen = set()
    unique_facts = []
    for f in facts:
        normalized = f[:80].lower()
        if normalized not in seen:
            seen.add(normalized)
            unique_facts.append(f)
    return unique_facts[:15]


# ──────────────────────────────────────────────
# 4. Content Gap Identification
# ──────────────────────────────────────────────

def identify_content_gaps(topic: str, competitor_headings: list[str], user_keywords: list[str] = None, language: str = "en") -> list[str]:
    """Identify angles and subtopics competitors cover that could be expanded upon."""
    gaps = []

    if language == "fa":
        subtopic_hints = {
            "guide": ["شروع", "قدم به قدم", "نحوه", "آموزش", "مبتدی"],
            "comparison": ["مقایسه", "تفاوت", "جایگزین", "در مقابل"],
            "deep_dive": ["تعریف", "معنی", "چیست", "مرور"],
            "practical": ["مثال", "نمونه", "بهترین روش", "نکته", "کاربرد"],
            "advanced": ["پیشرفته", "حرفه‌ای", "استراتژی", "بهینه‌سازی"],
            "problems": ["مشکل", "خطا", "چالش", "اشتباه", "پرهیز"],
            "future": ["آینده", "ترند", "پیش‌بینی", "۱۴۰۵", "۱۴۰۶"],
            "resources": ["ابزار", "نرم‌افزار", "پلتفرم", "قالب", "چک‌لیست"],
        }
        all_headings_lower = " ".join(competitor_headings).lower()
        for category, hints in subtopic_hints.items():
            covered = any(hint in all_headings_lower for hint in hints)
            if not covered:
                gaps.append(f"زیرموضوع گمشده: {category} (رقیبان این بخش را پوشش نداده‌اند)")
    else:
        subtopic_hints = {
            "guide": ["getting started", "step by step", "how to", "tutorial", "beginner"],
            "comparison": ["vs", "comparison", "alternative", "difference between"],
            "deep_dive": ["explained", "definition", "meaning", "what is", "overview"],
            "practical": ["example", "case study", "use case", "best practice", "tip"],
            "advanced": ["advanced", "pro tips", "expert", "strategy", "optimization"],
            "problems": ["problem", "issue", "challenge", "mistake", "pitfall", "avoid"],
            "future": ["future", "trend", "prediction", "2025", "2026", "upcoming"],
            "resources": ["tool", "software", "platform", "resource", "template", "checklist"],
        }
        all_headings_lower = " ".join(competitor_headings).lower()
        for category, hints in subtopic_hints.items():
            covered = any(hint in all_headings_lower for hint in hints)
            if not covered:
                gaps.append(f"Missing subtopic: {category} angle (competitors don't cover this well)")
    return gaps[:8]


# ──────────────────────────────────────────────
# 5. Full Research Pipeline
# ──────────────────────────────────────────────

def research_topic(
    topic: str,
    target_keywords: list[str] = None,
    language: str = "en",
    num_results: int = 6,
) -> dict:
    """
    Full topic research pipeline with caching:
    1. Check cache first
    2. Search Google for the topic
    3. Fetch and analyze top-ranking pages
    4. Extract key facts, headings, content structure
    5. Identify content gaps and unique angles
    """
    if target_keywords is None:
        target_keywords = []

    # Check cache first
    cached = get_cached_research(topic)
    if cached is not None:
        _safe_print(f"[topic_researcher] Using cached research for '{topic}'")
        return cached

    research = {
        "topic": topic,
        "language": language,
        "search_results": [],
        "competitor_analysis": [],
        "key_facts": [],
        "top_headings": [],
        "content_gaps": [],
        "recommended_structure": [],
        "research_summary": "",
    }

    # Step 1: Search Google
    _safe_print(f"[topic_researcher] Searching Google for '{topic}'...")
    serp_results = search_google(topic, num_results=num_results)
    research["search_results"] = serp_results

    if not serp_results:
        research["research_summary"] = "No search results found. Article will be based on provided keywords only."
        _cache_research(topic, research)
        return research

    # Step 2: Fetch and analyze top pages
    _safe_print(f"[topic_researcher] Analyzing {len(serp_results)} top results...")
    all_headings = []
    all_facts = []
    all_body_texts = []

    for i, result in enumerate(serp_results[:5]):
        url = result.get("url", "")
        if not url:
            continue

        _safe_print(f"[topic_researcher]   [{i+1}/5] Fetching: {url[:80]}...")
        page = extract_page_content(url)

        if page.get("success"):
            research["competitor_analysis"].append({
                "url": url,
                "title": page.get("title", ""),
                "description": page.get("description", ""),
                "word_count": page.get("word_count", 0),
                "h1": page.get("headings", {}).get("h1", []),
                "h2": page.get("headings", {}).get("h2", []),
                "h3": page.get("headings", {}).get("h3", []),
                "has_lists": len(page.get("lists", [])) > 0,
                "has_tables": len(page.get("tables", [])) > 0,
            })

            for level in ["h1", "h2", "h3"]:
                all_headings.extend(page.get("headings", {}).get(level, []))

            facts = extract_key_facts(page.get("body_text", ""))
            all_facts.extend(facts)

            body = page.get("body_text", "")
            if body:
                all_body_texts.append(body[:3000])

        if i < len(serp_results) - 1:
            time.sleep(random.uniform(0.8, 1.5))

    # Step 3: Consolidate findings
    seen_headings = set()
    unique_headings = []
    for h in all_headings:
        h_lower = h.lower().strip()
        if h_lower not in seen_headings and len(h_lower) > 5:
            seen_headings.add(h_lower)
            unique_headings.append(h)
    research["top_headings"] = unique_headings[:30]

    seen_facts = set()
    unique_facts = []
    for f in all_facts:
        f_key = f[:60].lower()
        if f_key not in seen_facts:
            seen_facts.add(f_key)
            unique_facts.append(f)
    research["key_facts"] = unique_facts[:20]

    # Step 4: Identify content gaps
    research["content_gaps"] = identify_content_gaps(
        topic, unique_headings, target_keywords, language=language
    )

    # Step 5: Recommend article structure
    avg_word_count = 0
    if research["competitor_analysis"]:
        word_counts = [c.get("word_count", 0) for c in research["competitor_analysis"]]
        valid_wc = [wc for wc in word_counts if wc > 0]
        avg_word_count = sum(valid_wc) // max(len(valid_wc), 1)

    h2_counts = Counter()
    for comp in research["competitor_analysis"]:
        for h2 in comp.get("h2", []):
            h2_lower = h2.lower().strip()
            h2_counts[h2_lower] += 1

    common_h2_patterns = h2_counts.most_common(10)

    research["recommended_structure"] = {
        "suggested_word_count": max(avg_word_count, 1500),
        "competitor_avg_word_count": avg_word_count,
        "common_h2_patterns": [h for h, c in common_h2_patterns],
        "has_lists_in_competitors": any(c.get("has_lists") for c in research["competitor_analysis"]),
        "has_tables_in_competitors": any(c.get("has_tables") for c in research["competitor_analysis"]),
    }

    num_competitors = len(research["competitor_analysis"])
    num_facts = len(research["key_facts"])
    num_gaps = len(research["content_gaps"])

    if language == "fa":
        research["research_summary"] = (
            f"تحقیق روی {num_competitors} صفحه برتر برای '{topic}' انجام شد. "
            f"{num_facts} واقعیت/آمار کلیدی، {len(unique_headings)} تیتر یکتا، "
            f"و {num_gaps} شکاف محتوایی شناسایی شد. "
            f"میانگین تعداد کلمات رقیبان: {avg_word_count}."
        )
    else:
        research["research_summary"] = (
            f"Researched {num_competitors} top-ranking pages for '{topic}'. "
            f"Found {num_facts} key facts/statistics, {len(unique_headings)} unique headings, "
            f"and {num_gaps} content gaps to exploit. "
            f"Competitor average word count: {avg_word_count}."
        )

    _safe_print(f"[topic_researcher] {research['research_summary']}")

    # Cache the result
    _cache_research(topic, research)

    return research
