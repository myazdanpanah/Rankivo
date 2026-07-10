"""
Rankivo — Image Optimization Analysis Module
Checks alt text quality, file sizes, format recommendations, responsive images,
lazy loading, CLS prevention, and image SEO best practices.
"""
import re
import random
import requests
from urllib.parse import urlparse, urljoin
from config import REQUEST_TIMEOUT, USER_AGENTS


def _random_ua() -> str:
    return random.choice(USER_AGENTS)


# ──────────────────────────────────────────────
# Format detection from URL / Content-Type
# ──────────────────────────────────────────────

_MODERN_FORMATS = {"webp", "avif", "heif", "heic"}
_LEGACY_FORMATS = {"jpg", "jpeg", "png", "gif", "bmp", "tiff", "svg"}

FORMAT_RECOMMENDATIONS = {
    "jpeg": "Consider WebP (30% smaller) or AVIF (50% smaller) for lossy photos",
    "jpg": "Consider WebP (30% smaller) or AVIF (50% smaller) for lossy photos",
    "png": "Consider WebP for lossless (26% smaller) or AVIF for even better compression",
    "gif": "Consider WebP for animated images (smaller) or MP4 for video animations",
    "bmp": "Convert to WebP or AVIF — BMP files are extremely large",
    "tiff": "Convert to WebP or AVIF — TIFF files are unnecessarily large for web",
}


def _detect_format(url: str, content_type: str = "") -> str:
    """Detect image format from URL extension or Content-Type header."""
    # Try Content-Type first
    if content_type:
        ct = content_type.lower()
        if "webp" in ct:
            return "webp"
        elif "avif" in ct:
            return "avif"
        elif "jpeg" in ct or "jpg" in ct:
            return "jpeg"
        elif "png" in ct:
            return "png"
        elif "gif" in ct:
            return "gif"
        elif "svg" in ct:
            return "svg"
        elif "bmp" in ct:
            return "bmp"
        elif "tiff" in ct:
            return "tiff"

    # Fallback to URL extension
    path = urlparse(url).path.lower()
    for ext in ["webp", "avif", "jpeg", "jpg", "png", "gif", "bmp", "tiff", "svg"]:
        if path.endswith(f".{ext}"):
            return ext
    return "unknown"


def _is_modern_format(fmt: str) -> bool:
    return fmt.lower() in _MODERN_FORMATS


# ──────────────────────────────────────────────
# Image Analysis
# ──────────────────────────────────────────────

def _check_alt_text(img, index: int) -> dict:
    """Analyze alt text quality for a single image."""
    alt = (img.get("alt") or "").strip()
    src = img.get("src", "")
    title = (img.get("title") or "").strip()

    result = {
        "index": index,
        "src": src[:120],
        "alt": alt,
        "has_alt": bool(alt),
        "alt_length": len(alt),
        "issues": [],
        "score": 0,
    }

    if not alt:
        result["issues"].append("Missing alt text")
        result["score"] = 0
    elif len(alt) < 5:
        result["issues"].append(f"Alt text too short ({len(alt)} chars) — be descriptive")
        result["score"] = 2
    elif len(alt) > 125:
        result["issues"].append(f"Alt text too long ({len(alt)} chars) — keep under 125 characters")
        result["score"] = 5
    else:
        result["score"] = 10

    # Check for keyword stuffing
    words = alt.lower().split()
    if len(words) > 3:
        word_freq = {}
        for w in words:
            word_freq[w] = word_freq.get(w, 0) + 1
        max_freq = max(word_freq.values()) if word_freq else 0
        if max_freq > 2:
            result["issues"].append("Possible keyword stuffing in alt text")

    # Check for generic alt text
    generic = ["image", "photo", "picture", "img", "screenshot", "untitled"]
    if alt.lower().strip() in generic:
        result["issues"].append(f"Generic alt text '{alt}' — describe the image specifically")
        result["score"] = 3

    # Check for file name as alt (bad practice)
    if re.match(r'^[\w-]+\.\w{2,4}$', alt):
        result["issues"].append("Alt text appears to be a filename — write a description instead")
        result["score"] = 2

    return result


