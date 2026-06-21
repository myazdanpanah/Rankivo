"""
SEO AI Tools - LLM-Powered Keyword Intelligence
Uses local LLM (Ollama) for intent classification, semantic clustering via embeddings,
and keyword difficulty estimation via SERP analysis.

Requires:
  - Ollama with qwen2.5 model (for intent classification & difficulty)
  - Ollama with nomic-embed-text model (for semantic embeddings)
  - scikit-learn (for K-Means clustering)
"""
import json
import re
import time
import random
import requests
import numpy as np
from typing import Optional
from difflib import SequenceMatcher

from config import (
    OLLAMA_BASE_URL, OLLAMA_MODEL, REQUEST_TIMEOUT,
    EMBEDDING_MODEL, LLM_INTENT_CLASSIFICATION, SEMANTIC_CLUSTERING,
)
from keyword_research import classify_intent as _heuristic_intent


# ──────────────────────────────────────────────
# Ollama Helpers
# ──────────────────────────────────────────────


def _check_ollama() -> bool:
    """Check if Ollama is running and accessible."""
    try:
        resp = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=3)
        return resp.status_code == 200
    except Exception:
        return False


def _ollama_generate(prompt: str, system: str = "", model: str = "") -> str:
    """Call Ollama's generate endpoint."""
    if not model:
        model = OLLAMA_MODEL
    payload = {
        "model": model,
        "prompt": prompt,
        "system": system,
        "stream": False,
    }
    resp = requests.post(
        f"{OLLAMA_BASE_URL}/api/generate",
        json=payload,
        timeout=120,
    )
    resp.raise_for_status()
    return resp.json()["response"]


_cached_embedding_model: str | None = None


def _check_embedding_model() -> str:
    """Find the best available embedding model. Returns model name or empty string."""
    global _cached_embedding_model
    if _cached_embedding_model is not None:
        return _cached_embedding_model
    try:
        resp = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        if resp.status_code == 200:
            models = [m["name"] for m in resp.json().get("models", [])]
            for preferred in [EMBEDDING_MODEL, "nomic-embed-text", "mxbai-embed-large", "all-minilm"]:
                for m in models:
                    if preferred in m:
                        _cached_embedding_model = m
                        return m
    except Exception:
        pass
    _cached_embedding_model = ""
    return ""


def _ollama_embeddings(texts: list[str], model: str = "") -> list[list[float]]:
    """Get embeddings for a list of texts using Ollama's embedding endpoint.
    Falls back to TF-IDF vectorizer if no embedding model is available."""
    if not model:
        model = _check_embedding_model()
    
    if not model:
        print("[llm_intel] No embedding model available, using TF-IDF fallback")
        return _tfidf_embeddings(texts)
    
    embeddings = []
    for text in texts:
        try:
            resp = requests.post(
                f"{OLLAMA_BASE_URL}/api/embeddings",
                json={"model": model, "prompt": text},
                timeout=30,
            )
            resp.raise_for_status()
            embeddings.append(resp.json()["embedding"])
        except Exception as e:
            print(f"[llm_intel] Embedding error for '{text[:50]}': {e}")
            embeddings.append([0.0] * 768)
    return embeddings


def _tfidf_embeddings(texts: list[str], max_features: int = 256) -> list[list[float]]:
    """Generate TF-IDF based embeddings as fallback when no LLM embedding model is available.
    Uses character n-grams for multilingual support (works with Persian/Farsi)."""
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.preprocessing import normalize
    
    if not texts:
        return []
    
    # Use character n-grams (2-4) for multilingual support
    vectorizer = TfidfVectorizer(
        analyzer='char',
        ngram_range=(2, 4),
        max_features=max_features,
        sublinear_tf=True,
    )
    try:
        tfidf_matrix = vectorizer.fit_transform(texts)
        # Normalize to unit vectors for cosine similarity
        normalized = normalize(tfidf_matrix, norm='l2')
        return normalized.toarray().tolist()
    except Exception as e:
        print(f"[llm_intel] TF-IDF fallback error: {e}")
        return [[0.0] * max_features for _ in texts]


# ──────────────────────────────────────────────
# 1. LLM-Powered Intent Classification
# ──────────────────────────────────────────────

