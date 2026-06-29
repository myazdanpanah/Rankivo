"""
SEO AI Tools - Google Trends Module
Fetches trend data, interest over time, and related queries using pytrends.
"""
import json
from typing import Optional
from config import _safe_print


try:
    from pytrends.request import TrendReq as _TrendReqClass
    PYTRENDS_AVAILABLE = True
except ImportError:
    _TrendReqClass = None
    PYTRENDS_AVAILABLE = False


_trends_client = None


def _get_client():
    """Get or create a pytrends client."""
    global _trends_client
    if not PYTRENDS_AVAILABLE:
        return None
    if _trends_client is None:
        try:
            _trends_client = _TrendReqClass(hl='en-US', tz=360, retries=3, backoff_factor=0.5)
        except Exception as e:
            _safe_print(f"[google_trends] Failed to create client: {e}")
            return None
    return _trends_client


def get_interest_over_time(keywords: list[str], timeframe: str = "today 12-m", geo: str = "") -> dict:
    """
    Get interest over time for one or more keywords.
    
    Args:
        keywords: List of up to 5 keywords to compare
        timeframe: pytrends timeframe (e.g. "today 12-m", "today 3-m", "today 5-y", "all")
        geo: Geo location code (e.g. "US", "" for worldwide)
    
    Returns:
        dict with dates and values per keyword
    """
    client = _get_client()
    if not client:
        return {"error": "pytrends library not available. Install with: pip install pytrends"}

    if not keywords:
        return {"error": "At least one keyword is required"}

    kw_list = keywords[:5]  # pytrends max 5 at a time

    try:
        client.build_payload(kw_list, cat=0, timeframe=timeframe, geo=geo, gprop='')
        data = client.interest_over_time()
        
        if data.empty:
            return {"dates": [], "keywords": kw_list, "values": {}, "message": "No data available"}

        dates = data.index.strftime('%Y-%m-%d').tolist()
        values = {}
        for kw in kw_list:
            if kw in data.columns:
                values[kw] = data[kw].tolist()

        return {
            "dates": dates,
            "keywords": kw_list,
            "values": values,
            "is_partial": data.get('isPartial', False) if hasattr(data, 'get') else False,
        }
    except Exception as e:
        _safe_print(f"[google_trends] interest_over_time error: {e}")
        return {"error": str(e)}


def get_related_queries(keywords: list[str], timeframe: str = "today 12-m", geo: str = "") -> dict:
    """
    Get related queries (top & rising) for keywords.
    
    Args:
        keywords: List of up to 5 keywords
        timeframe: pytrends timeframe
        geo: Geo location code
    
    Returns:
        dict with top and rising queries per keyword
    """
    client = _get_client()
    if not client:
        return {"error": "pytrends library not available"}

    if not keywords:
        return {"error": "At least one keyword is required"}

    kw = keywords[0:1]  # related_queries works best with single keyword

    try:
        client.build_payload(kw, cat=0, timeframe=timeframe, geo=geo, gprop='')
        data = client.related_queries()

        result = {}
        for k in kw:
            k_data = data.get(k, {})
            top = k_data.get('top')
            rising = k_data.get('rising')

            result[k] = {
                "top": top.to_dict('records') if top is not None and not top.empty else [],
                "rising": rising.to_dict('records') if rising is not None and not rising.empty else [],
            }

        return result
    except Exception as e:
        _safe_print(f"[google_trends] related_queries error: {e}")
        return {"error": str(e)}


def get_trending_searches(geo: str = "US") -> list[dict]:
    """
    Get today's trending searches for a region.
    
    Args:
        geo: Geo code (e.g. "US", "IR", "GB")
    
    Returns:
        List of trending search entries
    """
    client = _get_client()
    if not client:
        return [{"error": "pytrends library not available"}]

    try:
        data = client.trending_searches(pn=geo)
        if data is not None and not data.empty:
            trending = []
            for _, row in data.iterrows():
                trending.append({"title": row.get(0, str(row.iloc[0])) if hasattr(row, 'get') else str(row.iloc[0])})
            return trending
        return []
    except Exception as e:
        _safe_print(f"[google_trends] trending_searches error: {e}")
        return [{"error": str(e)}]


def get_interest_by_region(keywords: list[str], timeframe: str = "today 12-m", geo: str = "", resolution: str = "COUNTRY") -> dict:
    """
    Get interest by region for keywords.
    
    Args:
        keywords: List of up to 5 keywords
        timeframe: pytrends timeframe
        geo: Geo location
        resolution: "COUNTRY", "REGION", "CITY", "DMA"
    
    Returns:
        dict with region data
    """
    client = _get_client()
    if not client:
        return {"error": "pytrends library not available"}

    if not keywords:
        return {"error": "At least one keyword is required"}

    kw_list = keywords[:5]

    try:
        client.build_payload(kw_list, cat=0, timeframe=timeframe, geo=geo, gprop='')
        data = client.interest_by_region(resolution=resolution, inc_low_vol=True, inc_geo_code=True)

        if data is not None and not data.empty:
            return json.loads(data.to_json(orient='records'))
        return {"message": "No region data available", "data": []}
    except Exception as e:
        _safe_print(f"[google_trends] interest_by_region error: {e}")
        return {"error": str(e)}


def check_availability() -> dict:
    """Check if pytrends is available."""
    client = _get_client()
    return {
        "available": client is not None,
        "library_installed": PYTRENDS_AVAILABLE,
        "message": "Google Trends is ready!" if client else "Install pytrends: pip install pytrends",
    }


# ──────────────────────────────────────────────
# Iran Province-Level Trends
# ──────────────────────────────────────────────

