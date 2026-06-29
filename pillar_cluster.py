"""
SEO AI Tools - Pillar / Cluster Mapper
Groups keywords into pillar pages and supporting cluster articles.
"""
from collections import defaultdict
from difflib import SequenceMatcher
from datetime import datetime


# ──────────────────────────────────────────────
# 1. Keyword Similarity Grouping
# ──────────────────────────────────────────────


def _keyword_similarity(kw1: str, kw2: str) -> float:
    """
    Compute a similarity score between two keywords.
    Uses a combination of word overlap and sequence matching.
    """
    words1 = set(kw1.lower().split())
    words2 = set(kw2.lower().split())

    if not words1 or not words2:
        return 0.0

    # Jaccard word overlap
    intersection = words1 & words2
    union = words1 | words2
    jaccard = len(intersection) / len(union)

    # Sequence matcher for phrase-level similarity
    seq_ratio = SequenceMatcher(None, kw1.lower(), kw2.lower()).ratio()

    return 0.6 * jaccard + 0.4 * seq_ratio


def group_keywords_into_clusters(keywords: list[str], threshold: float = 0.35) -> list[dict]:
    """
    Group similar keywords into clusters using single-linkage clustering.
    Returns list of dicts: { "cluster_id": int, "topic": str, "keywords": list[str] }
    """
    if not keywords:
        return []

    # Build similarity matrix and find clusters
    assigned = [False] * len(keywords)
    clusters = []

    for i, kw in enumerate(keywords):
        if assigned[i]:
            continue

        cluster_keywords = [kw]
        assigned[i] = True

        for j in range(i + 1, len(keywords)):
            if assigned[j]:
                continue

            # Check similarity against all existing cluster members
            max_sim = max(
                _keyword_similarity(kw, keywords[j])
                for kw in cluster_keywords
            )

            if max_sim >= threshold:
                cluster_keywords.append(keywords[j])
                assigned[j] = True

        clusters.append({
            "topic": cluster_keywords[0],  # First keyword becomes the topic
            "keywords": cluster_keywords,
        })

    # Sort clusters by size (largest first)
    clusters.sort(key=lambda c: len(c["keywords"]), reverse=True)

    # Assign IDs
    for i, c in enumerate(clusters):
        c["cluster_id"] = i

    return clusters


# ──────────────────────────────────────────────
# 2. Pillar Page Identification
# ──────────────────────────────────────────────


def identify_pillar_clusters(
    clusters: list[dict],
    intent_map: dict[str, str] | None = None,
    language: str = "en",
) -> list[dict]:
    """
    For each cluster, determine the best pillar keyword.
    Prioritises broad informational keywords (pillar) over specific ones (cluster).
    """
    pillar_clusters = []

    for cluster in clusters:
        keywords = cluster["keywords"]

        # Score each keyword: longer tail = cluster candidate, broader = pillar candidate
        scored = []
        for kw in keywords:
            word_count = len(kw.split())
            intent = (intent_map or {}).get(kw, "informational")
            # Broad, informational keywords score highest for pillar
            pillar_score = (10 - min(word_count, 10))  # fewer words = broader
            if intent == "informational":
                pillar_score += 2
            elif intent == "commercial":
                pillar_score += 1
            scored.append((kw, pillar_score))

        scored.sort(key=lambda x: x[1], reverse=True)
        pillar_keyword = scored[0][0]
        cluster_keywords = [s[0] for s in scored[1:]]

        pillar_clusters.append({
            "cluster_id": cluster["cluster_id"],
            "pillar_keyword": pillar_keyword,
            "cluster_keywords": cluster_keywords,
            "all_keywords": keywords,
            "size": len(keywords),
            "pillar_title_suggestion": _generate_pillar_title(pillar_keyword, language=language),
        })

    return pillar_clusters


def _generate_pillar_title(keyword: str, language: str = "en") -> str:
    """Generate a suggested pillar page title from the keyword."""
    if language == "fa":
        return _generate_pillar_title_fa(keyword)
    words = keyword.split()
    title = " ".join(w.capitalize() if w[0].islower() else w for w in words)
    # Add common pillar suffixes if the keyword doesn't already imply one
    lower = keyword.lower()
    if not any(w in lower for w in ["guide", "hub", "resource", "overview", "complete"]):
        title = f"The Complete Guide to {title}"
    return title


def _generate_pillar_title_fa(keyword: str) -> str:
    """Generate a Persian pillar page title from the keyword."""
    return f"راهنمای جامع {keyword}"


# ──────────────────────────────────────────────
# 3. Content Brief Generation
# ──────────────────────────────────────────────


