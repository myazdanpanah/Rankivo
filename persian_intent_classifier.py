"""
Rankivo — Persian Search Intent Classifier
Enhanced classifier with comprehensive Persian/Farsi keyword patterns,
few-shot examples, and an Ollama-powered classification mode.

Training data and patterns based on Persian search behavior analysis.
"""
import re
import json
import time
import requests
from config import OLLAMA_BASE_URL, _safe_print, check_ollama


# ──────────────────────────────────────────────
# 1. Persian Search Intent Patterns (Rule-Based)
# ──────────────────────────────────────────────

# Each category has weighted patterns: (pattern, weight)
# Higher weight = stronger signal

PERSIAN_INTENT_PATTERNS = {
    "transactional": {
        "keywords": [
            # Purchase intent
            ("خرید", 10), ("خریدن", 10), ("سفارش", 9), ("سفارش دادن", 9),
            ("پرداخت", 8), ("پرداخت آنلاین", 9), ("پرداخت اینترنتی", 9),
            # Price/cost
            ("قیمت", 8), ("قیمت روز", 9), ("ارزان", 8), ("ارزان‌ترین", 9),
            ("گران", 6), ("تخفیف", 9), ("حراج", 8), ("تخفیف ویژه", 9),
            ("با تخفیف", 8), ("ارزان‌ترین", 9), ("مقرون به صرفه", 7),
            # Download/install
            ("دانلود", 8), ("دانلود رایگان", 9), ("نصب", 6),
            ("دریافت", 7), ("لینک دانلود", 9),
            # Subscription/order
            ("عضویت", 7), ("ثبت نام", 7), ("ثبت‌نام", 7),
            ("اشتراک", 7), ("خرید اشتراک", 9),
            # Product-specific
            ("فروش", 7), ("فروشگاه", 6), ("فروشگاه آنلاین", 8),
            ("کد تخفیف", 9), ("کوپن", 8), ("پیشنهاد ویژه", 8),
            ("پکیج", 6), ("بسته", 5),
        ],
        "regex": [
            r"(?:خرید|دانلود|سفارش|پرداخت|قیمت|ارزان|تخفیف|فروش)",
            r"(?:چقدر|多少钱|cost|price|how much)",
        ],
    },
    "navigational": {
        "keywords": [
            # Direct navigation
            ("ورود", 10), ("ورود به", 10), ("لاگین", 10), ("ورود به حساب", 10),
            ("سایت رسمی", 10), ("وب‌سایت رسمی", 10), ("آدرس سایت", 9),
            ("اپلیکیشن", 8), ("اپ", 7), ("اپلیکیشن رسمی", 9),
            # Brand/company
            ("بازار", 7), ("دیجی‌کالا", 10), ("آپارات", 10),
            ("نماشا", 10), ("بلیط", 7),
            # Official channels
            ("پشتیبانی", 7), ("تماس با ما", 8), ("شماره تماس", 8),
            ("آدرس دفتر", 8), ("دفتر مرکزی", 8),
            # Account management
            ("حساب کاربری", 9), ("پروفایل", 8), ("داشبورد", 8),
            ("پنل کاربری", 9), ("پنل مدیریت", 9),
        ],
        "regex": [
            r"(?:ورود|لاگین|سایت رسمی|اپلیکیشن|حساب کاربری)",
            r"^(?:com|ir|org|net)$",
        ],
    },
    "informational": {
        "keywords": [
            # Learning/education
            ("آموزش", 10), ("آموزشی", 9), ("آموختن", 8), ("یادگیری", 9),
            ("یاد بگیرم", 9), ("یاد بگیرید", 9),
            # Guide/tutorial
            ("راهنما", 9), ("راهنمای", 9), ("توضیح", 7),
            ("آموزش گام به گام", 10), ("قدم به قدم", 9),
            # How-to
            ("نحوه", 10), ("چگونه", 10), ("چطور", 10), ("چطوری", 10),
            ("روش", 8), ("روش انجام", 9), ("میشه", 6),
            ("می‌شود", 7), ("می شود", 7),
            # Definition/what is
            ("چیست", 10), ("چیست؟", 10), ("چیه", 8),
            ("تعریف", 9), ("تعریف کردن", 8),
            ("معنی", 8), ("معنای", 8),
            # Why
            ("چرا", 8), ("دلیل", 7), ("چرا که", 5),
            # Tips/advice
            ("نکات", 8), ("نکته", 7), ("نکته مهم", 8),
            ("پیشنهاد", 7), ("توصیه", 7), ("توصیه می‌کنم", 6),
            # Overview
            ("overview", 6), ("مرور", 5), ("معرفی", 8),
            ("معرفی کامل", 9),
            # General info
            ("اطلاعات", 7), ("درباره", 7), ("درباره چیست", 8),
        ],
        "regex": [
            r"(?:چیست|نحوه|چگونه|چطور|آموزش|راهنما|تعریف|معنی|چرا|نکات)",
            r"(?:how to|what is|why|guide|tutorial|tips)",
        ],
    },
    "commercial": {
        "keywords": [
            # Best/top
            ("بهترین", 10), ("بهترین‌ها", 10), ("برترین", 9),
            ("top", 7), ("best", 7),
            # Comparison
            ("مقایسه", 10), ("مقایسه کردن", 10), ("مقایسه‌ای", 9),
            ("تفاوت", 9), ("تفاوت بین", 10), ("فرق", 8),
            ("vs", 8), ("در مقابل", 8),
            # Reviews
            ("بررسی", 9), ("نقد", 8), ("نقد و بررسی", 10),
            ("نظرات کاربران", 9), ("نظر کاربران", 9),
            ("تجربه استفاده", 8), ("تجربه کاربری", 8),
            # Alternative
            ("جایگزین", 9), ("جایگزین‌های", 9), ("مشابه", 7),
            ("مشابه آن", 7), ("رقیب", 7),
            # Recommendation
            ("پیشنهاد", 7), ("پیشنهاد می‌دهم", 8),
            ("توصیه می‌کنم", 8), ("انتخاب", 7),
            ("انتخاب کردن", 7),
            # Ranking
            ("رتبه‌بندی", 8), ("لیست بهترین", 9),
            ("معرفی بهترین", 10),
        ],
        "regex": [
            r"(?:بهترین|مقایسه|تفاوت|بررسی|نقد|جایگزین|رتبه|لیست)",
            r"(?:best|vs|comparison|review|alternative|ranking|top)",
        ],
    },
}


