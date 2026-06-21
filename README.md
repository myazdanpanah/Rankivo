# 🔍 Rankivo — SEO AI Tools

A powerful, all-in-one Python SEO toolkit with a **modern web dashboard**. Research keywords, build content clusters, generate AI articles, audit websites, track performance, analyze Google Trends & Bing SEO, and plan your editorial calendar — all from free sources with a pluggable AI backend.

![Python](https://img.shields.io/badge/Python-3.10+-blue) ![Flask](https://img.shields.io/badge/Flask-3.0+-green) ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-optional-blue) ![License](https://img.shields.io/badge/License-MIT-green)

---

## ✨ Features

| Feature | Description |
|---|---|
| **📊 Keyword Research** | Google autocomplete suggestions, modifier expansion, People Also Ask, related searches, SERP analysis, search intent classification |
| **🗺️ Pillar-Cluster Map** | Auto-groups keywords into topic clusters, identifies pillar vs. cluster articles, generates a full content plan with interactive charts |
| **✍️ Article Generator** | Creates full SEO-optimized articles (Markdown) with H1/H3 structure, keyword placement, internal link suggestions |
| **🌐 Multi-Language Articles** | Generate articles in English or Persian (Farsi) with locale-aware prompts and SEO conventions |
| **📦 Batch Article Generation** | Generate multiple articles from a content plan in a single request |
| **🔄 Unified Pipeline** | One-click automated pipeline: Keyword Research → Pillar-Cluster → AI Analysis → Content Plan with priority scoring |
| **🔍 SEO Audit** | Analyzes any URL — meta tags, headings hierarchy, word count, keyword density, internal/external links, image alt text, SEO score (0-100) |
| **🏷️ Page-Type Audit** | Homepage, Product, Blog, and Generic page audits with auto-detection and page-type-specific scoring weights |
| **📋 Batch Audit** | Upload a CSV of URLs, audit them concurrently, get comparison tables and charts |
| **📈 Keyword Tracking** | Save keyword research snapshots over time, visualize trends, persist data in PostgreSQL or SQLite |
| **📅 Content Calendar** | Generate editorial timelines from pillar-cluster plans, track status, manage deadlines |
| **🧠 AI Recommendations** | AI-powered SEO recommendations that analyze audit results and suggest specific fixes |
| **📈 Google Trends** | Interest over time, related queries, trending searches, and interest by region via pytrends |
| **🔵 Bing SEO** | Bing-specific SEO analysis, index status check, URL submission, Bing trends dashboard |
| **🔔 Notifications** | Email and Slack webhook alerts for upcoming content calendar deadlines |
| **📜 Audit History** | Full audit history stored in the database for trend analysis |
| **🔐 User Management** | Multi-user support with admin/user roles, password management, database-backed authentication |
| **⚙️ Settings** | Database-backed application settings with admin-only management |
| **📄 PDF Export** | One-click PDF audit report generation with full SEO breakdown |
| **📊 CSV Export** | Download keyword research data as CSV with keyword, source, and intent columns |

---

## 🚀 Quick Start

### 1. Clone & install

```bash
git clone https://github.com/myazdanpanah/Rankivo.git
cd Rankivo
pip install -r requirements.txt
```

### 2. Configure (optional)

```bash
cp .env.example .env
# Edit .env with your API keys and settings
```

### 3. Run

**Windows (recommended):**
```
Double-click start.bat
```

**Cross-platform:**
```bash
python app.py
```

Opens at **http://localhost:5500**

**Default login:** `admin` / `rankivo`

---

## ⚙️ Configuration

### Authentication

By default, the dashboard is protected with a database-backed login system with role-based access:

| Setting | Default | Description |
|---|---|---|
| `ADMIN_USERNAME` | `admin` | Login username |
| `ADMIN_PASSWORD` | `rankivo` | Login password |
| `SECRET_KEY` | `rankivo-change-me-in-production` | Token signing key (set a stable value in production) |

Set via environment variables or in `.env`:

```bash
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your-secure-password
SECRET_KEY=your-random-secret-key
```

### AI Providers

| Provider | Cost | Setup |
|---|---|---|
| **Ollama** | Free | Install [Ollama](https://ollama.ai), run `ollama pull llama3` |
| **OpenAI** | ~$0.01/article | Set `OPENAI_API_KEY` in `.env` |
| **Claude** | ~$0.01/article | Set `ANTHROPIC_API_KEY` in `.env` |
| **Gemini** | Free tier available | Set `GOOGLE_API_KEY` in `.env` |

### Database

Rankivo supports **PostgreSQL** (production) with automatic **SQLite** fallback (local development).

**SQLite (default, no setup needed):**
- Data stored in `data/rankivo.db`
- Works out of the box

**PostgreSQL (recommended for production):**
```bash
# Set in .env
DATABASE_URL=postgresql://user:password@localhost:5432/rankivo
```

Tables are auto-created on first run:
- `keyword_snapshots` — keyword tracking history
- `calendar_events` — content calendar events
- `audit_history` — SEO audit results
- `users` — user accounts with roles
- `settings` — application settings

### Google Trends

Google Trends integration uses the `pytrends` library (no API key required):

```bash
# Optional: configure locale and timezone
GOOGLE_TRENDS_HL=en-US
GOOGLE_TRENDS_TZ=360
```

### Bing SEO

Bing SEO analysis works without an API key for on-page checks. For index status and URL submission:

```bash
BING_API_KEY=your-bing-webmaster-api-key
```

### Language Support

Generate articles in multiple languages:

| Code | Language |
|---|---|
| `en` | English (default) |
| `fa` | فارسی (Persian/Farsi) |

```bash
DEFAULT_LANGUAGE=en
```

### Notifications

**Email (SMTP):**
```bash
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM=your-email@gmail.com
```

**Slack:**
```bash
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/T.../B.../xxx
```

---

## 📁 Project Structure

```
Rankivo/
├── app.py                  # Flask entry point (run this)
├── api.py                  # REST API backend (auth, endpoints, exports)
├── config.py               # API keys, database URL, auth & notification settings
├── database.py             # PostgreSQL + SQLite persistence layer
├── users.py                # User management, authentication, settings
├── keyword_research.py     # Google autocomplete, SERP scraping, intent classification
├── pillar_cluster.py       # Keyword clustering, content planning
├── content_generator.py    # Pluggable AI article generation (Ollama/OpenAI/Claude/Gemini)
├── seo_audit.py            # URL analysis (meta tags, headings, density, links, images)
├── batch_audit.py          # Multi-URL CSV audit with comparison reports
├── content_calendar.py     # Editorial calendar generation and export
├── seo_recommendations.py  # AI-powered SEO recommendations + quick wins
├── notifications.py        # Email and Slack webhook notifications
├── google_trends.py        # Google Trends integration (pytrends)
├── seo_bing.py             # Bing SEO analysis, index status, URL submission
├── static/
│   └── index.html          # Modern SPA dashboard (sidebar nav, charts, dark mode)
├── requirements.txt        # Python dependencies
├── start.bat               # Windows launcher with auto Python detection
├── .gitignore              # Git ignore rules
└── README.md               # This file
```

---

## 🧩 How It Works

1. **Enter a seed keyword** → Google autocomplete suggestions, question/commercial/informational modifiers, People Also Ask, related searches, SERP results
2. **Build a cluster map** → Keywords grouped by similarity into pillar + cluster articles with suggested titles
3. **Generate articles** → AI writes a full SEO article using your keyword research and SERP context (supports English & Persian)
4. **One-click pipeline** → Automated Research → Cluster → AI Analysis → prioritized content plan
5. **Audit any URL** → Full SEO breakdown with page-type-specific checks (homepage, product, blog)
6. **Batch audit** → Compare multiple URLs side by side from a CSV upload
7. **Track keywords** → Save snapshots over time, visualize trends, persist in PostgreSQL/SQLite
8. **Plan content** → Generate editorial calendar from pillar-cluster plans, track status
9. **Get recommendations** → AI analyzes your audit and suggests specific fixes
10. **Analyze trends** → Google Trends interest data, related queries, trending searches
11. **Optimize for Bing** → Bing-specific SEO checks, index status, URL submission
12. **Export reports** → Download PDF audit reports and CSV keyword data
13. **Stay notified** → Email/Slack alerts for upcoming content deadlines

---

## 🛠️ Tech Stack

- **Frontend:** HTML5 / CSS3 / Vanilla JS (SPA), Chart.js, Font Awesome, Marked.js
- **Backend:** Python 3.10+, Flask, Flask-CORS
- **AI:** Ollama (local), OpenAI, Anthropic Claude, Google Gemini (pluggable)
- **Database:** PostgreSQL (optional) + SQLite (default)
- **Exports:** ReportLab (PDF), Python csv module (CSV)
- **Scraping:** Google Autocomplete API, BeautifulSoup, googlesearch-python
- **Trends:** pytrends (Google Trends), Bing Webmaster API
- **Notifications:** SMTP email, Slack webhooks

---

## 🔌 API Endpoints

### Authentication & Users
| Endpoint | Method | Description |
|---|---|---|
| `/api/auth/login` | POST | Login and get auth token |
| `/api/auth/logout` | POST | Logout and invalidate token |
| `/api/auth/check` | GET | Check if token is valid |
| `/api/auth/change-password` | POST | Change current user's password |
| `/api/users` | GET | List all users (admin only) |
| `/api/users` | POST | Create a new user (admin only) |
| `/api/users/<username>` | DELETE | Delete a user (admin only) |

### Keyword Research & Clustering
| Endpoint | Method | Description |
|---|---|---|
| `/api/keyword-research` | POST | Run keyword research |
| `/api/keyword-research` | GET | Get cached keyword data from session |
| `/api/keyword-research/export-csv` | POST | Export keywords as CSV |
| `/api/pillar-cluster` | POST | Build pillar-cluster map |
| `/api/pillar-cluster` | GET | Get cached cluster map from session |

### Content Generation
| Endpoint | Method | Description |
|---|---|---|
| `/api/article/generate` | POST | Generate single SEO article |
| `/api/article/generate-batch` | POST | Generate multiple articles from content plan |
| `/api/article/providers` | GET | List available AI providers |

### SEO Audit
| Endpoint | Method | Description |
|---|---|---|
| `/api/audit` | POST | Run SEO audit on a URL |
| `/api/audit/export-pdf` | POST | Export audit as PDF report |
| `/api/batch-audit` | POST | Run batch audit from CSV |
| `/api/batch-audit/sample-csv` | GET | Download sample CSV template |
| `/api/audit-history` | GET | View past audit results |

### Keyword Tracking & Calendar
| Endpoint | Method | Description |
|---|---|---|
| `/api/tracking` | GET | List tracked keywords |
| `/api/tracking` | POST | Track current keyword research |
| `/api/tracking/<keyword>` | DELETE | Remove keyword from tracking |
| `/api/tracking/<keyword>/history` | GET | Get keyword tracking history |
| `/api/calendar` | GET | Get content calendar |
| `/api/calendar` | POST | Generate calendar from cluster map |
| `/api/calendar/<event_id>` | PATCH | Update event status |
| `/api/calendar/<event_id>` | DELETE | Delete calendar event |
| `/api/calendar/export/<fmt>` | GET | Export calendar (markdown/json) |

### AI & Pipeline
| Endpoint | Method | Description |
|---|---|---|
| `/api/recommendations` | POST | Generate AI SEO recommendations |
| `/api/recommendations/quick-wins` | GET | Get quick-win fixes (no AI needed) |
| `/api/pipeline/run` | POST | One-click: Research → Cluster → AI Analysis → Content Plan |

### Google Trends
| Endpoint | Method | Description |
|---|---|---|
| `/api/trends/interest-over-time` | POST | Get interest over time for keywords |
| `/api/trends/related-queries` | POST | Get top & rising related queries |
| `/api/trends/trending` | GET | Get today's trending searches |
| `/api/trends/interest-by-region` | POST | Get interest breakdown by region |
| `/api/trends/status` | GET | Check Google Trends availability |

### Bing SEO
| Endpoint | Method | Description |
|---|---|---|
| `/api/bing/analyze` | POST | Analyze page for Bing-specific SEO factors |
| `/api/bing/index-status` | POST | Check if URL is indexed in Bing |
| `/api/bing/submit` | POST | Submit URL to Bing for indexing |
| `/api/bing/status` | GET | Check Bing API configuration |
| `/api/bing/trends` | POST | Get Bing search interest data |

### Settings & System
| Endpoint | Method | Description |
|---|---|---|
| `/api/settings` | GET | Get all application settings |
| `/api/settings` | POST | Update settings (admin only) |
| `/api/languages` | GET | List supported languages |
| `/api/status` | GET | Server status and available providers |

---

## ⚠️ Notes

- **Google scraping** is used for free keyword data. Avoid rapid repeated requests to prevent rate limiting.
- **Ollama** requires ~8GB+ RAM for LLaMA 3. Smaller models work on less RAM.
- Keyword research results are cached in the session for faster repeat searches.
- The tool uses heuristic intent classification — for production use, consider integrating a paid keyword data API.
- Auth tokens are stored in-memory — they reset when the server restarts.
- **Google Trends** data may be rate-limited by Google. Use sparingly in automated pipelines.
- **Bing index status** requires a valid `BING_API_KEY` from [Bing Webmaster Tools](https://www.bing.com/webmasters).
- **Persian (Farsi)** article generation requires an AI provider that supports RTL text well (Claude and GPT-4 recommended).

---

## 📄 License

MIT

---

## 🤝 Contributing

Contributions welcome! Please open an issue or PR.

---

## 📋 Changelog

### v2.0.0 (Latest)

#### 🆕 New Features
- **Google Trends Integration** — Interest over time, related queries, trending searches, and regional interest data via pytrends
- **Bing SEO Module** — Bing-specific SEO analysis, index status checking, URL submission, and Bing trends dashboard
- **User Management** — Multi-user support with admin/user roles, password management, database-backed auth with `users` table
- **Batch Article Generation** — Generate multiple articles from a content plan in a single API call
- **Unified Auto-Pipeline** — One-click automated pipeline: Research → Cluster → AI Analysis → Content Plan with AI-powered priority scoring
- **Multi-Language Support** — Generate articles in English (default) or Persian (Farsi) with locale-aware prompts and SEO conventions
- **Settings Management** — Database-backed application settings with admin-only API management
- **Page-Type-Specific Audit** — Homepage, Product, Blog, and Generic audit modes with auto-detection from URL patterns and type-specific scoring weights
- **Windows Launcher** — `start.bat` with automatic Python detection, dependency installation, and port conflict checking

#### 🔧 Improvements
- Authentication now uses database-backed users with role-based access control (admin/user)
- Login endpoint returns user role for frontend permission handling
- Keyword research automatically fetches Google Trends data for the seed keyword
- Pillar-cluster maps include Google Trends interest data
- Article generator supports Persian (Farsi) with dedicated system prompts
- SEO audit scoring is weighted differently per page type (homepage links, product images, blog content depth)

#### 🐛 Bug Fixes
- Fixed `google_trends.py` using `TrendReq` directly instead of `_TrendReqClass` alias
- Fixed redundant `import json as json_module` inside pipeline endpoint
- Removed unused `Optional` import in `content_calendar.py`

#### 🗑️ Removed Dead Code
- Deleted `keyword_tracker.py` (entire file — fully replaced by `database.py` db_* functions)
- Removed file-based calendar functions from `content_calendar.py` (`save_calendar_events`, `load_calendar_events`, `update_event_status`, `delete_event`) — replaced by database equivalents
- Removed `generate_comparison_markdown()` from `batch_audit.py` (unused)
- Removed `check_and_notify()` from `notifications.py` (unused)
- Removed unused dependencies: `streamlit`, `plotly`, `pandas` from `requirements.txt`

### v1.0.0 (Initial Release)

- Initial release with keyword research, pillar-cluster mapping, AI article generation
- SEO audit with scoring, batch audit with CSV import
- Content calendar with editorial planning
- AI-powered SEO recommendations and quick wins
- Email and Slack notifications for deadlines
- PDF audit export and CSV keyword export
- PostgreSQL + SQLite database support
- Token-based authentication
- Modern SPA dashboard with dark mode
