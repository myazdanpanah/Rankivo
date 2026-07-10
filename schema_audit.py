"""
Rankivo — Schema.org Deep Audit Module
Detects, validates, and provides recommendations for 15+ schema types.
Tracks deprecated types per Google's guidelines (2024-2026).
"""
import json
import re
import requests
from config import REQUEST_TIMEOUT, USER_AGENTS
import random


def _random_ua() -> str:
    return random.choice(USER_AGENTS)


# ──────────────────────────────────────────────
# Schema type definitions with required/recommended fields
# Based on Google Search Docs and Schema.org spec
# ──────────────────────────────────────────────

SCHEMA_TYPES = {
    "Article": {
        "category": "content",
        "required": ["headline", "author"],
        "recommended": [
            "datePublished", "dateModified", "image", "description",
            "publisher", "mainEntityOfPage",
        ],
        "rich_results": True,
        "notes": "Base type for all article-like content",
    },
    "BlogPosting": {
        "category": "content",
        "required": ["headline", "author"],
        "recommended": [
            "datePublished", "dateModified", "image", "description",
            "publisher", "wordCount", "articleSection",
        ],
        "rich_results": True,
        "notes": "Blog-specific article type",
    },
    "NewsArticle": {
        "category": "content",
        "required": ["headline", "author"],
        "recommended": [
            "datePublished", "dateModified", "image", "description",
            "publisher", "speakable",
        ],
        "rich_results": True,
        "notes": "News-specific article type",
    },
    "TechArticle": {
        "category": "content",
        "required": ["headline", "author"],
        "recommended": [
            "datePublished", "dateModified", "image", "description",
            "proficiencyLevel", "dependencies",
        ],
        "rich_results": False,
        "notes": "Technical content — no dedicated rich results",
    },
    "Organization": {
        "category": "identity",
        "required": ["name"],
        "recommended": [
            "url", "logo", "description", "sameAs", "contactPoint",
            "address", "foundingDate", "knowsAbout",
        ],
        "rich_results": True,
        "notes": "Brand / organization identity. Supports Knowledge Panel.",
    },
    "LocalBusiness": {
        "category": "identity",
        "required": ["name", "address"],
        "recommended": [
            "telephone", "openingHours", "geo", "image",
            "priceRange", "aggregateRating", "review",
        ],
        "rich_results": True,
        "notes": "Local business with physical location. Requires address.",
    },
    "Person": {
        "category": "identity",
        "required": ["name"],
        "recommended": [
            "url", "image", "jobTitle", "worksFor", "sameAs",
            "knowsAbout", "alumniOf",
        ],
        "rich_results": False,
        "notes": "Individual person — author, founder, etc.",
    },
    "Product": {
        "category": "commerce",
        "required": ["name"],
        "recommended": [
            "description", "image", "offers", "brand",
            "sku", "mpn", "gtin", "aggregateRating", "review",
        ],
        "rich_results": True,
        "notes": "Product with offers for rich product results.",
    },
    "Offer": {
        "category": "commerce",
        "required": ["price", "priceCurrency"],
        "recommended": [
            "availability", "url", "priceValidUntil",
            "itemCondition", "seller",
        ],
        "rich_results": True,
        "notes": "Pricing and availability — child of Product.",
    },
    "Review": {
        "category": "commerce",
        "required": ["itemReviewed"],
        "recommended": [
            "author", "datePublished", "reviewRating",
            "reviewBody", "publisher",
        ],
        "rich_results": True,
        "notes": "Individual review with rating.",
    },
    "AggregateRating": {
        "category": "commerce",
        "required": ["ratingValue", "reviewCount"],
        "recommended": [
            "bestRating", "worstRating", "ratingCount",
        ],
        "rich_results": True,
        "notes": "Aggregate rating — child of Product/LocalBusiness.",
    },
    "BreadcrumbList": {
        "category": "navigation",
        "required": ["itemListElement"],
        "recommended": [],
        "rich_results": True,
        "notes": "Breadcrumb navigation for search results.",
    },
    "WebSite": {
        "category": "identity",
        "required": ["name"],
        "recommended": [
            "url", "potentialAction", "description", "publisher",
        ],
        "rich_results": True,
        "notes": "Site-wide identity. Enables sitelinks searchbox.",
    },
    "WebPage": {
        "category": "content",
        "required": ["name"],
        "recommended": [
            "description", "url", "image", "datePublished",
            "dateModified", "breadcrumb",
        ],
        "rich_results": False,
        "notes": "Generic page descriptor.",
    },
    "Event": {
        "category": "content",
        "required": ["name", "startDate", "location"],
        "recommended": [
            "endDate", "description", "image", "offers",
            "organizer", "eventAttendanceMode",
        ],
        "rich_results": True,
        "notes": "Events with rich result support.",
    },
    "JobPosting": {
        "category": "content",
        "required": ["title", "description", "datePosted", "hiringOrganization"],
        "recommended": [
            "validThrough", "employmentType", "jobLocation",
            "baseSalary", "identifier",
        ],
        "rich_results": True,
        "notes": "Job listings for Google for Jobs.",
    },
    "FAQPage": {
        "category": "content",
        "required": ["mainEntity"],
        "recommended": [],
        "rich_results": False,  # Removed May 2026
        "notes": "⚠️ Google stopped showing FAQ rich results May 7, 2026. Still useful as AI/entity signal.",
    },
    "HowTo": {
        "category": "content",
        "required": ["name"],
        "recommended": ["step", "totalTime", "estimatedCost", "supply", "tool"],
        "rich_results": False,  # Removed Sept 2023
        "notes": "⚠️ DEPRECATED: Rich results removed September 2023. Use Article + structured headings instead.",
    },
    "VideoObject": {
        "category": "media",
        "required": ["name", "description", "thumbnailUrl", "uploadDate"],
        "recommended": [
            "duration", "contentUrl", "embedUrl", "interactionStatistic",
        ],
        "rich_results": True,
        "notes": "Video content for video rich results.",
    },
    "Course": {
        "category": "education",
        "required": ["name", "description"],
        "recommended": [
            "provider", "url", "image", "offers",
            "educationalLevel", "coursePrerequisites",
        ],
        "rich_results": True,
        "notes": "Educational course for Google for Education.",
    },
}


