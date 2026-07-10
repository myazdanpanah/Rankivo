"""
Rankivo — Strategic SEO Planning Module
Generates industry-specific SEO strategies: SaaS, Local, E-commerce, Publisher, Agency.
"""
import re
from datetime import datetime  # noqa: F401


# ──────────────────────────────────────────────
# Industry Templates
# ──────────────────────────────────────────────

INDUSTRY_STRATEGIES = {
    "saas": {
        "label": "SaaS / Software",
        "icon": "💻",
        "focus_areas": [
            "Product-led SEO (feature pages, use cases)",
            "Comparison and alternative pages",
            "Integration/partner pages",
            "Documentation and help center",
            "Pricing page optimization",
        ],
        "content_types": [
            {"type": "Landing Pages", "priority": "high", "desc": "Feature pages, use case pages, industry pages"},
            {"type": "Comparison Pages", "priority": "high", "desc": "vs pages, alternatives pages, competitor comparisons"},
            {"type": "Blog Content", "priority": "medium", "desc": "How-to guides, thought leadership, product updates"},
            {"type": "Documentation", "priority": "medium", "desc": "API docs, guides, tutorials for technical SEO"},
            {"type": "Case Studies", "priority": "medium", "desc": "Customer success stories for trust and long-tail"},
        ],
        "schema_types": ["Organization", "SoftwareApplication", "FAQPage", "HowTo"],
        "kpis": [
            "Organic signups (trial/demo requests)",
            "Feature page rankings for high-intent keywords",
            "Comparison page traffic vs competitors",
            "Documentation page engagement",
        ],
        "phases": [
            {"phase": 1, "timeline": "Month 1-2", "tasks": ["Technical audit", "Keyword research", "Competitor analysis", "Content gap analysis"]},
            {"phase": 2, "timeline": "Month 2-4", "tasks": ["Feature page creation", "Comparison pages", "Schema implementation", "Internal linking"]},
            {"phase": 3, "timeline": "Month 4-6", "tasks": ["Blog content calendar", "Link building", "Documentation optimization", "A/B testing"]},
            {"phase": 4, "timeline": "Month 6+", "tasks": ["Scale winning content", "International expansion", "Advanced schema", "AI optimization"]},
        ],
    },
    "local": {
        "label": "Local Business",
        "icon": "📍",
        "focus_areas": [
            "Google Business Profile optimization",
            "Local citations and NAP consistency",
            "Review management and generation",
            "Local content and landing pages",
            "Map pack visibility",
        ],
        "content_types": [
            {"type": "Location Pages", "priority": "high", "desc": "City/neighborhood landing pages with local content"},
            {"type": "Service Pages", "priority": "high", "desc": "Individual service pages with local schema"},
            {"type": "Blog Posts", "priority": "medium", "desc": "Local news, events, community involvement"},
            {"type": "FAQ Pages", "priority": "medium", "desc": "Common customer questions with local context"},
            {"type": "About/Team Pages", "priority": "low", "desc": "Team bios, history, values for E-E-A-T"},
        ],
        "schema_types": ["LocalBusiness", "Review", "AggregateRating", "FAQPage"],
        "kpis": [
            "Google Business Profile views and actions",
            "Map pack rankings for local keywords",
            "Review count and average rating",
            "Local landing page traffic",
        ],
        "phases": [
            {"phase": 1, "timeline": "Month 1", "tasks": ["GBP audit and optimization", "NAP audit", "Competitor local analysis", "Citation building"]},
            {"phase": 2, "timeline": "Month 2-3", "tasks": ["Location page creation", "Review generation strategy", "Local schema", "Content creation"]},
            {"phase": 3, "timeline": "Month 3-6", "tasks": ["Link building", "Content scaling", "Review management", "Local PR"]},
            {"phase": 4, "timeline": "Month 6+", "tasks": ["Multi-location expansion", "Advanced analytics", "Competitive monitoring", "AI optimization"]},
        ],
    },
    "ecommerce": {
        "label": "E-commerce",
        "icon": "🛒",
        "focus_areas": [
            "Product page optimization",
            "Category page SEO",
            "Product schema and rich results",
            "Internal linking and faceted navigation",
            "Content marketing (guides, reviews)",
        ],
        "content_types": [
            {"type": "Product Pages", "priority": "high", "desc": "Unique descriptions, images, schema, reviews"},
            {"type": "Category Pages", "priority": "high", "desc": "Optimized category descriptions and filters"},
            {"type": "Buying Guides", "priority": "medium", "desc": "How to choose, comparison, best-of lists"},
            {"type": "Blog Content", "priority": "medium", "desc": "How-to, trends, industry news"},
            {"type": "FAQ/Support", "priority": "low", "desc": "Shipping, returns, sizing, compatibility"},
        ],
        "schema_types": ["Product", "Offer", "AggregateRating", "Review", "BreadcrumbList"],
        "kpis": [
            "Product page organic traffic",
            "Rich result impressions (stars, price)",
            "Category page rankings",
            "Revenue from organic search",
        ],
        "phases": [
            {"phase": 1, "timeline": "Month 1-2", "tasks": ["Technical audit", "Product schema", "Category optimization", "Crawl budget analysis"]},
            {"phase": 2, "timeline": "Month 2-4", "tasks": ["Product description rewrite", "Internal linking", "Image optimization", "Review collection"]},
            {"phase": 3, "timeline": "Month 4-6", "tasks": ["Content marketing", "Link building", "Faceted nav optimization", "A/B testing"]},
            {"phase": 4, "timeline": "Month 6+", "tasks": ["International expansion", "Advanced schema", "Programmatic SEO", "AI optimization"]},
        ],
    },
    "publisher": {
        "label": "Publisher / Media",
        "icon": "📰",
        "focus_areas": [
            "Content quality and E-E-A-T",
            "Topical authority building",
            "Featured snippet optimization",
            "Content freshness and updates",
            "Core Web Vitals",
        ],
        "content_types": [
            {"type": "In-Depth Articles", "priority": "high", "desc": "Comprehensive, authoritative content (2000+ words)"},
            {"type": "News Articles", "priority": "high", "desc": "Timely, factual reporting with NewsArticle schema"},
            {"type": "How-To Guides", "priority": "medium", "desc": "Step-by-step guides with structured headings"},
            {"type": "Listicles", "priority": "medium", "desc": "Best-of lists, rankings, roundups"},
            {"type": "Opinion/Analysis", "priority": "low", "desc": "Expert takes, industry analysis"},
        ],
        "schema_types": ["Article", "NewsArticle", "BlogPosting", "FAQPage"],
        "kpis": [
            "Organic traffic growth",
            "Featured snippet captures",
            "E-E-A-T score improvements",
            "Content freshness metrics",
        ],
        "phases": [
            {"phase": 1, "timeline": "Month 1", "tasks": ["Content audit", "Technical SEO", "E-E-A-T analysis", "Competitor content analysis"]},
            {"phase": 2, "timeline": "Month 2-3", "tasks": ["Content calendar", "Topical cluster planning", "Schema optimization", "Internal linking"]},
            {"phase": 3, "timeline": "Month 3-6", "tasks": ["Content production", "Link building", "Featured snippet targeting", "Content updates"]},
            {"phase": 4, "timeline": "Month 6+", "tasks": ["Scale production", "International", "AI optimization", "Advanced analytics"]},
        ],
    },
    "agency": {
        "label": "Agency / Services",
        "icon": "🏢",
        "focus_areas": [
            "Service page optimization",
            "Case study and portfolio SEO",
            "Local and national visibility",
            "Thought leadership content",
            "Lead generation optimization",
        ],
        "content_types": [
            {"type": "Service Pages", "priority": "high", "desc": "Individual service pages with clear CTAs"},
            {"type": "Case Studies", "priority": "high", "desc": "Client success stories with measurable results"},
            {"type": "Industry Pages", "priority": "medium", "desc": "Vertical-specific landing pages"},
            {"type": "Blog/Insights", "priority": "medium", "desc": "Thought leadership, guides, industry trends"},
            {"type": "About/Team", "priority": "low", "desc": "Team expertise, company story, certifications"},
        ],
        "schema_types": ["Organization", "Service", "FAQPage", "Review"],
        "kpis": [
            "Lead form submissions from organic",
            "Service page rankings",
            "Case study engagement",
            "Brand search volume",
        ],
        "phases": [
            {"phase": 1, "timeline": "Month 1", "tasks": ["Website audit", "Competitor analysis", "Keyword research", "Content gap analysis"]},
            {"phase": 2, "timeline": "Month 2-3", "tasks": ["Service page optimization", "Case study creation", "Schema implementation", "Internal linking"]},
            {"phase": 3, "timeline": "Month 3-6", "tasks": ["Content marketing", "Link building", "Thought leadership", "Lead optimization"]},
            {"phase": 4, "timeline": "Month 6+", "tasks": ["Scale content", "Advanced analytics", "AI optimization", "International"]},
        ],
    },
}


