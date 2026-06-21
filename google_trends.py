"""
SEO AI Tools - Google Trends Module
Fetches trend data, interest over time, and related queries using pytrends.
"""
import traceback
import json
from typing import Optional

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
            print(f"[google_trends] Failed to create client: {e}")
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
        print(f"[google_trends] interest_over_time error: {e}")
        traceback.print_exc()
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
        print(f"[google_trends] related_queries error: {e}")
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
        print(f"[google_trends] trending_searches error: {e}")
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
        print(f"[google_trends] interest_by_region error: {e}")
        return {"error": str(e)}


def check_availability() -> dict:
    """Check if pytrends is available."""
    client = _get_client()
    return {
        "available": client is not None,
        "library_installed": PYTRENDS_AVAILABLE,
        "message": "Google Trends is ready!" if client else "Install pytrends: pip install pytrends",
    }