INTENT_SYSTEM_PROMPT = """You are an SEO keyword intent classifier. Classify the given keyword into exactly ONE of these categories:
- informational: The user wants to learn something (how, what, why, guide, tutorial, definition)
- transactional: The user wants to buy/download/subscribe (buy, price, cheap, deal, download, order)
- navigational: The user wants to find a specific website/brand (login, official, website, app, brand names)
- commercial: The user is comparing options before buying (best, top, review, vs, comparison, alternative, compare)

Rules:
- Respond with ONLY the category name, nothing else.
- If unsure, default to "informational".
- For Persian/Farsi keywords, translate mentally and classify based on meaning.
- Consider cultural context (e.g., "خرید" = buy = transactional, "آموزش" = tutorial = informational)."""

# Persian-specific few-shot prompt for better accuracy
INTENT_SYSTEM_PROMPT_FA = """You are an SEO keyword intent classifier. Classify the given Persian/Farsi keyword into exactly ONE of these categories:
- informational: کاربر می‌خواهد چیزی یاد بگیرد (آموزش، راهنما، چیست، نحوه)
- transactional: کاربر می‌خواهد خرید/دانلود/عضویت کند (خرید، قیمت، ارزان، دانلود)
- navigational: کاربر می‌خواهد سایت/برند خاصی را پیدا کند (ورود، سایت رسمی، اپلیکیشن)
- commercial: کاربر در حال مقایسه گزینه‌ها قبل از خرید است (بهترین، مقایسه، نقد، بررسی)

Examples:
- "خرید لپتاپ ارزان" → transactional
- "آموزش پایتون" → informational
- "ورود به جیمیل" → navigational
- "بهترین گوشی ۲۰۲۶" → commercial
- "نحوه نصب ویندوز" → informational
- "قیمت آیفون" → transactional

Rules:
- Respond with ONLY the category name, nothing else.
- If unsure, default to "informational"."""


def _normalize_persian(text: str) -> str:
    """Normalize Persian text for consistent processing."""
    try:
        from hazm import Normalizer
        normalizer = Normalizer()
        return normalizer.normalize(text)
    except ImportError:
        # Basic normalization without hazm
        text = text.replace('ي', 'ی').replace('ك', 'ک')
        text = text.replace('ؤ', 'و').replace('إ', 'ا').replace('أ', 'ا')
        return text


def _is_persian(text: str) -> bool:
    """Check if text contains Persian characters."""
    persian_range = range(0x0600, 0x06FF + 1)
    arabic_range = range(0xFB50, 0xFDFF + 1)
    extended_arabic = range(0xFE70, 0xFEFF + 1)
    persian_count = sum(1 for c in text if ord(c) in persian_range or ord(c) in arabic_range or ord(c) in extended_arabic)
    return persian_count > len(text) * 0.3


def classify_intent_llm(keyword: str, model: str = "") -> str:
    """
    Classify search intent for a single keyword using LLM.
    Falls back to heuristic if LLM is unavailable.
    """
    if not _check_ollama():
        return _classify_intent_heuristic(keyword)

    try:
        # Use Persian-specific prompt for Persian keywords
        is_fa = _is_persian(keyword)
        system_prompt = INTENT_SYSTEM_PROMPT_FA if is_fa else INTENT_SYSTEM_PROMPT
        normalized_kw = _normalize_persian(keyword) if is_fa else keyword
        
        result = _ollama_generate(
            prompt=f"Classify this keyword: \"{normalized_kw}\"",
            system=system_prompt,
            model=model or OLLAMA_MODEL,
        ).strip().lower()

        # Validate response
        valid_intents = {"informational", "transactional", "navigational", "commercial"}
        for intent in valid_intents:
            if intent in result:
                return intent
        return "informational"
    except Exception as e:
        print(f"[llm_intel] Intent classification error: {e}")
        return _classify_intent_heuristic(keyword)


