"""
Rankivo — Local SEO Analysis Module
Evaluates Google Business Profile signals, NAP consistency,
review intelligence, local schema markup, and map pack readiness.
"""
import re
import json
import requests
from urllib.parse import urlparse
from config import REQUEST_TIMEOUT, USER_AGENTS, random_ua
import random




# ──────────────────────────────────────────────
# NAP (Name, Address, Phone) Detection
# ──────────────────────────────────────────────

_PHONE_PATTERNS = [
    r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}',
    r'\+\d{10,15}',
    r'\d{3}[-.\s]\d{3}[-.\s]\d{4}',
]

_ADDRESS_PATTERNS = [
    r'\d+\s+[\w\s]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Lane|Ln|Court|Ct|Way|Place|Pl)\b',
    r'(?:P\.?O\.?\s*Box|PO\s*Box)\s+\d+',
    r'\b\d{5}(?:-\d{4})?\b',  # US ZIP
]

_EMAIL_PATTERN = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'


def _extract_nap(body_text: str, soup) -> dict:
    """Extract Name, Address, Phone from page content."""
    nap = {
        "phones": [],
        "emails": [],
        "addresses": [],
        "has_schema_nap": False,
    }

    # Phone numbers
    for pattern in _PHONE_PATTERNS:
        matches = re.findall(pattern, body_text)
        for m in matches:
            cleaned = re.sub(r'[^\d+\-() ]', '', m).strip()
            if len(cleaned) >= 7:
                nap["phones"].append(cleaned)
    nap["phones"] = list(set(nap["phones"]))[:5]

    # Emails
    emails = re.findall(_EMAIL_PATTERN, body_text)
    nap["emails"] = list(set(emails))[:5]

    # Addresses (simple detection)
    for pattern in _ADDRESS_PATTERNS:
        matches = re.findall(pattern, body_text)
        nap["addresses"].extend(matches[:3])
    nap["addresses"] = list(set(nap["addresses"]))[:5]

    # Check schema.org for structured NAP
    for script in soup.find_all("script", attrs={"type": "application/ld+json"}):
        try:
            data = json.loads(script.string or "")
            if isinstance(data, dict):
                items = data.get("@graph", [data]) if "@graph" in data else [data]
                for item in items:
                    if isinstance(item, dict):
                        stype = item.get("@type", "")
                        if stype in ("LocalBusiness", "Organization", "Restaurant", "MedicalBusiness"):
                            if item.get("telephone"):
                                nap["has_schema_nap"] = True
                            if item.get("address"):
                                nap["has_schema_nap"] = True
        except Exception:
            pass

    return nap


# ──────────────────────────────────────────────
# Local Business Schema Check
# ──────────────────────────────────────────────

_LOCAL_BUSINESS_TYPES = {
    "LocalBusiness", "Restaurant", "MedicalBusiness", "DentistOffice",
    "Hospital", "Pharmacy", "AutomotiveBusiness", "EmploymentAgency",
    "EntertainmentBusiness", "FinancialService", "FoodEstablishment",
    "GovernmentOrganization", "HealthAndBeautyBusiness", "HomeAndConstructionBusiness",
    "InternetCafe", "Library", "LodgingBusiness", "ProfessionalService",
    "RadioStation", "SelfStorage", "ShoppingCenter", "SportsActivityLocation",
    "TouristInformationCenter", "TravelAgency",
}

_REQUIRED_LOCAL_FIELDS = ["name", "address", "telephone"]
_RECOMMENDED_LOCAL_FIELDS = [
    "openingHours", "geo", "image", "priceRange", "aggregateRating",
    "review", "url", "description", "areaServed",
]