# Google Trends returns English region names for Iran provinces.
# This mapping provides English→Persian translation for display.
IRAN_PROVINCES_EN_FA = {
    "Tehran": "تهران",
    "Isfahan": "اصفهان",
    "Fars": "فارس",
    "Khorasan Razavi": "خراسان رضوی",
    "Khuzestan": "خوزستان",
    "West Azerbaijan": "آذربایجان غربی",
    "East Azerbaijan": "آذربایجان شرقی",
    "Alborz": "البرز",
    "Kerman": "کرمان",
    "Mazandaran": "مازندران",
    "Gilan": "گیلان",
    "Lorestan": "لرستان",
    "Kermanshah": "کرمانشاه",
    "Sistan and Baluchestan": "سیستان و بلوچستان",
    "Hormozgan": "هرمزگان",
    "Kurdistan": "کردستان",
    "Zanjan": "زنجان",
    "Hamadan": "همدان",
    "Markazi": "مرکزی",
    "Golestan": "گلستان",
    "Hamedan": "همدان",
    "Ilam": "ایلام",
    "Chaharmahal and Bakhtiari": "چهارمحال و بختیاری",
    "Kohgiluyeh and Boyer-Ahmad": "کهگیلویه و بویراحمد",
    "Khorasan South": "خراسان جنوبی",
    "Khorasan North": "خراسان شمالی",
    "Yazd": "یزد",
    "Qom": "قم",
    "Qazvin": "قزوین",
    "Semnan": "سمنان",
    "Bushehr": "بوشهر",
    "Ardabil": "اردبیل",
    "North Khorasan": "خراسان شمالی",
    "South Khorasan": "خراسان جنوبی",
    "Razavi Khorasan": "خراسان رضوی",
}

# Sorted list of top Iran provinces by population (for ranking display)
IRAN_TOP_PROVINCES = [
    "Tehran", "Isfahan", "Fars", "Khorasan Razavi", "Khuzestan",
    "West Azerbaijan", "East Azerbaijan", "Alborz", "Kerman", "Mazandaran",
    "Gilan", "Lorestan", "Kermanshah", "Sistan and Baluchestan", "Hormozgan",
    "Kurdistan", "Zanjan", "Hamedan", "Markazi", "Golestan",
]


def get_iran_province_trends(
    keywords: list[str],
    timeframe: str = "today 12-m",
) -> dict:
    """
    Get search interest by Iranian province for the given keywords.
    Uses Google Trends with geo="IR" and resolution="REGION".

    Returns:
        dict with:
          - provinces: list of {name_en, name_fa, score, rank} per keyword
          - top_provinces: top 5 provinces by search interest
          - recommendation: content targeting suggestion
          - search_volume_ranking: overall keyword ranking (0-100 scale)
    """
    client = _get_client()
    if not client:
        return {"error": "pytrends library not available"}

    if not keywords:
        return {"error": "At least one keyword is required"}

    kw_list = keywords[:5]
    results = {}

    for kw in kw_list:
        try:
            client.build_payload([kw], cat=0, timeframe=timeframe, geo="IR", gprop="")
            data = client.interest_by_region(
                resolution="REGION", inc_low_vol=True, inc_geo_code=True
            )

            if data is None or data.empty:
                results[kw] = {
                    "provinces": [],
                    "top_provinces": [],
                    "recommendation": f"داده‌ای برای '{kw}' در استان‌های ایران یافت نشد.",
                    "search_volume_ranking": 0,
                }
                continue

            # Extract and sort province data
            province_list = []
            for region_name, row_data in data.iterrows():
                score = int(row_data.iloc[0]) if hasattr(row_data, 'iloc') else int(row_data)
                if score > 0:
                    name_fa = IRAN_PROVINCES_EN_FA.get(region_name, region_name)
                    province_list.append({
                        "name_en": region_name.strip(),
                        "name_fa": name_fa,
                        "score": score,
                    })

            # Sort by score descending and assign ranks
            province_list.sort(key=lambda x: x["score"], reverse=True)
            for i, p in enumerate(province_list):
                p["rank"] = i + 1

            # Overall search volume ranking (0-100 scale)
            max_score = province_list[0]["score"] if province_list else 0
            search_volume_ranking = max_score  # Google Trends already gives 0-100

            # Top 5 provinces
            top_5 = province_list[:5]
            top_5_fa = [f"{p['name_fa']} ({p['score']})" for p in top_5]

            # Generate targeting recommendation in Persian
            if len(top_5) >= 3:
                top_names = "، ".join(p["name_fa"] for p in top_5[:3])
                recommendation = (
                    f"بیشترین جستجو برای '{kw}' در استان‌های {top_names} است. "
                    f"محتوای خود را برای مخاطبان این استان‌ها بهینه کنید. "
                    f"از کلمات کلیدی محلی و اصطلاحات منطقه‌ای استفاده کنید."
                )
            elif top_5:
                recommendation = (
                    f"استان {top_5[0]['name_fa']} بیشترین جستجو برای '{kw}' را دارد. "
                    f"محتوای هدفمند برای این منطقه تولید کنید."
                )
            else:
                recommendation = f"داده کافی برای توصیه هدف‌گیری استانی '{kw}' موجود نیست."

            results[kw] = {
                "provinces": province_list,
                "top_provinces": top_5,
                "recommendation": recommendation,
                "search_volume_ranking": search_volume_ranking,
            }

        except Exception as e:
            _safe_print(f"[google_trends] Iran province error for '{kw}': {e}")
            results[kw] = {
                "provinces": [],
                "top_provinces": [],
                "recommendation": f"خطا در دریافت داده استانی برای '{kw}'.",
                "search_volume_ranking": 0,
                "error": str(e),
            }

        # Rate limit between keywords
        time.sleep(1.0)

    return {"keywords": kw_list, "data": results}