def _check_responsive(img) -> dict:
    """Check for responsive image attributes."""
    srcset = img.get("srcset", "")
    sizes = img.get("sizes", "")
    width = img.get("width", "")
    height = img.get("height", "")

    result = {
        "has_srcset": bool(srcset),
        "has_sizes": bool(sizes),
        "has_width": bool(width),
        "has_height": bool(height),
        "is_responsive": bool(srcset),
        "issues": [],
    }

    if not srcset:
        result["issues"].append("Missing srcset — no responsive image variants")
    if not width or not height:
        result["issues"].append("Missing width/height attributes — can cause CLS (layout shift)")
    if srcset and not sizes:
        result["issues"].append("Has srcset but missing sizes attribute")

    return result


def _check_lazy_loading(img) -> dict:
    """Check for lazy loading implementation."""
    loading = img.get("loading", "")
    decoding = img.get("decoding", "")

    result = {
        "has_lazy_loading": loading == "lazy",
        "loading_attr": loading,
        "decoding_attr": decoding,
        "issues": [],
    }

    # Above-the-fold images should NOT be lazy loaded
    # We can't determine position from HTML alone, so flag if NO images use lazy loading
    if loading and loading != "lazy" and loading != "eager":
        result["issues"].append(f"Invalid loading attribute: '{loading}'")

    return result


def _check_formats(images_data: list[dict]) -> dict:
    """Analyze format distribution across all images."""
    format_counts = {}
    modern_count = 0
    legacy_count = 0

    for img in images_data:
        fmt = img.get("format", "unknown")
        format_counts[fmt] = format_counts.get(fmt, 0) + 1
        if _is_modern_format(fmt):
            modern_count += 1
        elif fmt in _LEGACY_FORMATS:
            legacy_count += 1

    result = {
        "format_distribution": format_counts,
        "modern_format_count": modern_count,
        "legacy_format_count": legacy_count,
        "modern_percentage": round(modern_count / max(len(images_data), 1) * 100, 1),
        "issues": [],
        "recommendations": [],
    }

    if legacy_count > 0 and modern_count == 0:
        result["issues"].append(f"All {legacy_count} images use legacy formats (JPEG/PNG)")
        result["recommendations"].append(
            "Convert images to WebP or AVIF for 30-50% size reduction. "
            "Use <picture> element with fallback for older browsers."
        )
    elif legacy_count > modern_count:
        result["issues"].append(f"Most images ({legacy_count}/{len(images_data)}) use legacy formats")

    # Check for SVG usage (good for logos/icons)
    svg_count = format_counts.get("svg", 0)
    if svg_count == 0:
        result["recommendations"].append(
            "Consider using SVG for logos, icons, and simple illustrations — they scale perfectly"
        )

    return result


def _check_file_sizes(img_urls: list[str]) -> dict:
    """Check file sizes by making HEAD requests (sample up to 10 images)."""
    large_images = []
    total_size = 0
    checked = 0
    errors = 0

    sample = img_urls[:10]

    for url in sample:
        try:
            headers = {"User-Agent": _random_ua()}
            resp = requests.head(url, headers=headers, timeout=5, allow_redirects=True)
            content_length = int(resp.headers.get("content-length", 0))
            content_type = resp.headers.get("content-type", "")

            if content_length > 0:
                checked += 1
                total_size += content_length
                size_kb = round(content_length / 1024, 1)

                entry = {"url": url[:120], "size_bytes": content_length, "size_kb": size_kb}

                if content_length > 500_000:  # 500KB
                    large_images.append(entry)

        except Exception:
            errors += 1
            continue

    avg_size = round(total_size / max(checked, 1) / 1024, 1)

    result = {
        "images_checked": checked,
        "errors": errors,
        "average_size_kb": avg_size,
        "total_size_kb": round(total_size / 1024, 1),
        "large_images": large_images,
        "issues": [],
        "recommendations": [],
    }

    if large_images:
        result["issues"].append(
            f"{len(large_images)} image(s) exceed 500KB — "
            f"largest: {large_images[0]['size_kb']}KB"
        )
        result["recommendations"].append(
            "Compress large images using TinyPNG, Squoosh, or WebP conversion. "
            "Target under 200KB for most web images."
        )

    if avg_size > 300:
        result["issues"].append(f"Average image size is {avg_size}KB — aim for under 200KB")
        result["recommendations"].append(
            "Use responsive images (srcset) to serve appropriately sized images per viewport"
        )

    return result


# ──────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────