def _check_local_schema(soup) -> dict:
    """Check for local business schema markup."""
    result = {
        "has_local_business": False,
        "schema_type": None,
        "fields_present": [],
        "fields_missing": [],
        "issues": [],
    }

    for script in soup.find_all("script", attrs={"type": "application/ld+json"}):
        try:
            data = json.loads(script.string or "")
            if isinstance(data, dict):
                items = data.get("@graph", [data]) if "@graph" in data else [data]
                for item in items:
                    if isinstance(item, dict) and item.get("@type") in _LOCAL_BUSINESS_TYPES:
                        result["has_local_business"] = True
                        result["schema_type"] = item["@type"]

                        for field in _REQUIRED_LOCAL_FIELDS:
                            if item.get(field):
                                result["fields_present"].append(field)
                            else:
                                result["fields_missing"].append(field)
                                result["issues"].append(f"Missing required field: {field}")

                        for field in _RECOMMENDED_LOCAL_FIELDS:
                            if item.get(field):
                                result["fields_present"].append(field)
                            else:
                                result["fields_missing"].append(field)

                        break
        except Exception:
            pass

    if not result["has_local_business"]:
        result["issues"].append("No LocalBusiness schema found — add for local SEO")

    return result


# ──────────────────────────────────────────────
# Google Business Profile Signals
# ──────────────────────────────────────────────

def _check_gbp_signals(soup, body_text: str, url: str) -> dict:
    """Check for Google Business Profile related signals."""
    signals = {
        "has_google_maps_embed": False,
        "has_directions_link": False,
        "has_google_reviews": False,
        "has_business_hours": False,
        "has_geocoordinates": False,
        "google_maps_url": None,
        "issues": [],
    }

    # Check for Google Maps embed
    for iframe in soup.find_all("iframe"):
        src = iframe.get("src", "")
        if "google.com/maps" in src or "maps.google" in src:
            signals["has_google_maps_embed"] = True
            signals["google_maps_url"] = src[:200]
            break

    # Check for Google Maps link
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "google.com/maps" in href or "goo.gl/maps" in href:
            signals["has_google_maps_embed"] = True
            signals["google_maps_url"] = href[:200]
            break
        if "directions" in href.lower():
            signals["has_directions_link"] = True

    # Check for business hours
    hours_patterns = [
        r'(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)',
        r'(?:opening\s*hours?|business\s*hours?|working\s*hours?)',
        r'\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)',
    ]
    for pattern in hours_patterns:
        if re.search(pattern, body_text, re.IGNORECASE):
            signals["has_business_hours"] = True
            break

    # Check for Google Reviews widget/link
    review_patterns = [
        r'google.*review', r'review.*google', r'google.*rating',
    ]
    for pattern in review_patterns:
        if re.search(pattern, body_text, re.IGNORECASE):
            signals["has_google_reviews"] = True
            break

    # Check for geocoordinates in schema
    for script in soup.find_all("script", attrs={"type": "application/ld+json"}):
        try:
            data = json.loads(script.string or "")
            if isinstance(data, dict):
                items = data.get("@graph", [data]) if "@graph" in data else [data]
                for item in items:
                    if isinstance(item, dict) and item.get("geo"):
                        signals["has_geocoordinates"] = True
                        break
        except Exception:
            pass

    if not signals["has_business_hours"]:
        signals["issues"].append("No business hours found — critical for local SEO")
    if not signals["has_google_maps_embed"]:
        signals["issues"].append("No Google Maps embed — add for local signals")
    if not signals["has_geocoordinates"]:
        signals["issues"].append("No geocoordinates in schema — add geo latitude/longitude")

    return signals


# ──────────────────────────────────────────────
# Review Analysis
# ──────────────────────────────────────────────

def _check_review_signals(soup, body_text: str) -> dict:
    """Check for review and rating signals."""
    signals = {
        "has_aggregate_rating": False,
        "has_reviews": False,
        "review_count": 0,
        "has_review_schema": False,
        "issues": [],
    }

    # Check schema for ratings
    for script in soup.find_all("script", attrs={"type": "application/ld+json"}):
        try:
            data = json.loads(script.string or "")
            if isinstance(data, dict):
                items = data.get("@graph", [data]) if "@graph" in data else [data]
                for item in items:
                    if isinstance(item, dict):
                        if item.get("aggregateRating"):
                            signals["has_aggregate_rating"] = True
                            signals["has_review_schema"] = True
                        if item.get("review"):
                            signals["has_reviews"] = True
                            if isinstance(item["review"], list):
                                signals["review_count"] = len(item["review"])
        except Exception:
            pass

    # Check for review text patterns
    review_patterns = [
        r'(?:customer|client|user)\s+reviews?',
        r'(?:\d+(?:\.\d+)?)\s*(?:out of|\/)\s*5',
        r'(?:★|☆|⭐|⭐⭐⭐|⭐⭐⭐⭐|⭐⭐⭐⭐⭐)',
        r'(?:rating|reviews?)[\s:]+\d',
    ]
    for pattern in review_patterns:
        if re.search(pattern, body_text, re.IGNORECASE):
            signals["has_reviews"] = True
            break

    if not signals["has_aggregate_rating"]:
        signals["issues"].append("No AggregateRating schema — add for star rich results")
    if not signals["has_reviews"]:
        signals["issues"].append("No review signals found — encourage customer reviews")

    return signals