def classify_intents_batch(keywords: list[str], model: str = "", batch_size: int = 10) -> dict[str, str]:
    """
    Classify intent for multiple keywords efficiently.
    Uses batch prompting to reduce API calls.
    Returns dict mapping keyword -> intent.
    """
    if not keywords:
        return {}

    if not _check_ollama():
        return {kw: _classify_intent_heuristic(kw) for kw in keywords}

    results = {}

    # Detect if batch is predominantly Persian - split mixed batches
    persian_kws = [kw for kw in keywords if _is_persian(kw)]
    english_kws = [kw for kw in keywords if not _is_persian(kw)]
    
    # Process Persian and English keywords separately if batch is mixed
    all_results = {}
    if persian_kws and english_kws:
        all_results.update(classify_intents_batch(persian_kws, model=model, batch_size=batch_size))
        all_results.update(classify_intents_batch(english_kws, model=model, batch_size=batch_size))
        return all_results
    
    is_fa_batch = len(persian_kws) > 0
    
    # Process in batches to reduce API calls
    for i in range(0, len(keywords), batch_size):
        batch = keywords[i:i + batch_size]
        normalized_batch = [_normalize_persian(kw) if _is_persian(kw) else kw for kw in batch]
        batch_text = "\n".join(f"{j + 1}. \"{kw}\"" for j, kw in enumerate(normalized_batch))

        if is_fa_batch:
            prompt = f"""هر یک از کلمات کلیدی زیر را در یکی از دسته‌بندی‌های زیر طبقه‌بندی کنید:
informational, transactional, navigational, commercial

کلمات کلیدی:
{batch_text}

یک شیء JSON برگردانید که شماره هر کلمه کلیدی را به intent آن نگاشت کند.
فرمت مثال:
{{"1": "informational", "2": "transactional"}}

فقط شیء JSON را برگردانید، بدون متن اضافی."""
        else:
            prompt = f"""Classify each of these keywords into one of: informational, transactional, navigational, commercial.

Keywords:
{batch_text}

Return a JSON object mapping each keyword number to its intent. Example format:
{{"1": "informational", "2": "transactional"}}

Return ONLY the JSON object, no other text."""

        try:
            response = _ollama_generate(
                prompt=prompt,
                system=INTENT_SYSTEM_PROMPT,
                model=model or OLLAMA_MODEL,
            ).strip()

            # Extract JSON from response
            json_match = re.search(r'\{[^}]+\}', response, re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group())
                for j, kw in enumerate(batch):
                    key = str(j + 1)
                    intent = parsed.get(key, "informational")
                    if intent in {"informational", "transactional", "navigational", "commercial"}:
                        results[kw] = intent
                    else:
                        results[kw] = _classify_intent_heuristic(kw)
            else:
                # Fallback to individual classification
                for kw in batch:
                    results[kw] = classify_intent_llm(kw, model)
        except Exception as e:
            print(f"[llm_intel] Batch classification error: {e}")
            for kw in batch:
                results[kw] = _classify_intent_heuristic(kw)

        # Small delay between batches
        if i + batch_size < len(keywords):
            time.sleep(0.5)

    return results


def _classify_intent_heuristic(keyword: str) -> str:
    """Fallback heuristic intent classifier with Persian support.
    Extends the base heuristic from keyword_research.py."""
    # First try the base English heuristic
    base = _heuristic_intent(keyword)
    if base != "informational":
        return base

    # Extended Persian signals
    kw = keyword.lower()

    transactional_fa = ["خرید", "قیمت", "ارزان", "تخفیف", "سفارش", "دانلود"]
    if any(s in kw for s in transactional_fa):
        return "transactional"

    navigational_fa = ["ورود", "سایت رسمی", "اپلیکیشن"]
    if any(s in kw for s in navigational_fa):
        return "navigational"

    commercial_fa = ["بهترین", "مقایسه", "نقد", "بررسی", "جایگزین"]
    if any(s in kw for s in commercial_fa):
        return "commercial"

    informational_fa = ["آموزش", "چیست", "راهنما", "نحوه", "تعریف"]
    if any(s in kw for s in informational_fa):
        return "informational"

    return "informational"


# ──────────────────────────────────────────────
# 2. Semantic Embedding Clustering
# ──────────────────────────────────────────────

def compute_embeddings(keywords: list[str], model: str = "") -> np.ndarray:
    """
    Compute semantic embeddings for a list of keywords.
    Returns numpy array of shape (n_keywords, embedding_dim).
    """
    if not keywords:
        return np.array([])

    if not model:
        model = EMBEDDING_MODEL
    print(f"[llm_intel] Computing embeddings for {len(keywords)} keywords using {model}...")
    embeddings_list = _ollama_embeddings(keywords, model=model)
    return np.array(embeddings_list)


