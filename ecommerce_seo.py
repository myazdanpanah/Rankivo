"""
Rankivo — E-commerce SEO Module
Analyzes product schema, pricing signals, availability, marketplace presence,
and e-commerce-specific SEO factors.
"""
import re
import requests
from urllib.parse import urlparse
from config import REQUEST_TIMEOUT, USER_AGENTS
import random


def _random_ua() -> str:
    return random.choice(USER_AGENTS)


# ──────────────────────────────────────────────
# Product Schema Validation
# ──────────────────────────────────────────────

_REQUIRED_PRODUCT_FIELDS = ["name"]
_RECOMMENDED_PRODUCT_FIELDS = [
    "description", "image", "offers", "brand", "sku", "mpn", "gtin",
    "aggregateRating", "review", "url",
]

_REQUIRED_OFFER_FIELDS = ["price", "priceCurrency"]
_RECOMMENDED_OFFER_FIELDS = [
    "availability", "url", "priceValidUntil", "itemCondition", "seller",
    "shippingDetails", "hasMerchantReturnPolicy",
]

_EU_REQUIRED_FIELDS = ["energyEfficiencyClass"]  # EU energy labeling


def _validate_product_schema(data: dict) -> dict:
    """Deep validate a Product schema."""
    issues = []
    fields_present = []
    fields_missing = []
    score = 100

    # Required fields
    for field in _REQUIRED_PRODUCT_FIELDS:
        if data.get(field):
            fields_present.append(field)
        else:
            fields_missing.append(field)
            issues.append({"severity": "critical", "message": f"Product missing required field: {field}"})
            score -= 15

    # Recommended fields
    for field in _RECOMMENDED_PRODUCT_FIELDS:
        if data.get(field):
            fields_present.append(field)
        else:
            fields_missing.append(field)

    # Validate offers
    offers = data.get("offers")
    if not offers:
        issues.append({"severity": "warning", "message": "Product missing offers — needed for rich product results"})
        score -= 10
    else:
        offer_list = offers if isinstance(offers, list) else [offers]
        for i, offer in enumerate(offer_list):
            if isinstance(offer, dict):
                for field in _REQUIRED_OFFER_FIELDS:
                    if not offer.get(field):
                        issues.append({"severity": "warning", "message": f"Offer #{i+1} missing {field}"})
                        score -= 5

                # Check availability
                avail = offer.get("availability", "")
                if avail:
                    if "OutOfStock" in avail:
                        issues.append({"severity": "info", "message": "Product shows as OutOfStock"})

                # Check price validity
                if offer.get("priceValidUntil"):
                    try:
                        from datetime import datetime
                        valid_until = datetime.strptime(offer["priceValidUntil"], "%Y-%m-%d")
                        if valid_until < datetime.now():
                            issues.append({"severity": "warning", "message": "Offer priceValidUntil has expired"})
                            score -= 5
                    except (ValueError, TypeError):
                        pass

    # Check for images
    images = data.get("image")
    if not images:
        issues.append({"severity": "info", "message": "Product missing image — critical for visual search"})
        score -= 5

    # Check for brand
    if not data.get("brand"):
        issues.append({"severity": "info", "message": "Product missing brand — helps with brand recognition"})

    # Check for ratings
    if not data.get("aggregateRating") and not data.get("review"):
        issues.append({"severity": "info", "message": "No ratings/reviews — add for star rich results"})

    return {
        "issues": issues,
        "fields_present": fields_present,
        "fields_missing": fields_missing,
        "score": max(0, min(100, score)),
    }


# ──────────────────────────────────────────────
# Product Page Analysis
# ──────────────────────────────────────────────

def _analyze_product_page(soup, body_text: str, url: str) -> dict:
    """Analyze product page elements."""
    result = {
        "has_price": False,
        "has_buy_button": False,
        "has_product_images": False,
        "has_reviews_section": False,
        "has_faq_section": False,
        "has_specs_table": False,
        "has_shipping_info": False,
        "has_return_policy": False,
        "has_breadcrumbs": False,
        "issues": [],
    }

    # Price detection
    price_patterns = [
        r'[\$€£¥]\s*\d+(?:[.,]\d{2})?',
        r'\d+(?:[.,]\d{2})?\s*(?:USD|EUR|GBP|IRR|IRT)',
        r'(?:price|قیمت|preis|prix)[:\s]*[\d$€£¥]',
    ]
    for pattern in price_patterns:
        if re.search(pattern, body_text, re.IGNORECASE):
            result["has_price"] = True
            break

    # Buy/Add to Cart button
    buy_patterns = [
        r'(?:add to cart|buy now|purchase|order now|افزودن به سبد|خرید)',
        r'(?:buy|purchase|order|cart|checkout|سبد خرید)',
    ]
    for pattern in buy_patterns:
        if re.search(pattern, body_text, re.IGNORECASE):
            result["has_buy_button"] = True
            break

    # Product images (multiple = good)
    images = soup.find_all("img")
    product_images = [img for img in images if img.get("src", "")]
    result["has_product_images"] = len(product_images) >= 2

    # Reviews section
    review_patterns = [
        r'(?:reviews?|rating|-stars?|تقييم|نقد)',
        r'(?:\d+(?:\.\d+)?)\s*(?:out of|\/|از)\s*5',
    ]
    for pattern in review_patterns:
        if re.search(pattern, body_text, re.IGNORECASE):
            result["has_reviews_section"] = True
            break

    # FAQ section
    faq_patterns = [
        r'(?:frequently asked|faq|سوالات متداول)',
        r'(?:q\s*&\s*a|questions?\s*(?:and|&)\s*answers?)',
    ]
    for pattern in faq_patterns:
        if re.search(pattern, body_text, re.IGNORECASE):
            result["has_faq_section"] = True
            break

    # Specs table
    tables = soup.find_all("table")
    result["has_specs_table"] = len(tables) > 0

    # Shipping info
    if re.search(r'(?:shipping|delivery|ارسال| доставк)', body_text, re.IGNORECASE):
        result["has_shipping_info"] = True

    # Return policy
    if re.search(r'(?:return|refund|policy|بازگشت|استرداد)', body_text, re.IGNORECASE):
        result["has_return_policy"] = True

    # Breadcrumbs
    result["has_breadcrumbs"] = bool(soup.find("nav", attrs={"aria-label": re.compile(r"breadcrumb", re.I)}))
    if not result["has_breadcrumbs"]:
        # Check for BreadcrumbList schema
        for script in soup.find_all("script", attrs={"type": "application/ld+json"}):
            try:
                data = json.loads(script.string or "")
                if isinstance(data, dict):
                    items = data.get("@graph", [data]) if "@graph" in data else [data]
                    for item in items:
                        if isinstance(item, dict) and item.get("@type") == "BreadcrumbList":
                            result["has_breadcrumbs"] = True
                            break
            except Exception:
                pass

    # Generate issues
    if not result["has_price"]:
        result["issues"].append({"severity": "critical", "message": "No visible price on page"})
    if not result["has_buy_button"]:
        result["issues"].append({"severity": "warning", "message": "No buy/add-to-cart button detected"})
    if not result["has_product_images"]:
        result["issues"].append({"severity": "warning", "message": "Few product images — add multiple angles"})
    if not result["has_reviews_section"]:
        result["issues"].append({"severity": "info", "message": "No reviews section — add for social proof"})
    if not result["has_faq_section"]:
        result["issues"].append({"severity": "info", "message": "No FAQ section — adds rich result opportunities"})
    if not result["has_breadcrumbs"]:
        result["issues"].append({"severity": "info", "message": "No breadcrumbs detected — add BreadcrumbList schema"})

    return result