# ──────────────────────────────────────────────
# 2. Persian Stop Words
# ──────────────────────────────────────────────

PERSIAN_STOP_WORDS = {
    "و", "در", "به", "از", "که", "این", "را", "با", "است", "برای",
    "آن", "یک", "خود", "تا", "کرد", "بر", "هم", "نیز", "گفت", "می",
    "شود", "شده", "بود", "دارد", "ها", "های", "شد", "یا", "اما",
    "باید", "پس", "اگر", "وقتی", "آنکه", "می‌شود", "می‌کند",
    "شد", "نه", "همه", "بیشتر", "کمتر", "خیلی", "حتی", "البته",
    "بله", "خب", "اوه", "هیچ", "هیچکدام",
}


# ──────────────────────────────────────────────
# 3. Classification Engine
# ──────────────────────────────────────────────

def _normalize_persian_text(text: str) -> str:
    """Normalize Persian text for classification."""
    try:
        from persian_nlp import normalize_persian
        return normalize_persian(text)
    except ImportError:
        text = text.replace("ي", "ی").replace("ك", "ک")
        text = text.replace("\u0640", "")  # remove tatweel
        return text


def classify_persian_intent_heuristic(keyword: str) -> dict:
    """
    Rule-based Persian search intent classifier with confidence scores.
    
    Returns dict with:
        - intent: the classified intent
        - confidence: 0.0 to 1.0
        - scores: breakdown by category
        - signals: matched keywords/patterns
    """
    keyword_lower = keyword.lower().strip()
    keyword_normalized = _normalize_persian_text(keyword_lower)
    
    scores = {}
    signals = {}
    
    for category, config in PERSIAN_INTENT_PATTERNS.items():
        score = 0
        matched = []
        
        # Check keyword matches
        for pattern, weight in config["keywords"]:
            if pattern in keyword_normalized:
                score += weight
                matched.append(f"kw:{pattern}")
        
        # Check regex matches
        for regex in config["regex"]:
            if re.search(regex, keyword_normalized, re.IGNORECASE):
                score += 5
                matched.append(f"re:{regex}")
        
        # Bonus for exact match at start
        for pattern, weight in config["keywords"]:
            if keyword_normalized.startswith(pattern):
                score += 3
                matched.append(f"start:{pattern}")
        
        scores[category] = score
        signals[category] = matched
    
    # Find winning category
    max_score = max(scores.values()) if scores else 0
    total_score = sum(scores.values())
    
    if max_score == 0:
        return {
            "intent": "informational",
            "confidence": 0.3,
            "scores": scores,
            "signals": {"fallback": ["no signals matched"]},
        }
    
    # Determine winner
    winner = max(scores, key=scores.get)
    confidence = min(max_score / 20.0, 1.0)  # normalize to 0-1
    
    # Check for mixed signals (e.g., "best product to buy")
    if total_score > 0:
        second_score = sorted(scores.values(), reverse=True)[1] if len(scores) > 1 else 0
        if second_score > 0 and second_score / max_score > 0.7:
            confidence *= 0.7  # lower confidence for mixed signals
    
    return {
        "intent": winner,
        "confidence": round(confidence, 2),
        "scores": scores,
        "signals": signals,
    }