# ──────────────────────────────────────────────
# Deprecated types tracker (2024-2026)
# ──────────────────────────────────────────────

DEPRECATED_TYPES = {
    "HowTo": {
        "deprecated_date": "2023-09",
        "reason": "Rich results removed by Google September 2023",
        "replacement": "Use Article or BlogPosting with step-by-step headings",
    },
    "SpecialAnnouncement": {
        "deprecated_date": "2025-07",
        "reason": "Retired by Google July 2025",
        "replacement": "Use Article with datePublished for time-sensitive content",
    },
    "ClaimReview": {
        "deprecated_date": "2025-06",
        "reason": "Retired by Google June 2025",
        "replacement": "No direct replacement; use Article for fact-check content",
    },
    "VehicleListing": {
        "deprecated_date": "2025-06",
        "reason": "Retired by Google June 2025",
        "replacement": "Use Product with appropriate vehicle attributes",
    },
    "EstimatedSalary": {
        "deprecated_date": "2025-06",
        "reason": "Retired by Google June 2025",
        "replacement": "No direct replacement",
    },
    "LearningVideo": {
        "deprecated_date": "2025-06",
        "reason": "Retired by Google June 2025",
        "replacement": "Use VideoObject",
    },
    "CourseInfo": {
        "deprecated_date": "2025-06",
        "reason": "Course carousel retired by Google June 2025",
        "replacement": "Use Course type",
    },
}


# ──────────────────────────────────────────────
# Parser
# ──────────────────────────────────────────────

def _extract_schemas(soup) -> list[dict]:
    """Extract all JSON-LD schema blocks from a page."""
    schemas = []
    scripts = soup.find_all("script", attrs={"type": "application/ld+json"})
    for i, script in enumerate(scripts):
        raw = script.string or ""
        raw = raw.strip()
        if not raw:
            continue
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            schemas.append({
                "index": i,
                "valid": False,
                "error": "Invalid JSON",
                "raw_preview": raw[:200],
            })
            continue

        # Handle @graph wrapper
        items = [data]
        if isinstance(data, dict) and "@graph" in data:
            items = data["@graph"]
        elif isinstance(data, list):
            items = data

        for item in items:
            if isinstance(item, dict):
                schemas.append({
                    "index": i,
                    "type": item.get("@type", "unknown"),
                    "data": item,
                    "valid": True,
                })

    return schemas