def analyze_images(url: str) -> dict:
    """
    Full image optimization analysis for a URL.
    Checks alt text, formats, responsive images, lazy loading, and file sizes.
    """
    result = {
        "url": url,
        "total_images": 0,
        "images_with_alt": 0,
        "images_without_alt": 0,
        "alt_coverage_pct": 0,
        "images": [],
        "format_analysis": {},
        "responsive_analysis": {},
        "lazy_loading_analysis": {},
        "file_size_analysis": {},
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

    # Find all images
    img_tags = soup.find_all("img")
    result["total_images"] = len(img_tags)

    if not img_tags:
        result["issues"].append({"severity": "info", "message": "No images found on page"})
        result["recommendations"].append("Add relevant images to improve engagement and SEO")
        return result

    images_data = []
    img_urls = []

    for i, img in enumerate(img_tags):
        src = img.get("src", "")
        if not src:
            continue

        abs_url = urljoin(url, src)
        img_urls.append(abs_url)

        # Get format
        fmt = _detect_format(abs_url)

        # Analyze alt text
        alt_analysis = _check_alt_text(img, i)
        if alt_analysis["has_alt"]:
            result["images_with_alt"] += 1
        else:
            result["images_without_alt"] += 1

        # Analyze responsive
        responsive = _check_responsive(img)

        # Analyze lazy loading
        lazy = _check_lazy_loading(img)

        img_data = {
            "src": abs_url[:150],
            "alt": alt_analysis["alt"],
            "has_alt": alt_analysis["has_alt"],
            "format": fmt,
            "is_modern_format": _is_modern_format(fmt),
            "alt_score": alt_analysis["score"],
            "alt_issues": alt_analysis["issues"],
            "responsive": responsive,
            "lazy_loading": lazy,
        }
        images_data.append(img_data)

        # Collect issues
        for issue in alt_analysis["issues"]:
            result["issues"].append({"severity": "warning", "message": f"Image #{i+1}: {issue}"})
        for issue in responsive["issues"]:
            result["issues"].append({"severity": "info", "message": f"Image #{i+1}: {issue}"})

    result["images"] = images_data[:30]
    result["alt_coverage_pct"] = round(
        result["images_with_alt"] / max(result["total_images"], 1) * 100, 1
    )

    # Format analysis
    result["format_analysis"] = _check_formats(images_data)

    # Lazy loading summary
    lazy_count = sum(1 for img in images_data if img["lazy_loading"]["has_lazy_loading"])
    result["lazy_loading_analysis"] = {
        "images_with_lazy": lazy_count,
        "images_without_lazy": len(images_data) - lazy_count,
        "recommendation": (
            "Add loading='lazy' to below-the-fold images" 
            if lazy_count < len(images_data) // 2 
            else "Good lazy loading coverage"
        ),
    }

    # File size analysis (sample)
    result["file_size_analysis"] = _check_file_sizes(img_urls)

    # Calculate score
    score = 100

    # Alt text scoring
    if result["alt_coverage_pct"] < 50:
        score -= 25
    elif result["alt_coverage_pct"] < 80:
        score -= 10
    elif result["alt_coverage_pct"] < 100:
        score -= 3

    # Format scoring
    fmt = result["format_analysis"]
    if fmt.get("modern_format_count", 0) == 0 and fmt.get("legacy_format_count", 0) > 0:
        score -= 15
    elif fmt.get("legacy_format_count", 0) > fmt.get("modern_format_count", 0):
        score -= 5

    # File size scoring
    fs = result["file_size_analysis"]
    if fs.get("large_images"):
        score -= len(fs["large_images"]) * 5
    if fs.get("average_size_kb", 0) > 500:
        score -= 15
    elif fs.get("average_size_kb", 0) > 300:
        score -= 5

    # Responsive scoring
    responsive_count = sum(1 for img in images_data if img["responsive"]["is_responsive"])
    if responsive_count == 0 and len(images_data) > 1:
        score -= 10

    # Lazy loading scoring
    if lazy_count == 0 and len(images_data) > 3:
        score -= 5

    result["score"] = max(0, min(100, score))

    # Generate recommendations
    if result["images_without_alt"] > 0:
        result["recommendations"].append(
            f"Add descriptive alt text to {result['images_without_alt']} image(s)"
        )
    if not result["format_analysis"].get("modern_format_count"):
        result["recommendations"].append(
            "Convert images to WebP or AVIF format for better compression"
        )
    if responsive_count == 0:
        result["recommendations"].append(
            "Add srcset attribute for responsive images on different screen sizes"
        )
    result["recommendations"].append(
        "Add width and height attributes to prevent CLS (Cumulative Layout Shift)"
    )

    return result