# ──────────────────────────────────────────────
# NAP Consistency Check
# ──────────────────────────────────────────────

def _check_nap_consistency(nap: dict, local_schema: dict, body_text: str) -> dict:
    """Check NAP consistency across page elements."""
    issues = []

    has_phone_in_text = len(nap.get("phones", [])) > 0
    has_phone_in_schema = "telephone" in local_schema.get("fields_present", [])

    has_address_in_text = len(nap.get("addresses", [])) > 0
    has_address_in_schema = "address" in local_schema.get("fields_present", [])

    if not has_phone_in_text and not has_phone_in_schema:
        issues.append("No phone number found anywhere on page")
    elif has_phone_in_text and not has_phone_in_schema:
        issues.append("Phone found in text but missing from LocalBusiness schema")

    if not has_address_in_text and not has_address_in_schema:
        issues.append("No address found anywhere on page")
    elif has_address_in_text and not has_address_in_schema:
        issues.append("Address found in text but missing from LocalBusiness schema")

    if not nap.get("emails"):
        issues.append("No email address found on page")

    return {
        "phone_consistent": has_phone_in_text and has_phone_in_schema,
        "address_consistent": has_address_in_text and has_address_in_schema,
        "issues": issues,
    }


# ──────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────

def audit_local_seo(url: str) -> dict:
    """
    Full local SEO audit for a URL.
    Checks GBP signals, NAP, local schema, reviews, and consistency.
    """
    result = {
        "url": url,
        "nap": {},
        "local_schema": {},
        "gbp_signals": {},
        "review_signals": {},
        "nap_consistency": {},
        "issues": [],
        "recommendations": [],
        "score": 100,
    }

    # Fetch page
    try:
        headers = {"User-Agent": random_ua()}
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

    # Run all checks
    result["nap"] = _extract_nap(body_text, soup)
    result["local_schema"] = _check_local_schema(soup)
    result["gbp_signals"] = _check_gbp_signals(soup, body_text, url)
    result["review_signals"] = _check_review_signals(soup, body_text)
    result["nap_consistency"] = _check_nap_consistency(
        result["nap"], result["local_schema"], body_text
    )

    # Aggregate issues
    score = 100

    for issue in result["local_schema"]["issues"]:
        result["issues"].append({"severity": "warning", "message": issue})
        score -= 10

    for issue in result["gbp_signals"]["issues"]:
        result["issues"].append({"severity": "warning", "message": issue})
        score -= 5

    for issue in result["review_signals"]["issues"]:
        result["issues"].append({"severity": "info", "message": issue})
        score -= 5

    for issue in result["nap_consistency"]["issues"]:
        result["issues"].append({"severity": "warning", "message": issue})
        score -= 5

    # Generate recommendations
    if not result["local_schema"]["has_local_business"]:
        result["recommendations"].append(
            "Add LocalBusiness schema with name, address, telephone, openingHours, and geo coordinates"
        )
    if not result["gbp_signals"]["has_business_hours"]:
        result["recommendations"].append(
            "Add visible business hours on the page and in schema markup"
        )
    if not result["gbp_signals"]["has_google_maps_embed"]:
        result["recommendations"].append(
            "Embed a Google Maps widget for your business location"
        )
    if not result["review_signals"]["has_aggregate_rating"]:
        result["recommendations"].append(
            "Add AggregateRating schema with ratingValue and reviewCount for star rich results"
        )

    result["score"] = max(0, min(100, score))
    return result