def _validate_schema(schema_data: dict, schema_type: str) -> dict:
    """Validate a single schema instance against known requirements."""
    type_info = SCHEMA_TYPES.get(schema_type, {})
    required = type_info.get("required", [])
    recommended = type_info.get("recommended", [])

    issues = []
    fields_present = []
    fields_missing = []

    # Check @context
    if "@context" not in schema_data:
        issues.append({"severity": "critical", "message": "Missing @context"})

    # Check required fields
    for field in required:
        if field in schema_data and schema_data[field]:
            fields_present.append(field)
        else:
            fields_missing.append(field)
            issues.append({
                "severity": "warning",
                "message": f"Missing required field: {field}",
            })

    # Check recommended fields
    for field in recommended:
        if field in schema_data and schema_data[field]:
            fields_present.append(field)
        else:
            fields_missing.append(field)

    # Type-specific deep validation
    if schema_type == "Product":
        issues.extend(_validate_product(schema_data))
    elif schema_type == "LocalBusiness":
        issues.extend(_validate_local_business(schema_data))
    elif schema_type in ("Article", "BlogPosting", "NewsArticle"):
        issues.extend(_validate_article(schema_data, schema_type))
    elif schema_type == "BreadcrumbList":
        issues.extend(_validate_breadcrumb(schema_data))
    elif schema_type == "FAQPage":
        issues.append({
            "severity": "info",
            "message": "⚠️ FAQPage: Google stopped showing FAQ rich results May 2026. Still useful as AI/entity signal but not for rich results.",
        })

    # Check for deprecated type
    if schema_type in DEPRECATED_TYPES:
        dep = DEPRECATED_TYPES[schema_type]
        issues.append({
            "severity": "critical",
            "message": f"⚠️ DEPRECATED TYPE: {schema_type} — {dep['reason']}. Replacement: {dep['replacement']}",
        })

    return {
        "type": schema_type,
        "issues": issues,
        "fields_present": fields_present,
        "fields_missing": fields_missing,
        "has_rich_results": type_info.get("rich_results", False),
        "category": type_info.get("category", "unknown"),
    }


def _validate_product(data: dict) -> list[dict]:
    """Deep validation for Product schema."""
    issues = []
    offers = data.get("offers")
    if not offers:
        issues.append({"severity": "warning", "message": "Product missing offers — needed for price/rich results"})
    elif isinstance(offers, dict):
        if not offers.get("price"):
            issues.append({"severity": "warning", "message": "Offer missing price"})
        if not offers.get("priceCurrency"):
            issues.append({"severity": "info", "message": "Offer missing priceCurrency"})
        if not offers.get("availability"):
            issues.append({"severity": "info", "message": "Offer missing availability"})
    elif isinstance(offers, list):
        for j, offer in enumerate(offers):
            if isinstance(offer, dict):
                if not offer.get("price"):
                    issues.append({"severity": "warning", "message": f"Offer #{j+1} missing price"})
    if not data.get("image"):
        issues.append({"severity": "info", "message": "Product missing image"})
    if not data.get("brand"):
        issues.append({"severity": "info", "message": "Product missing brand"})
    if not data.get("aggregateRating") and not data.get("review"):
        issues.append({"severity": "info", "message": "Product has no ratings/reviews — add for star rich results"})
    return issues


def _validate_local_business(data: dict) -> list[dict]:
    """Deep validation for LocalBusiness schema."""
    issues = []
    if not data.get("address"):
        issues.append({"severity": "critical", "message": "LocalBusiness requires address"})
    if not data.get("telephone"):
        issues.append({"severity": "warning", "message": "LocalBusiness missing telephone"})
    if not data.get("openingHours"):
        issues.append({"severity": "warning", "message": "LocalBusiness missing openingHours"})
    if not data.get("geo"):
        issues.append({"severity": "info", "message": "LocalBusiness missing geo coordinates"})
    if not data.get("image"):
        issues.append({"severity": "info", "message": "LocalBusiness missing image"})
    return issues


def _validate_article(data: dict, schema_type: str) -> list[dict]:
    """Deep validation for Article schema types."""
    issues = []
    author = data.get("author")
    if not author:
        issues.append({"severity": "warning", "message": "Article missing author"})
    elif isinstance(author, dict) and not author.get("name") and not author.get("@id"):
        issues.append({"severity": "info", "message": "Author object should have name or @id"})
    if not data.get("datePublished"):
        issues.append({"severity": "warning", "message": "Article missing datePublished"})
    if not data.get("dateModified"):
        issues.append({"severity": "info", "message": "Article missing dateModified"})
    if not data.get("publisher"):
        issues.append({"severity": "info", "message": "Article missing publisher"})
    if not data.get("image"):
        issues.append({"severity": "info", "message": "Article missing image"})
    if not data.get("mainEntityOfPage"):
        issues.append({"severity": "info", "message": "Article missing mainEntityOfPage"})
    return issues


