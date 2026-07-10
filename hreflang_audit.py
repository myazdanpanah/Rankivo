"""
Rankivo — Hreflang / International SEO Audit Module
Validates hreflang tags, self-referencing, return tag reciprocity,
x-default, language codes, and canonical alignment.
"""
import re
import requests
from urllib.parse import urlparse, urljoin
from config import REQUEST_TIMEOUT, USER_AGENTS
import random


def _random_ua() -> str:
    return random.choice(USER_AGENTS)


# ISO 639-1 valid language codes (common subset)
VALID_LANG_CODES = {
    "en", "es", "fr", "de", "it", "pt", "nl", "ru", "zh", "ja", "ko", "ar",
    "hi", "bn", "pa", "tr", "vi", "th", "pl", "uk", "cs", "sv", "da", "fi",
    "no", "nb", "nn", "el", "he", "ro", "hu", "id", "ms", "tl", "sw", "fa",
    "ur", "gu", "ta", "te", "kn", "ml", "my", "si", "km", "lo", "ka", "am",
    "ne", "ps", "sq", "bs", "hr", "sr", "sl", "sk", "et", "lv", "lt", "mt",
    "cy", "ga", "is", "mk", "bg", "ca", "eu", "gl", "af", "zu", "xh",
}

# Common invalid/mistaken hreflang values
COMMON_MISTAKES = {
    "en-us": "en-US",
    "en-gb": "en-GB",
    "pt-br": "pt-BR",
    "zh-cn": "zh-CN",
    "zh-tw": "zh-TW",
    "fr-fr": "fr-FR",
    "de-de": "de-DE",
    "es-es": "es-ES",
    "pt-br": "pt-BR",
}


def _validate_lang_code(code: str) -> dict:
    """Validate a hreflang language/region code."""
    issues = []
    is_valid = True

    # Check x-default
    if code == "x-default":
        return {"valid": True, "code": code, "type": "x-default", "issues": []}

    parts = code.split("-")

    if len(parts) == 1:
        # Language only
        lang = parts[0].lower()
        if lang not in VALID_LANG_CODES:
            issues.append(f"Unknown language code: '{lang}'")
            is_valid = False
    elif len(parts) == 2:
        # Language-Region
        lang = parts[0].lower()
        region = parts[1].upper()

        if lang not in VALID_LANG_CODES:
            issues.append(f"Unknown language code: '{lang}'")
            is_valid = False

        # Region should be 2 uppercase letters (ISO 3166-1)
        if not re.match(r'^[A-Z]{2}$', region):
            issues.append(f"Invalid region code: '{region}' — should be 2 uppercase letters (e.g., US, GB)")
            is_valid = False

        # Check common case mistakes
        original = f"{parts[0].lower()}-{parts[1].lower()}"
        if original in COMMON_MISTAKES:
            issues.append(f"Possible case error: '{code}' should be '{COMMON_MISTAKES[original]}'")
    else:
        issues.append(f"Invalid hreflang format: '{code}' — use 'xx' or 'xx-XX'")
        is_valid = False

    return {"valid": is_valid, "code": code, "type": "lang-region" if len(parts) == 2 else "lang", "issues": issues}


def _extract_hreflang_tags(soup, page_url: str) -> list[dict]:
    """Extract all hreflang tags from a page."""
    hreflang_tags = []

    # From <link rel="alternate" hreflang="..." href="..."> tags
    for link in soup.find_all("link", attrs={"rel": "alternate", "hreflang": True}):
        hreflang_tags.append({
            "lang": link.get("hreflang", ""),
            "href": link.get("href", ""),
            "source": "link-tag",
        })

    # From sitemap (we check separately)

    return hreflang_tags


def _check_self_referencing(tags: list[dict], page_url: str) -> dict:
    """Check if the page has a self-referencing hreflang tag."""
    parsed_page = urlparse(page_url)
    page_path = parsed_page.path.rstrip("/")

    self_ref = None
    for tag in tags:
        parsed_tag = urlparse(tag["href"])
        tag_path = parsed_tag.path.rstrip("/")
        if tag_path == page_path and parsed_tag.netloc == parsed_page.netloc:
            self_ref = tag
            break

    return {
        "has_self_referencing": self_ref is not None,
        "self_referencing_tag": self_ref,
        "issues": [] if self_ref else ["Missing self-referencing hreflang tag — page should reference itself"],
    }


def _check_return_tags(tags: list[dict]) -> dict:
    """Check hreflang return tag reciprocity (A→B requires B→A)."""
    issues = []

    # Build language→URL mapping
    lang_urls = {}
    for tag in tags:
        lang = tag["lang"]
        href = tag["href"]
        if lang and href:
            lang_urls[lang] = href

    # For each pair, check reciprocity
    checked = set()
    for lang_a, url_a in lang_urls.items():
        for lang_b, url_b in lang_urls.items():
            if lang_a == lang_b:
                continue
            pair = tuple(sorted([lang_a, lang_b]))
            if pair in checked:
                continue
            checked.add(pair)

            # Check if lang_b exists on the page pointed to by lang_a
            # (We can't easily fetch all pages, so we check within the same page)
            # Simple heuristic: if lang_b is in our tag list, assume reciprocity exists
            # Full check would require fetching each URL

    return {
        "total_pairs": len(checked),
        "issues": issues,
        "note": "Full reciprocity check requires fetching each alternate URL",
    }