def cluster_keywords_semantic(
    keywords: list[str],
    n_clusters: int = 0,
    max_clusters: int = 20,
    min_cluster_size: int = 2,
) -> list[dict]:
    """
    Cluster keywords using semantic embeddings + K-Means.

    Args:
        keywords: List of keyword strings
        n_clusters: Number of clusters (0 = auto-determine)
        max_clusters: Maximum number of clusters when auto-determining
        min_cluster_size: Minimum keywords per cluster

    Returns:
        List of dicts: {cluster_id, topic, keywords, centroid_keyword}
    """
    from sklearn.cluster import KMeans
    from sklearn.metrics import silhouette_score

    if len(keywords) < 2:
        return [{"cluster_id": 0, "topic": keywords[0] if keywords else "", "keywords": keywords}]

    # Compute embeddings
    embeddings = compute_embeddings(keywords)

    # Filter out zero vectors (failed embeddings)
    valid_mask = np.any(embeddings != 0, axis=1)
    if valid_mask.sum() < 2:
        # Fallback to word-overlap clustering
        return _fallback_cluster(keywords)

    valid_embeddings = embeddings[valid_mask]
    valid_keywords = [kw for kw, v in zip(keywords, valid_mask) if v]
    invalid_keywords = [kw for kw, v in zip(keywords, valid_mask) if not v]

    # Auto-determine optimal number of clusters
    if n_clusters <= 0:
        n_clusters = _find_optimal_clusters(valid_embeddings, max_k=min(max_clusters, len(valid_keywords) - 1))

    # Ensure we don't have more clusters than keywords
    n_clusters = min(n_clusters, len(valid_keywords))

    if n_clusters < 2:
        # Everything belongs to one cluster
        return [{"cluster_id": 0, "topic": valid_keywords[0], "keywords": valid_keywords + invalid_keywords}]

    # Run K-Means
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10, max_iter=300)
    labels = kmeans.fit_predict(valid_embeddings)

    # Build clusters
    clusters = {}
    for kw, label in zip(valid_keywords, labels):
        label = int(label)
        if label not in clusters:
            clusters[label] = []
        clusters[label].append(kw)

    # Add invalid keywords to nearest cluster
    if invalid_keywords:
        # Put them in the largest cluster
        largest = max(clusters.keys(), key=lambda k: len(clusters[k]))
        clusters[largest].extend(invalid_keywords)

    # Filter small clusters and reassign their keywords
    result = []
    orphans = []
    for label in sorted(clusters.keys()):
        kws = clusters[label]
        if len(kws) < min_cluster_size:
            orphans.extend(kws)
        else:
            result.append(kws)

    # Distribute orphans to nearest cluster
    if orphans and result:
        for kw in orphans:
            result[0].append(kw)  # Put in first (largest) cluster

    # Build final output
    output = []
    for i, kws in enumerate(sorted(result, key=len, reverse=True)):
        # Find the keyword closest to the centroid as the "topic"
        centroid = kmeans.cluster_centers_[i] if i < len(kmeans.cluster_centers_) else None
        topic = _find_closest_keyword(centroid, kws, valid_keywords, valid_embeddings, valid_mask, keywords)

        output.append({
            "cluster_id": i,
            "topic": topic,
            "keywords": kws,
            "size": len(kws),
        })

    return output


def _find_optimal_clusters(embeddings: np.ndarray, max_k: int = 15) -> int:
    """Find optimal number of clusters using silhouette score."""
    from sklearn.cluster import KMeans
    from sklearn.metrics import silhouette_score

    if len(embeddings) <= 2:
        return min(len(embeddings), 2)

    best_score = -1
    best_k = 2

    max_k = min(max_k, len(embeddings) - 1)
    for k in range(2, max_k + 1):
        try:
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=5, max_iter=100)
            labels = kmeans.fit_predict(embeddings)
            score = silhouette_score(embeddings, labels)
            if score > best_score:
                best_score = score
                best_k = k
        except Exception:
            continue

    return best_k


def _find_closest_keyword(centroid, cluster_keywords, all_keywords, all_embeddings, valid_mask, original_keywords):
    """Find the keyword in the cluster closest to the centroid."""
    if centroid is None:
        return cluster_keywords[0]

    # Build a dict for O(1) lookup instead of O(n) .index()
    kw_to_idx = {kw: i for i, kw in enumerate(all_keywords)}

    best_kw = cluster_keywords[0]
    best_dist = float("inf")

    for kw in cluster_keywords:
        idx = kw_to_idx.get(kw)
        if idx is not None and idx < len(all_embeddings):
            dist = np.linalg.norm(all_embeddings[idx] - centroid)
            if dist < best_dist:
                best_dist = dist
                best_kw = kw

    return best_kw


