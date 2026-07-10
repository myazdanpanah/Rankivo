"""
Rankivo — SPA Renderer Module
Renders JavaScript-heavy pages using Playwright headless Chromium.
Falls back to standard requests if Playwright is not installed.
"""
import os
import time
import requests
from urllib.parse import urlparse
from config import REQUEST_TIMEOUT, USER_AGENTS, _safe_print, random_ua
import random




# ──────────────────────────────────────────────
# Playwright Availability Check
# ──────────────────────────────────────────────

_playwright_available = None


def is_playwright_available() -> bool:
    """Check if Playwright is installed and Chromium is available."""
    global _playwright_available
    if _playwright_available is not None:
        return _playwright_available
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            browser.close()
        _playwright_available = True
    except Exception:
        _playwright_available = False
    return _playwright_available


# ──────────────────────────────────────────────
# SPA Detection Heuristics
# ──────────────────────────────────────────────

def _is_likely_spa(html: str) -> bool:
    """
    Detect if a page is likely a Single Page Application.
    Checks for common SPA indicators in the HTML.
    """
    html_lower = html.lower()

    # Empty root div (React/Vue/Angular mount point)
    spa_indicators = [
        '<div id="root"></div>',
        '<div id="app"></div>',
        '<div id="__next"></div>',
        '<div id="__nuxt"></div>',
        '<div id="svelte"></div>',
        '<div id="app-root"></div>',
    ]
    for indicator in spa_indicators:
        if indicator in html_lower:
            return True

    # Single bundle script pattern
    if html_lower.count("<script") <= 3 and 'src="/static/js/' in html_lower:
        return True

    # Framework detection
    framework_hints = [
        'react', 'next', 'vue', 'nuxt', 'angular', 'svelte',
        '__NEXT_DATA__', '__NUXT__', 'webpackJsonp',
    ]
    hint_count = sum(1 for h in framework_hints if h in html_lower)
    if hint_count >= 2:
        return True

    # Very little content (likely client-rendered)
    from bs4 import BeautifulSoup
    try:
        soup = BeautifulSoup(html, "lxml")
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()
        text = soup.get_text(strip=True)
        if len(text) < 200:
            return True
    except Exception:
        pass

    return False


# ──────────────────────────────────────────────
# Playwright Rendering
# ──────────────────────────────────────────────

def render_with_playwright(
    url: str,
    wait_ms: int = 3000,
    timeout_ms: int = 30000,
) -> dict:
    """
    Render a page using Playwright headless Chromium.
    Returns the fully-rendered HTML after JavaScript execution.
    """
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-setuid-sandbox"],
            )
            context = browser.new_context(
                user_agent=random_ua(),
                viewport={"width": 1920, "height": 1080},
            )
            page = context.new_page()

            # Navigate and wait for network idle
            response = page.goto(
                url,
                wait_until="networkidle",
                timeout=timeout_ms,
            )

            # Additional wait for dynamic content
            page.wait_for_timeout(wait_ms)

            # Get rendered HTML
            html = page.content()
            final_url = page.url

            # Extract metadata
            title = page.title()
            meta_desc = page.evaluate("""
                () => {
                    const meta = document.querySelector('meta[name="description"]');
                    return meta ? meta.getAttribute('content') : '';
                }
            """)

            browser.close()

            return {
                "success": True,
                "method": "playwright",
                "html": html,
                "final_url": final_url,
                "title": title,
                "meta_description": meta_desc,
                "status_code": response.status if response else None,
            }

    except ImportError:
        return {
            "success": False,
            "method": "playwright",
            "error": "Playwright not installed. Run: pip install playwright && playwright install chromium",
        }
    except Exception as e:
        return {
            "success": False,
            "method": "playwright",
            "error": str(e),
        }


# ──────────────────────────────────────────────
# Fallback: Standard HTTP Fetch
# ──────────────────────────────────────────────

def render_with_requests(url: str) -> dict:
    """Standard HTTP fetch fallback when Playwright is not available."""
    try:
        headers = {"User-Agent": random_ua()}
        resp = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT, allow_redirects=True)

        return {
            "success": True,
            "method": "requests",
            "html": resp.text,
            "final_url": resp.url,
            "title": "",
            "meta_description": "",
            "status_code": resp.status_code,
            "note": "Standard HTTP fetch — JavaScript content not rendered",
        }
    except Exception as e:
        return {
            "success": False,
            "method": "requests",
            "error": str(e),
        }


# ──────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────

def render_page(
    url: str,
    force_playwright: bool = False,
    auto_detect: bool = True,
    wait_ms: int = 3000,
) -> dict:
    """
    Smart page renderer that auto-detects SPAs and uses the best method.
    
    Args:
        url: The URL to render
        force_playwright: Always use Playwright (skip detection)
        auto_detect: Auto-detect if page needs JS rendering
        wait_ms: Extra wait time for Playwright (ms)
    
    Returns:
        dict with rendered HTML, metadata, and method used
    """
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    # If Playwright not available, always use requests
    if not is_playwright_available() and not force_playwright:
        result = render_with_requests(url)
        result["playwright_available"] = False
        return result

    if force_playwright:
        result = render_with_playwright(url, wait_ms=wait_ms)
        result["playwright_available"] = True
        return result

    # Auto-detect: first fetch raw HTML, check if SPA
    if auto_detect:
        try:
            headers = {"User-Agent": random_ua()}
            resp = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT, allow_redirects=True)
            raw_html = resp.text

            if _is_likely_spa(raw_html):
                _safe_print(f"[spa_renderer] SPA detected for {url}, rendering with Playwright...")
                result = render_with_playwright(url, wait_ms=wait_ms)
                result["detected_spa"] = True
                result["playwright_available"] = True
                return result
            else:
                return {
                    "success": True,
                    "method": "requests",
                    "html": raw_html,
                    "final_url": resp.url,
                    "detected_spa": False,
                    "playwright_available": True,
                    "status_code": resp.status_code,
                }
        except Exception as e:
            # If requests fails, try Playwright as fallback
            result = render_with_playwright(url, wait_ms=wait_ms)
            result["playwright_available"] = True
            return result

    # Default: try Playwright
    result = render_with_playwright(url, wait_ms=wait_ms)
    result["playwright_available"] = True
    return result


def get_status() -> dict:
    """Check SPA renderer capabilities."""
    return {
        "playwright_available": is_playwright_available(),
        "auto_detect": True,
        "supported_frameworks": ["React", "Vue", "Angular", "Svelte", "Next.js", "Nuxt.js"],
    }