# ──────────────────────────────────────────────
# 4. Few-Shot Examples for LLM Classification
# ──────────────────────────────────────────────

PERSIAN_FEW_SHOT_EXAMPLES = """
## مثال‌های آموزشی (Training Examples):

### تراکنشی (Transactional):
- "خرید آیفون ۱۶" → transactional
- "قیمت لپتاپ ایسوس" → transactional
- "دانلود تلگرام" → transactional
- "تخفیف دیجی‌کالا" → transactional
- "ارزان‌ترین هاست ایران" → transactional
- "سفارش آنلاین غذا" → transactional
- "کد تخفیف اسنپ‌فود" → transactional
- "عضویت نت‌فلیکس" → transactional

### هدایتی (Navigational):
- "ورود به جیمیل" → navigational
- "سایت رسمی دیجی‌کالا" → navigational
- "اپلیکیشن دیجی‌کالا" → navigational
- "حساب کاربری من" → navigational
- "پنل مدیریت وردپرس" → navigational
- "لاگین اینستاگرام" → navigational

### اطلاعاتی (Informational):
- "آموزش پایتون" → informational
- "چگونه وبلاگ بسازیم" → informational
- "نحوه نصب ویندوز ۱۱" → informational
- "seo چیست" → informational
- "تفاوت html و css" → informational
- "نکات عکاسی" → informational
- "معرفی کامل هوش مصنوعی" → informational
- "چرا ورزش مهم است" → informational

### تجاری (Commercial):
- "بهترین گوشی ۲۰۲۶" → commercial
- "مقایسه آیفون و سامسونگ" → commercial
- "بررسی تسلا مدل ۳" → commercial
- "جایگزین وردپرس" → commercial
- "نقد و بررسی آیپد پرو" → commercial
- "لیست بهترین کتاب‌های ۲۰۲۶" → commercial
- "فرق پایتون و جاوا" → commercial
"""

PERSIAN_LLM_SYSTEM_PROMPT = f"""شما یک متخصص طبقه‌بندی قصد جستجوی فارسی هستید.
کلمه کلیدی فارسی داده شده را در یکی از دسته‌بندی‌های زیر قرار دهید:

1. **transactional** (تراکنشی): کاربر می‌خواهد خرید/دانلود/عضویت/سفارش دهد
   - سیگنال‌ها: خرید، قیمت، ارزان، تخفیف، دانلود، سفارش، پرداخت
   
2. **navigational** (هدایتی): کاربر می‌خواهد سایت/اپلیکیشن/صفحه خاصی را پیدا کند
   - سیگنال‌ها: ورود، سایت رسمی، اپلیکیشن، حساب کاربری، لاگین
   
3. **informational** (اطلاعاتی): کاربر می‌خواهد چیزی یاد بگیرد یا اطلاعات کسب کند
   - سیگنال‌ها: آموزش، چگونه، چیست، راهنما، نکات، معرفی
   
4. **commercial** (تجاری): کاربر در حال مقایسه و بررسی گزینه‌ها قبل از خرید
   - سیگنال‌ها: بهترین، مقایسه، بررسی، تفاوت، جایگزین، لیست

{PERSIAN_FEW_SHOT_EXAMPLES}

规则:
- فقط نام دسته‌بندی را برگردانید (مثلاً: transactional)
- توضیح اضافی ندهید
- اگر مطمئن نیستید، informational برگردانید
- سیگنال‌های فرهنگی ایران را در نظر بگیرید
"""


# ──────────────────────────────────────────────
# 5. LLM-Powered Classification
# ──────────────────────────────────────────────