def generate_cluster_content_plan(pillar_clusters: list[dict], intent_map: dict | None = None, language: str = "en") -> list[dict]:
    """
    For each pillar cluster, generate a content plan with suggested article
    titles for the cluster articles.
    """
    plans = []

    for pc in pillar_clusters:
        articles = []

        for kw in pc["cluster_keywords"]:
            intent = (intent_map or {}).get(kw, "informational")
            title = _generate_cluster_title(kw, intent, language=language)
            articles.append({
                "keyword": kw,
                "intent": intent,
                "suggested_title": title,
            })

        plans.append({
            "cluster_id": pc["cluster_id"],
            "pillar_keyword": pc["pillar_keyword"],
            "pillar_title": pc["pillar_title_suggestion"],
            "pillar_intent": (intent_map or {}).get(pc["pillar_keyword"], "informational"),
            "articles": articles,
            "total_content_pieces": 1 + len(articles),
        })

    return plans


def _generate_cluster_title(keyword: str, intent: str, language: str = "en") -> str:
    """Generate a cluster article title based on keyword and intent."""
    if language == "fa":
        return _generate_cluster_title_fa(keyword, intent)
    kw = keyword.strip().capitalize()

    current_year = datetime.now().year
    templates = {
        "informational": [
            f"What Is {kw}? A Detailed Explanation",
            f"{kw}: Everything You Need to Know",
            f"Understanding {kw}",
        ],
        "commercial": [
            f"Best {kw} in {current_year}",
            f"Top {kw} Options Compared",
            f"{kw}: Which One Should You Choose?",
        ],
        "transactional": [
            f"Where to Buy {kw}",
            f"{kw} Pricing Guide",
            f"How to Get the Best Deal on {kw}",
        ],
        "navigational": [
            f"{kw} Official Guide",
            f"Getting Started with {kw}",
        ],
    }

    options = templates.get(intent, templates["informational"])
    return options[0]


def _generate_cluster_title_fa(keyword: str, intent: str) -> str:
    """Generate a Persian cluster article title based on keyword and intent."""
    templates = {
        "informational": [
            f"{keyword} چیست؟ توضیح کامل",
            f"همه چیز درباره {keyword}",
            f"آشنایی کامل با {keyword}",
        ],
        "commercial": [
            f"بهترین {keyword} در سال {datetime.now().year}",
            f"مقایسه {keyword}ها — کدام بهتر است؟",
            f"{keyword}: کدام گزینه مناسب شماست؟",
        ],
        "transactional": [
            f"خرید {keyword} — راهنمای قیمت و خرید",
            f"راهنمای قیمت {keyword}",
            f"چگونه بهترین قیمت {keyword} را پیدا کنیم؟",
        ],
        "navigational": [
            f"راهنمای رسمی {keyword}",
            f"شروع کار با {keyword}",
        ],
    }
    options = templates.get(intent, templates["informational"])
    return options[0]


# ──────────────────────────────────────────────
# 4. Full Pillar-Cluster Pipeline
# ──────────────────────────────────────────────


def build_pillar_cluster_map(
    keyword_data: dict,
    cluster_threshold: float = 0.30,
    language: str = "en",
) -> dict:
    """
    Full pipeline: take keyword_research output and produce a pillar-cluster map.
    Returns dict with 'clusters', 'pillar_clusters', 'content_plan', and 'stats'.
    """
    # Collect all unique keywords
    all_kw = set()
    for key in ["suggestions", "modifier_expanded", "related_searches", "people_also_ask"]:
        all_kw.update(keyword_data.get(key, []))

    keywords = sorted(all_kw)
    intent_map = keyword_data.get("intent_map", {})

    # Step 1: Group into clusters
    clusters = group_keywords_into_clusters(keywords, threshold=cluster_threshold)

    # Step 2: Identify pillar keywords
    pillar_clusters = identify_pillar_clusters(clusters, intent_map, language=language)

    # Step 3: Generate content plan
    content_plan = generate_cluster_content_plan(pillar_clusters, intent_map, language=language)

    # Stats
    total_kw = len(keywords)
    total_clusters = len(pillar_clusters)
    total_articles = sum(p["total_content_pieces"] for p in content_plan)

    intent_counts = defaultdict(int)
    for intent in intent_map.values():
        intent_counts[intent] += 1

    return {
        "seed": keyword_data.get("seed", ""),
        "clusters": clusters,
        "pillar_clusters": pillar_clusters,
        "content_plan": content_plan,
        "stats": {
            "total_keywords": total_kw,
            "total_clusters": total_clusters,
            "total_content_pieces": total_articles,
            "intent_distribution": dict(intent_counts),
        },
    }
