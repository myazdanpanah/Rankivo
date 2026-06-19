"""
SEO AI Tools - Batch Audit Module
Analyze multiple URLs from a CSV file and generate comparison reports.
"""
import csv
import io
import time
import concurrent.futures
from seo_audit import audit_url


def parse_csv_urls(csv_content: str) -> list[dict]:
    """
    Parse a CSV string containing URLs and optional keywords/page_type.
    Expected columns: url, keyword (optional), page_type (optional).
    Valid page_type values: homepage, product, blog, generic, auto.
    """
    reader = csv.DictReader(io.StringIO(csv_content))
    entries = []
    for row in reader:
        url = row.get("url", "").strip()
        keyword = row.get("keyword", "").strip() if "keyword" in row else ""
        page_type = row.get("page_type", "generic").strip() if "page_type" in row else "generic"
        if url:
            entries.append({"url": url, "keyword": keyword, "page_type": page_type})
    return entries


def batch_audit(urls: list[dict], max_workers: int = 3, delay: float = 1.0) -> list[dict]:
    """
    Audit multiple URLs concurrently.
    Each item in `urls` should be {"url": str, "keyword": str}.
    Returns a list of audit results.
    """
    results = []

    def _audit_entry(entry):
        result = audit_url(entry["url"], entry.get("keyword", ""), entry.get("page_type", "generic"))
        return result

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {}
        for entry in urls:
            future = executor.submit(_audit_entry, entry)
            futures[future] = entry
            time.sleep(delay)  # Stagger requests to avoid rate limiting

        for future in concurrent.futures.as_completed(futures):
            entry = futures[future]
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                results.append({
                    "url": entry["url"],
                    "error": str(e),
                    "score": 0,
                    "page_title": "",
                    "meta_description": "",
                    "word_count": 0,
                    "links": {"internal_count": 0, "external_count": 0},
                    "images": {"total": 0, "with_alt": 0, "without_alt": 0, "alt_coverage": 0},
                    "headings": {},
                    "issues": [],
                    "status_code": 0,
                })

    # Sort by score descending
    results.sort(key=lambda r: r.get("score", 0), reverse=True)
    return results


def generate_comparison_table(results: list[dict]) -> list[dict]:
    """
    Generate a flat comparison table from batch audit results.
    Returns list of dicts suitable for pd.DataFrame.
    """
    rows = []
    for r in results:
        if r.get("error") and not r.get("page_title"):
            rows.append({
                "URL": r.get("url", ""),
                "Status": "❌ Error",
                "Score": 0,
                "Title": r.get("error", "")[:60],
                "Title Length": 0,
                "Description": "",
                "Desc Length": 0,
                "Words": 0,
                "H1 Count": 0,
                "Internal Links": 0,
                "External Links": 0,
                "Images": 0,
                "Missing Alt": 0,
                "Issues": len(r.get("issues", [])),
            })
        else:
            h1_count = len(r.get("headings", {}).get("h1", []))
            rows.append({
                "URL": r.get("final_url", r.get("url", "")),
                "Score": r.get("score", 0),
                "Title": r.get("page_title", ""),
                "Title Length": len(r.get("page_title", "")),
                "Description": r.get("meta_description", ""),
                "Desc Length": len(r.get("meta_description", "")),
                "Words": r.get("word_count", 0),
                "H1 Count": h1_count,
                "Internal Links": r.get("links", {}).get("internal_count", 0),
                "External Links": r.get("links", {}).get("external_count", 0),
                "Images": r.get("images", {}).get("total", 0),
                "Missing Alt": r.get("images", {}).get("without_alt", 0),
                "Issues": len(r.get("issues", [])),
            })

    return rows


def generate_comparison_markdown(results: list[dict]) -> str:
    """Generate a Markdown comparison report."""
    lines = ["# Batch SEO Audit Report\n"]
    lines.append(f"**URLs Analyzed:** {len(results)}\n")

    # Summary table
    lines.append("## Summary\n")
    lines.append("| URL | Score | Words | Title | Issues |")
    lines.append("|-----|-------|-------|-------|--------|")
    for r in results:
        if r.get("error") and not r.get("page_title"):
            lines.append(f"| {r.get('url', '')} | ❌ Error | - | - | - |")
        else:
            url = r.get("final_url", r.get("url", ""))
            title = r.get("page_title", "")[:40]
            score = r.get("score", 0)
            words = r.get("word_count", 0)
            issues = len(r.get("issues", []))
            lines.append(f"| {url} | {score}/100 | {words} | {title} | {issues} |")

    # Top issues across all URLs
    lines.append("\n## Common Issues\n")
    issue_counter = {}
    for r in results:
        for issue in r.get("issues", []):
            key = f"[{issue['severity'].upper()}] {issue['message']}"
            issue_counter[key] = issue_counter.get(key, 0) + 1

    for issue_text, count in sorted(issue_counter.items(), key=lambda x: -x[1])[:10]:
        lines.append(f"- {issue_text} (found in {count} URLs)")

    return "\n".join(lines)


def generate_sample_csv() -> str:
    """Generate a sample CSV template for users."""
    return "url,keyword,page_type\nhttps://example.com,example keyword,homepage\nhttps://example.com/about,about us,generic\nhttps://example.com/product/widget,buy widget,product\nhttps://example.com/blog/seo-tips,seo tips,blog\n"