def _fallback_cluster(keywords: list[str], threshold: float = 0.35) -> list[dict]:
    """Fallback clustering using word overlap when embeddings fail."""
    from pillar_cluster import group_keywords_into_clusters
    clusters = group_keywords_into_clusters(keywords, threshold=threshold)
    return [
        {"cluster_id": c["cluster_id"], "topic": c["topic"], "keywords": c["keywords"], "size": len(c["keywords"])}
        for c in clusters
    ]


# ──────────────────────────────────────────────
# 3. Keyword Difficulty Estimation
# ──────────────────────────────────────────────

def _get_serper_results(query: str, num: int = 10) -> list[dict]:
    """
    Get SERP results using Serper.dev API if configured,
    otherwise fall back to googlesearch-python.
    """
    import os
    serper_key = os.getenv("SERPER_API_KEY", "")

    if serper_key:
        return _get_serper_api(query, serper_key, num)
    else:
        return _get_serper_fallback(query, num)


def _get_serper_api(query: str, api_key: str, num: int = 10) -> list[dict]:
    """Use Serper.dev API for SERP data."""
    try:
        resp = requests.post(
            "https://google.serper.dev/search",
            headers={"X-API-KEY": api_key, "Content-Type": "application/json"},
            json={"q": query, "num": num},
            timeout=REQUEST_TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()
        results = []
        for r in data.get("organic", []):
            results.append({
                "title": r.get("title", ""),
                "url": r.get("link", ""),
                "snippet": r.get("snippet", ""),
                "position": r.get("position", 0),
                "domain_rating": r.get("domainRating", 0),
            })
        return results
    except Exception as e:
        print(f"[llm_intel] Serper API error: {e}")
        return []


def _get_serper_fallback(query: str, num: int = 10) -> list[dict]:
    """Fallback SERP scraping using googlesearch-python."""
    try:
        from googlesearch import search as gsearch
        results = []
        for r in gsearch(query, num_results=num, advanced=True):
            results.append({
                "title": getattr(r, "title", ""),
                "url": getattr(r, "url", ""),
                "snippet": getattr(r, "description", ""),
                "position": len(results) + 1,
                "domain_rating": 0,
            })
        return results
    except Exception as e:
        print(f"[llm_intel] SERP fallback error: {e}")
        return []


def _extract_domain_info(url: str) -> dict:
    """Extract domain-level signals from a URL."""
    from urllib.parse import urlparse
    parsed = urlparse(url)
    domain = parsed.netloc.lower()

    # Common high-authority domains
    high_authority = [
        "wikipedia.org", "youtube.com", "reddit.com", "stackoverflow.com",
        "github.com", "medium.com", "quora.com", "amazon.com",
    ]
    medium_authority = [
        "wordpress.com", "blogspot.com", "tumblr.com", "substack.com",
    ]

    is_high = any(d in domain for d in high_authority)
    is_medium = any(d in domain for d in medium_authority)
    is_gov = domain.endswith(".gov") or domain.endswith(".edu")
    is_org = domain.endswith(".org")

    tld = domain.split(".")[-1] if "." in domain else ""

    return {
        "is_high_authority": is_high,
        "is_medium_authority": is_medium,
        "is_gov_edu": is_gov,
        "is_org": is_org,
        "tld": tld,
        "domain": domain,
    }


def estimate_keyword_difficulty_llm(keyword: str, serp_results: list[dict] | None = None, model: str = "") -> dict:
    """
    Estimate keyword difficulty using LLM analysis of SERP results.

    Returns dict with:
      - score: 0-100 difficulty score
      - level: "easy", "medium", "hard", "very_hard"
      - factors: list of contributing factors
      - recommendation: strategy recommendation
    """
    # Fetch SERP results if not provided
    if serp_results is None:
        serp_results = _get_serper_results(keyword)

    if not serp_results:
        return {
            "score": 50,
            "level": "medium",
            "factors": ["No SERP data available"],
            "recommendation": "Unable to estimate — no search results found.",
        }

    # Analyze domain signals
    domain_signals = [_extract_domain_info(r["url"]) for r in serp_results[:10]]
    high_auth_count = sum(1 for d in domain_signals if d["is_high_authority"])
    gov_edu_count = sum(1 for d in domain_signals if d["is_gov_edu"])

    # Calculate base score from signals (lower = easier)
    base_score = 30  # Start at 30
    base_score += high_auth_count * 8  # Each high-authority domain adds difficulty
    base_score += gov_edu_count * 10  # Government/educational sites are harder to outrank
    base_score = min(base_score, 85)  # Cap at 85 before LLM analysis

    # Use LLM to analyze SERP quality
    if _check_ollama() and serp_results:
        try:
            serp_summary = "\n".join(
                f"  {i+1}. {r['title']} — {r['url']} — {r['snippet'][:150]}"
                for i, r in enumerate(serp_results[:10])
            )

            prompt = f"""Analyze the top 10 Google search results for the keyword "{keyword}" and estimate the keyword difficulty.

Top Results:
{serp_summary}

Based on these results, provide:
1. A difficulty score from 0-100 (0=easiest, 100=hardest)
2. A level: "easy" (0-30), "medium" (31-60), "hard" (61-80), or "very_hard" (81-100)
3. 2-3 key factors that make this keyword easy or hard
4. A brief strategy recommendation

Respond in JSON format ONLY:
{{"score": <number>, "level": "<string>", "factors": ["factor1", "factor2"], "recommendation": "<string>"}}"""

            response = _ollama_generate(
                prompt=prompt,
                system="You are an SEO keyword difficulty analyst. Analyze search results and provide accurate difficulty estimates. Respond ONLY in JSON format.",
                model=model or OLLAMA_MODEL,
            ).strip()

            # Parse JSON response
            json_match = re.search(r'\{[^}]+\}', response, re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group())
                llm_score = int(parsed.get("score", base_score))
                # Blend LLM score with signal-based score
                final_score = int(0.6 * llm_score + 0.4 * base_score)
                final_score = max(0, min(100, final_score))

                level = parsed.get("level", _score_to_level(final_score))
                factors = parsed.get("factors", [])
                recommendation = parsed.get("recommendation", "")

                # Add domain signal factors
                if high_auth_count > 3:
                    factors.append(f"{high_auth_count} high-authority domains in top results")
                if gov_edu_count > 0:
                    factors.append(f"{gov_edu_count} government/educational sites ranking")

                return {
                    "score": final_score,
                    "level": level,
                    "factors": factors[:5],
                    "recommendation": recommendation,
                    "serp_count": len(serp_results),
                    "high_authority_domains": high_auth_count,
                    "gov_edu_domains": gov_edu_count,
                }
        except Exception as e:
            print(f"[llm_intel] LLM difficulty analysis error: {e}")

    # Fallback: signal-based estimation only
    return {
        "score": base_score,
        "level": _score_to_level(base_score),
        "factors": _get_signal_factors(domain_signals, high_auth_count, gov_edu_count),
        "recommendation": _get_recommendation(base_score),
        "serp_count": len(serp_results),
        "high_authority_domains": high_auth_count,
        "gov_edu_domains": gov_edu_count,
    }


def _score_to_level(score: int) -> str:
    """Convert numeric score to level string."""
    if score <= 30:
        return "easy"
    elif score <= 60:
        return "medium"
    elif score <= 80:
        return "hard"
    return "very_hard"


def _get_signal_factors(domain_signals: list[dict], high_auth: int, gov_edu: int) -> list[str]:
    """Generate factor descriptions from domain signals."""
    factors = []
    if high_auth > 3:
        factors.append(f"High competition: {high_auth} authoritative domains in top results")
    if gov_edu > 0:
        factors.append(f"{gov_edu} government/educational sites ranking")
    total = len(domain_signals)
    unique_domains = len(set(d["domain"] for d in domain_signals))
    if unique_domains == total:
        factors.append("Diverse competition — many different sites ranking")
    if unique_domains < total * 0.5:
        factors.append("Low diversity — few domains dominate the SERP")
    if not factors:
        factors.append("Mixed competition signals")
    return factors


def _get_recommendation(score: int) -> str:
    """Get strategy recommendation based on difficulty score."""
    if score <= 20:
        return "Low difficulty — write a comprehensive article targeting this keyword for quick ranking gains."
    elif score <= 40:
        return "Moderate difficulty — create a well-structured piece with unique angles and internal links."
    elif score <= 60:
        return "Medium difficulty — build supporting cluster content first, then target this as a pillar page."
    elif score <= 80:
        return "High difficulty — requires strong backlink profile and comprehensive content. Consider long-tail variations first."
    return "Very high difficulty — focus on long-tail variations and building topical authority before targeting directly."


# ──────────────────────────────────────────────
# 4. Unified Pipeline
# ──────────────────────────────────────────────

def run_intelligent_keyword_analysis(
    keywords: list[str],
    seed: str = "",
    classify_intent: bool = True,
    cluster: bool = True,
    estimate_difficulty: bool = True,
    difficulty_sample_size: int = 5,
    model: str = "",
) -> dict:
    """
    Run the full LLM-powered keyword intelligence pipeline.

    Args:
        keywords: List of keyword strings to analyze
        seed: Original seed keyword (for context)
        classify_intent: Whether to classify intent
        cluster: Whether to cluster keywords semantically
        estimate_difficulty: Whether to estimate difficulty
        difficulty_sample_size: Number of keywords to estimate difficulty for
        model: Ollama model to use (default: from config)

    Returns:
        Dict with intent_map, clusters, difficulties, and stats
    """
    results = {
        "intent_map": {},
        "clusters": [],
        "difficulties": {},
        "stats": {},
    }

    if not keywords:
        return results

    print(f"[llm_intel] Analyzing {len(keywords)} keywords...")

    # Step 1: Intent Classification (respects config toggle)
    if classify_intent and LLM_INTENT_CLASSIFICATION:
        print("[llm_intel] Step 1: Classifying intent via LLM...")
        results["intent_map"] = classify_intents_batch(keywords, model=model)
    elif classify_intent:
        print("[llm_intel] Step 1: Classifying intent via heuristic (LLM disabled)...")
        results["intent_map"] = {kw: _classify_intent_heuristic(kw) for kw in keywords}

    # Step 2: Semantic Clustering (respects config toggle)
    if cluster and SEMANTIC_CLUSTERING:
        print("[llm_intel] Step 2: Semantic clustering via embeddings...")
        results["clusters"] = cluster_keywords_semantic(keywords)
    elif cluster:
        print("[llm_intel] Step 2: Fallback word-overlap clustering (semantic disabled)...")
        results["clusters"] = _fallback_cluster(keywords)

    # Step 3: Keyword Difficulty (sample a subset to avoid excessive API calls)
    if estimate_difficulty:
        print("[llm_intel] Step 3: Estimating difficulty...")
        # Sample keywords for difficulty estimation
        sample = keywords[:difficulty_sample_size]
        for kw in sample:
            print(f"[llm_intel] Estimating difficulty for '{kw}'...")
            results["difficulties"][kw] = estimate_keyword_difficulty_llm(kw, model=model)
            time.sleep(1)  # Rate limiting

    # Stats
    intent_counts = {}
    for intent in results["intent_map"].values():
        intent_counts[intent] = intent_counts.get(intent, 0) + 1

    results["stats"] = {
        "total_keywords": len(keywords),
        "classified_intents": len(results["intent_map"]),
        "total_clusters": len(results["clusters"]),
        "estimated_difficulties": len(results["difficulties"]),
        "intent_distribution": intent_counts,
    }

    return results


# ──────────────────────────────────────────────
# 5. Status / Health Check
# ──────────────────────────────────────────────

def check_llm_availability() -> dict:
    """Check which LLM capabilities are available."""
    ollama_running = _check_ollama()
    models = []

    if ollama_running:
        try:
            resp = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
            if resp.status_code == 200:
                models = [m["name"] for m in resp.json().get("models", [])]
        except Exception:
            pass

    has_embedding_model = any("nomic-embed" in m for m in models)
    has_generation_model = any(OLLAMA_MODEL in m or "qwen" in m or "llama" in m for m in models)

    import os
    has_serper = bool(os.getenv("SERPER_API_KEY", ""))

    return {
        "ollama_running": ollama_running,
        "available_models": models,
        "has_embedding_model": has_embedding_model,
        "has_generation_model": has_generation_model,
        "has_serper_api": has_serper,
        "capabilities": {
            "intent_classification": ollama_running and has_generation_model,
            "semantic_clustering": ollama_running and has_embedding_model,
            "difficulty_estimation": ollama_running,
            "difficulty_with_serper": has_serper,
        },
    }