def _check_x_default(tags: list[dict]) -> dict:
    """Check for x-default hreflang tag."""
    x_default = [t for t in tags if t["lang"] == "x-default"]

    issues = []
    if not x_default:
        issues.append("Missing x-default hreflang tag — defines the fallback page for unmatched languages")
    elif len(x_default) > 1:
        issues.append("Multiple x-default tags found — only one is allowed")

    return {
        "has_x_default": len(x_default) > 0,
        "x_default_tag": x_default[0] if x_default else None,
        "issues": issues,
    }


def _check_canonical_alignment(tags: list[dict], canonical: str, page_url: str) -> dict:
    """Check that canonical URL aligns with hreflang URLs."""
    issues = []

    if not canonical:
        issues.append("No canonical tag found — hreflang requires a canonical URL")
        return {"aligned": False, "issues": issues}

    parsed_canonical = urlparse(canonical)

    # Check if canonical matches any hreflang href
    canonical_matches = False
    for tag in tags:
        parsed_tag = urlparse(tag["href"])
        if parsed_tag.netloc == parsed_canonical.netloc and parsed_tag.path.rstrip("/") == parsed_canonical.path.rstrip("/"):
            canonical_matches = True
            break

    if not canonical_matches:
        issues.append("Canonical URL does not match any hreflang alternate URL")

    # Check for HTTP/HTTPS mismatch
    for tag in tags:
        parsed_tag = urlparse(tag["href"])
        if parsed_tag.scheme != parsed_canonical.scheme:
            issues.append(f"Protocol mismatch: canonical is {parsed_canonical.scheme}, hreflang '{tag['lang']}' uses {parsed_tag.scheme}")

    return {"aligned": canonical_matches, "issues": issues}


# ──────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────

def audit_hreflang(url: str) -> dict:
    """
    Full hreflang / international SEO audit for a URL.
    Validates tags, self-referencing, x-default, return tags, and canonical alignment.
    """
    result = {
        "url": url,
        "hreflang_tags_found": 0,
        "tags": [],
        "languages_found": [],
        "validation": {},
        "issues": [],
        "recommendations": [],
        "score": 100,
    }

    # Fetch page
    try:
        headers = {"User-Agent": _random_ua()}
        resp = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT, allow_redirects=True)
        resp.raise_for_status()
    except requests.RequestException as e:
        result["issues"].append({"severity": "critical", "message": f"Could not fetch URL: {e}"})
        result["score"] = 0
        return result

    from bs4 import BeautifulSoup
    soup = BeautifulSoup(resp.text, "lxml")

    # Extract hreflang tags
    hreflang_tags = _extract_hreflang_tags(soup, resp.url)
    result["hreflang_tags_found"] = len(hreflang_tags)

    if not hreflang_tags:
        result["issues"].append({"severity": "warning", "message": "No hreflang tags found on page"})
        result["score"] = 30
        result["recommendations"].append(
            "Add hreflang tags if this page has international variants. "
            "Example: <link rel=\"alternate\" hreflang=\"en\" href=\"https://example.com/page\" />"
        )
        return result

    # Get unique languages
    languages = list(set(t["lang"] for t in hreflang_tags if t["lang"]))
    result["languages_found"] = sorted(languages)
    result["tags"] = hreflang_tags[:20]

    # Validate each language code
    validation_results = []
    all_issues = []
    for tag in hreflang_tags:
        v = _validate_lang_code(tag["lang"])
        validation_results.append(v)
        for issue in v["issues"]:
            all_issues.append({"severity": "warning", "message": f" hreflang '{tag['lang']}': {issue}"})
            result["score"] -= 5

    result["validation"]["language_codes"] = validation_results

    # Check self-referencing
    self_ref = _check_self_referencing(hreflang_tags, resp.url)
    result["validation"]["self_referencing"] = self_ref
    for issue in self_ref["issues"]:
        all_issues.append({"severity": "warning", "message": issue})
        result["score"] -= 10

    # Check x-default
    x_default = _check_x_default(hreflang_tags)
    result["validation"]["x_default"] = x_default
    for issue in x_default["issues"]:
        all_issues.append({"severity": "info", "message": issue})
        result["score"] -= 5

    # Check return tags
    return_check = _check_return_tags(hreflang_tags)
    result["validation"]["return_tags"] = return_check

    # Check canonical alignment
    canonical_tag = soup.find("link", attrs={"rel": "canonical"})
    canonical = canonical_tag.get("href", "") if canonical_tag else ""
    canonical_check = _check_canonical_alignment(hreflang_tags, canonical, resp.url)
    result["validation"]["canonical_alignment"] = canonical_check
    for issue in canonical_check["issues"]:
        all_issues.append({"severity": "warning", "message": issue})
        result["score"] -= 5

    result["issues"].extend(all_issues)

    # Check for x-default presence in recommendations
    if not x_default["has_x_default"]:
        result["recommendations"].append("Add an x-default hreflang tag for language/region fallback")

    if not self_ref["has_self_referencing"]:
        result["recommendations"].append("Add a self-referencing hreflang tag (same page should reference itself)")

    result["recommendations"].append(
        "Ensure all hreflang pairs are reciprocal: if page A links to page B, page B must link back to page A"
    )

    result["score"] = max(0, min(100, result["score"]))
    return result