# ──────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────

def generate_seo_plan(industry: str = "saas") -> dict:
    """
    Generate a strategic SEO plan for an industry type.
    
    Args:
        industry: One of 'saas', 'local', 'ecommerce', 'publisher', 'agency'
    
    Returns:
        Complete SEO strategy with phases, content types, and KPIs
    """
    strategy = INDUSTRY_STRATEGIES.get(industry, INDUSTRY_STRATEGIES["saas"])

    plan = {
        "industry": industry,
        "label": strategy["label"],
        "icon": strategy["icon"],
        "generated_at": datetime.now().isoformat(),

        "focus_areas": strategy["focus_areas"],
        "content_types": strategy["content_types"],
        "recommended_schema": strategy["schema_types"],
        "kpis": strategy["kpis"],

        "implementation_phases": strategy["phases"],

        "quick_wins": [
            "Fix all critical technical SEO issues (broken links, missing meta tags)",
            "Add/improve schema markup on key pages",
            "Optimize title tags and meta descriptions for top 20 pages",
            "Fix Core Web Vitals issues (LCP, CLS, INP)",
            "Add internal links from high-authority pages to priority pages",
        ],

        "monthly_checklist": [
            "Run technical SEO audit",
            "Monitor keyword rankings",
            "Analyze organic traffic trends",
            "Review and respond to new reviews (local)",
            "Publish 4-8 new content pieces",
            "Build 5-10 quality backlinks",
            "Update and refresh existing content",
            "Monitor competitor changes",
        ],
    }

    return plan


def get_available_plans() -> list[dict]:
    """Get list of available industry plans."""
    return [
        {
            "id": key,
            "label": val["label"],
            "icon": val["icon"],
            "focus_count": len(val["focus_areas"]),
        }
        for key, val in INDUSTRY_STRATEGIES.items()
    ]