# ──────────────────────────────────────────────
# Marketplace Presence Check
# ──────────────────────────────────────────────

def _check_marketplace_signals(soup, body_text: str) -> dict:
    """Check for marketplace and comparison signals."""
    signals = {
        "has_social_proof": False,
        "has_trust_badges": False,
        "has_comparison_links": False,
        "issues": [],
    }

    # Social proof
    social_patterns = [
        r'(?:customers?|clients?|users?)\s+(?:love|trust|recommend)',
        r'(?:sold|downloaded|used)\s+(?:\d+|over|more than)',
        r'(?:★|⭐|⭐⭐⭐|⭐⭐⭐⭐|⭐⭐⭐⭐⭐)',
    ]
    for pattern in social_patterns:
        if re.search(pattern, body_text, re.IGNORECASE):
            signals["has_social_proof"] = True
            break

    # Trust badges
    trust_patterns = [
        r'(?:secure|encrypted|ssl|pci|gdpr|hipaa)',
        r'(?:money[- ]back|guarantee|warranty)',
        r'(?:verified|certified|official)',
    ]
    for pattern in trust_patterns:
        if re.search(pattern, body_text, re.IGNORECASE):
            signals["has_trust_badges"] = True
            break

    return signals


# ──────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────

def audit_ecommerce(url: str) -> dict:
    """
    Full e-commerce SEO audit for a URL.
    Analyzes product schema, page elements, and marketplace signals.
    """
    result = {
        "url": url,
        "product_schema": {},
        "product_page": {},
        "marketplace_signals": {},
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

    # Remove boilerplate
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    body_text = soup.get_text(separator=" ", strip=True)

    # Find Product schema
    product_schema = None
    for script in soup.find_all("script", attrs={"type": "application/ld+json"}):
        try:
            data = json.loads(script.string or "")
            if isinstance(data, dict):
                items = data.get("@graph", [data]) if "@graph" in data else [data]
                for item in items:
                    if isinstance(item, dict) and item.get("@type") == "Product":
                        product_schema = item
                        break
        except Exception:
            pass

    # Validate product schema
    if product_schema:
        validation = _validate_product_schema(product_schema)
        result["product_schema"] = {
            "found": True,
            "data": product_schema,
            **validation,
        }
        result["issues"].extend(validation["issues"])
        result["score"] = min(result["score"], validation["score"])
    else:
        result["product_schema"] = {"found": False}
        result["issues"].append({"severity": "critical", "message": "No Product schema found"})
        result["score"] -= 20

    # Analyze product page elements
    result["product_page"] = _analyze_product_page(soup, body_text, url)
    result["issues"].extend(result["product_page"]["issues"])

    # Marketplace signals
    result["marketplace_signals"] = _check_marketplace_signals(soup, body_text)

    # Deduct score for page issues
    for issue in result["product_page"]["issues"]:
        if issue["severity"] == "critical":
            result["score"] -= 10
        elif issue["severity"] == "warning":
            result["score"] -= 5
        elif issue["severity"] == "info":
            result["score"] -= 2

    # Generate recommendations
    if not result["product_schema"].get("found"):
        result["recommendations"].append(
            "Add Product schema with name, image, offers (price, currency, availability)"
        )
    if not result["product_page"].get("has_faq_section"):
        result["recommendations"].append(
            "Add FAQ section for FAQ rich result eligibility"
        )
    if not result["product_page"].get("has_reviews_section"):
        result["recommendations"].append(
            "Add customer reviews with AggregateRating schema for star rich results"
        )
    result["recommendations"].append(
        "Ensure product descriptions are unique (300+ words) — avoid manufacturer copy"
    )

    result["score"] = max(0, min(100, result["score"]))
    return result