def _validate_breadcrumb(data: dict) -> list[dict]:
    """Deep validation for BreadcrumbList."""
    issues = []
    items = data.get("itemListElement", [])
    if not items:
        issues.append({"severity": "warning", "message": "BreadcrumbList has no itemListElement"})
    else:
        for i, item in enumerate(items):
            if isinstance(item, dict):
                if not item.get("name") and not item.get("item"):
                    issues.append({"severity": "warning", "message": f"Breadcrumb item #{i+1} missing name or item"})
                if "position" not in item:
                    issues.append({"severity": "info", "message": f"Breadcrumb item #{i+1} missing position"})
    return issues


# ──────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────

def audit_schema(url: str) -> dict:
    """
    Deep Schema.org audit for a URL.
    Detects all JSON-LD blocks, validates against known types,
    tracks deprecated types, and provides actionable recommendations.
    """
    result = {
        "url": url,
        "schemas_found": 0,
        "valid_schemas": 0,
        "invalid_schemas": 0,
        "schemas": [],
        "types_found": [],
        "deprecated_types": [],
        "types_with_rich_results": [],
        "issues": [],
        "score": 100,
        "recommendations": [],
    }

    # Fetch page
    try:
        headers = {"User-Agent": _random_ua()}
        resp = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT, allow_redirects=True)
        resp.raise_for_status()
    except requests.RequestException as e:
        result["issues"].append({
            "severity": "critical",
            "message": f"Could not fetch URL: {e}",
        })
        result["score"] = 0
        return result

    from bs4 import BeautifulSoup
    soup = BeautifulSoup(resp.text, "lxml")

    # Extract all schemas
    raw_schemas = _extract_schemas(soup)
    result["schemas_found"] = len(raw_schemas)

    if not raw_schemas:
        result["issues"].append({
            "severity": "critical",
            "message": "No structured data (JSON-LD) found on page",
        })
        result["recommendations"].append({
            "priority": "high",
            "action": "Add JSON-LD structured data. Start with Organization or WebSite schema.",
            "how_to_verify": "Re-run audit and verify schemas_found > 0",
        })
        return result

    # Validate each schema
    for schema in raw_schemas:
        if not schema.get("valid"):
            result["invalid_schemas"] += 1
            result["issues"].append({
                "severity": "critical",
                "message": f"Schema block #{schema['index']+1}: {schema.get('error', 'Invalid')}",
            })
            result["score"] -= 10
            result["schemas"].append(schema)
            continue

        schema_type = schema.get("type", "unknown")
        result["types_found"].append(schema_type)

        # Check deprecated
        if schema_type in DEPRECATED_TYPES:
            dep = DEPRECATED_TYPES[schema_type]
            result["deprecated_types"].append({
                "type": schema_type,
                "reason": dep["reason"],
                "replacement": dep["replacement"],
            })

        # Check rich results
        type_info = SCHEMA_TYPES.get(schema_type, {})
        if type_info.get("rich_results"):
            result["types_with_rich_results"].append(schema_type)

        # Validate
        validated = _validate_schema(schema["data"], schema_type)
        validated["raw"] = schema["data"]
        result["schemas"].append(validated)
        result["valid_schemas"] += 1

        # Count issues per schema — subtractive scoring (like technical_seo.py)
        for issue in validated["issues"]:
            result["issues"].append(issue)
            if issue["severity"] == "critical":
                result["score"] -= 10
            elif issue["severity"] == "warning":
                result["score"] -= 5
            elif issue["severity"] == "info":
                result["score"] -= 1

    # Deduplicate types
    result["types_found"] = list(set(result["types_found"]))

    # Check for missing essential schemas
    types_set = set(result["types_found"])
    if "Organization" not in types_set and "LocalBusiness" not in types_set:
        result["recommendations"].append({
            "priority": "high",
            "action": "Add Organization schema for brand identity and Knowledge Panel eligibility",
            "how_to_verify": "Re-run audit and verify Organization type is detected",
        })
    if "BreadcrumbList" not in types_set:
        result["recommendations"].append({
            "priority": "medium",
            "action": "Add BreadcrumbList schema for enhanced navigation in search results",
            "how_to_verify": "Search for your site in Google — breadcrumbs should appear in SERPs",
        })
    if not any(t in types_set for t in ("Article", "BlogPosting", "NewsArticle")):
        result["recommendations"].append({
            "priority": "low",
            "action": "Consider adding Article schema to content pages for article rich results",
            "how_to_verify": "Add Article schema to blog posts and content pages",
        })

    # Check for deprecated type usage
    if result["deprecated_types"]:
        for dep in result["deprecated_types"]:
            result["recommendations"].append({
                "priority": "high",
                "action": f"Replace deprecated {dep['type']} with {dep['replacement']}",
                "how_to_verify": f"Re-run audit and verify {dep['type']} is no longer detected",
            })

    result["score"] = max(0, min(100, result["score"]))
    return result