def classify_persian_intent_llm(keyword: str, model: str = "") -> dict:
    """
    Classify Persian search intent using Ollama LLM.
    Falls back to heuristic if LLM is unavailable.
    """
    # Try heuristic first for instant results
    heuristic_result = classify_persian_intent_heuristic(keyword)
    
    # If heuristic has high confidence, use it directly
    if heuristic_result["confidence"] >= 0.7:
        heuristic_result["method"] = "heuristic"
        return heuristic_result
    
    # Try LLM for ambiguous cases
    if not check_ollama():
        heuristic_result["method"] = "heuristic"
        return heuristic_result
    
    try:
        model_name = model or "rankivo-persian-intent"
        payload = {
            "model": model_name,
            "prompt": f"کلمه کلیدی فارسی زیر را طبقه‌بندی کنید:\n\n\"{keyword}\"\n\nفقط نام دسته‌بندی را برگردانید.",
            "system": PERSIAN_LLM_SYSTEM_PROMPT,
            "stream": False,
        }
        resp = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json=payload,
            timeout=30,
        )
        resp.raise_for_status()
        result_text = resp.json()["response"].strip().lower()
        
        # Parse response
        valid_intents = {"transactional", "navigational", "informational", "commercial"}
        for intent in valid_intents:
            if intent in result_text:
                return {
                    "intent": intent,
                    "confidence": 0.85,
                    "scores": heuristic_result["scores"],
                    "signals": {"llm": [f"LLM classified as {intent}"]},
                    "method": "llm",
                }
        
        # LLM gave invalid response, use heuristic
        heuristic_result["method"] = "heuristic"
        return heuristic_result
        
    except Exception as e:
        _safe_print(f"[persian_intent] LLM classification error: {e}")
        heuristic_result["method"] = "heuristic"
        return heuristic_result


def classify_persian_intents_batch(keywords: list[str], model: str = "") -> dict[str, str]:
    """
    Classify intent for multiple Persian keywords.
    Uses batch LLM prompting when available.
    Returns dict mapping keyword -> intent string.
    """
    if not keywords:
        return {}
    
    results = {}
    
    # Split into high-confidence heuristic and ambiguous
    ambiguous = []
    for kw in keywords:
        result = classify_persian_intent_heuristic(kw)
        if result["confidence"] >= 0.7:
            results[kw] = result["intent"]
        else:
            ambiguous.append(kw)
    
    # Classify ambiguous ones via LLM if available
    if ambiguous:
        if check_ollama():
            try:
                for kw in ambiguous:
                    result = classify_persian_intent_llm(kw, model=model)
                    results[kw] = result["intent"]
                    time.sleep(0.3)
            except Exception:
                for kw in ambiguous:
                    if kw not in results:
                        results[kw] = classify_persian_intent_heuristic(kw)["intent"]
        else:
            for kw in ambiguous:
                results[kw] = classify_persian_intent_heuristic(kw)["intent"]
    
    return results


# ──────────────────────────────────────────────
# 6. Training Data Export (for fine-tuning)
# ──────────────────────────────────────────────

def export_training_data(format: str = "jsonl") -> list[dict] | str:
    """
    Export Persian intent classification training data.
    Useful for fine-tuning models or creating evaluation datasets.
    
    Returns list of dicts (jsonl=False) or JSONL string (jsonl=True).
    """
    training_examples = [
        # Transactional
        {"text": "خرید آیفون ۱۶ پرو مکس", "intent": "transactional"},
        {"text": "قیمت لپتاپ ایسوس روبوک", "intent": "transactional"},
        {"text": "دانلود تلگرام برای اندروید", "intent": "transactional"},
        {"text": "تخفیف دیجی‌کالا امروز", "intent": "transactional"},
        {"text": "ارزان‌ترین هاست ایران", "intent": "transactional"},
        {"text": "سفارش آنلاین غذا ریحون", "intent": "transactional"},
        {"text": "کد تخفیف اسنپ‌فود", "intent": "transactional"},
        {"text": "عضویت نت‌فلیکس ایران", "intent": "transactional"},
        {"text": "پرداخت قبض آب", "intent": "transactional"},
        {"text": "خرید اشتراک ویمئو", "intent": "transactional"},
        {"text": "قیمت روز دلار", "intent": "transactional"},
        {"text": "حراج تابستانی زارا", "intent": "transactional"},
        {"text": "دانلود رایگان کتاب", "intent": "transactional"},
        {"text": "نصب اینستاگرام", "intent": "transactional"},
        {"text": "خرید شارژ ایرانسل", "intent": "transactional"},
        
        # Navigational
        {"text": "ورود به جیمیل", "intent": "navigational"},
        {"text": "سایت رسمی دیجی‌کالا", "intent": "navigational"},
        {"text": "اپلیکیشن دیجی‌کالا", "intent": "navigational"},
        {"text": "حساب کاربری من در بانک ملی", "intent": "navigational"},
        {"text": "پنل مدیریت وردپرس", "intent": "navigational"},
        {"text": "لاگین اینستاگرام", "intent": "navigational"},
        {"text": "ورود به سامانه ثبت‌نام", "intent": "navigational"},
        {"text": "وب‌سایت رسمی دانشگاه تهران", "intent": "navigational"},
        {"text": "اپلیکیشن آپ", "intent": "navigational"},
        {"text": "داشبورد مدیریتی", "intent": "navigational"},
        {"text": "پروفایل لینکدین من", "intent": "navigational"},
        {"text": "شماره تماس پشتیبانی ایرانسل", "intent": "navigational"},
        {"text": "آدرس دفتر مرکزی گوگل", "intent": "navigational"},
        {"text": "اپلیکیشن رسمی روبیکا", "intent": "navigational"},
        {"text": "پنل کاربری هاست ایران", "intent": "navigational"},
        
        # Informational
        {"text": "آموزش پایتون از صفر", "intent": "informational"},
        {"text": "چگونه وبلاگ بسازیم", "intent": "informational"},
        {"text": "نحوه نصب ویندوز ۱۱", "intent": "informational"},
        {"text": "سئو چیست و چگونه کار می‌کند", "intent": "informational"},
        {"text": "تفاوت html و css چیست", "intent": "informational"},
        {"text": "نکات عکاسی با موبایل", "intent": "informational"},
        {"text": "معرفی کامل هوش مصنوعی", "intent": "informational"},
        {"text": "چرا ورزش مهم است", "intent": "informational"},
        {"text": "آموزش فتوشاپ مبتدی", "intent": "informational"},
        {"text": "راهنمای خرید لپتاپ", "intent": "informational"},
        {"text": "معنی کلمه آگاهی", "intent": "informational"},
        {"text": "تعریف بازاریابی دیجیتال", "intent": "informational"},
        {"text": "چطور زبان انگلیسی یاد بگیریم", "intent": "informational"},
        {"text": "روش تهیه قهوه اسپرسو", "intent": "informational"},
        {"text": "نکات مهم سفر به اروپا", "intent": "informational"},
        
        # Commercial
        {"text": "بهترین گوشی ۲۰۲۶", "intent": "commercial"},
        {"text": "مقایسه آیفون و سامسونگ", "intent": "commercial"},
        {"text": "بررسی تسلا مدل ۳", "intent": "commercial"},
        {"text": "جایگزین وردپرس", "intent": "commercial"},
        {"text": "نقد و بررسی آیپد پرو", "intent": "commercial"},
        {"text": "لیست بهترین کتاب‌های ۲۰۲۶", "intent": "commercial"},
        {"text": "فرق پایتون و جاوا", "intent": "commercial"},
        {"text": "بهترین اپلیکیشن‌های ایرانی", "intent": "commercial"},
        {"text": "مقایسه هاست ایران و خارج", "intent": "commercial"},
        {"text": "top 10 گوشی بازار ایران", "intent": "commercial"},
        {"text": "بررسی و نقد دوربین کانن", "intent": "commercial"},
        {"text": "بهترین رستوران‌های تهران", "intent": "commercial"},
        {"text": "تفاوت کره و مargarine", "intent": "commercial"},
        {"text": "انتخاب بهترین سیستم عامل", "intent": "commercial"},
        {"text": "لیست مقایسه‌ای خودروهای ۲۰۲۶", "intent": "commercial"},
    ]
    
    if format == "jsonl":
        lines = []
        for ex in training_examples:
            lines.append(json.dumps(ex, ensure_ascii=False))
        return "\n".join(lines)
    
    return training_examples


# ──────────────────────────────────────────────
# 7. Status / Health Check
# ──────────────────────────────────────────────

def get_persian_classifier_status() -> dict:
    """Check Persian intent classifier capabilities."""
    # Test heuristic
    test_result = classify_persian_intent_heuristic("خرید آیفون")
    heuristic_ok = test_result["intent"] == "transactional"
    
    # Test LLM
    llm_ok = check_ollama()
    
    # Count patterns
    total_patterns = sum(
        len(config["keywords"]) for config in PERSIAN_INTENT_PATTERNS.values()
    )
    total_regex = sum(
        len(config["regex"]) for config in PERSIAN_INTENT_PATTERNS.values()
    )
    
    return {
        "heuristic_available": True,
        "heuristic_test_passed": heuristic_ok,
        "llm_available": llm_ok,
        "total_keyword_patterns": total_patterns,
        "total_regex_patterns": total_regex,
        "categories": list(PERSIAN_INTENT_PATTERNS.keys()),
        "training_examples_count": 60,
    }
