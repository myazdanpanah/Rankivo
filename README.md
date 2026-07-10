# 🔍 Rankivo — SEO AI Tools

A powerful, all-in-one Python SEO toolkit with a **modern web dashboard**. Research keywords, build content clusters, generate AI articles, audit websites, track performance, analyze Google Trends & Bing SEO, and plan your editorial calendar — all from free sources with a pluggable AI backend.

![Python](https://img.shields.io/badge/Python-3.10+-blue) ![Flask](https://img.shields.io/badge/Flask-3.0+-green) ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-optional-blue) ![License](https://img.shields.io/badge/License-MIT-green)

---

## ✨ Features

### Core SEO Tools
| Feature | Description |
|---|---|
| **📊 Keyword Research** | Google autocomplete, modifier expansion, People Also Ask, related searches, SERP analysis, intent classification |
| **🗺️ Pillar-Cluster Map** | Auto-groups keywords into topic clusters with pillar/cluster articles and content plan |
| **✍️ Article Generator** | SEO-optimized articles (Markdown) with research-backed content, H1/H3 structure, keyword placement |
| **🌐 Multi-Language** | Generate articles in English or Persian (Farsi) with locale-aware prompts |
| **🔍 SEO Audit** | Full URL analysis — meta tags, headings, word count, keyword density, links, images, SEO score |
| **🧠 AI Recommendations** | AI-powered SEO recommendations that analyze audit results and suggest specific fixes |
| **📅 Content Calendar** | Generate editorial timelines from pillar-cluster plans, track status, manage deadlines |
| **📈 Google Trends** | Interest over time, related queries, trending searches, interest by region, Iran province data |
| **🔵 Bing SEO** | Bing-specific SEO analysis, index status check, URL submission, Bing trends |

### Advanced SEO Modules (New in v3.0)
| Feature | Description |
|---|---|
| **🏆 E-E-A-T Analysis** | Evaluate Experience, Expertise, Authoritativeness, Trustworthiness per Google Quality Rater Guidelines |
| **🏷️ Schema.org Deep Audit** | Detect, validate, and get recommendations for 15+ Schema.org types with deprecated type tracking |
| **🤖 GEO / AI Search** | Evaluate AI search readiness: passage citability, question headings, entity presence, attribution density |
| **🔗 Backlink Analysis** | Analyze backlinks using Bing Webmaster API and Common Crawl with toxic link detection |
| **📉 SEO Drift Monitoring** | Track SEO changes over time with snapshot comparison to detect regressions and improvements |
| **🖼️ Image SEO** | Analyze alt text, file sizes, WebP/AVIF formats, responsive images, lazy loading, CLS prevention |
| **🗺️ Sitemap Audit** | XML sitemap discovery, parsing, URL validation, deprecated tag detection |
| **🌍 Hreflang / i18n** | Hreflang validation — self-referencing, x-default, return tag reciprocity, canonical alignment |
| **📍 Local SEO** | Local SEO audit — GBP signals, NAP consistency, reviews, LocalBusiness schema |
| **🛒 E-commerce SEO** | Product schema validation, pricing signals, availability, marketplace detection |
| **✨ SXO (Search Experience)** | Page type classification, intent alignment, persona scoring, user experience optimization |
| **📝 Content Brief Generator** | Generate content briefs with outline, keywords, competitor angles, internal link suggestions |
| **⚙️ Programmatic SEO** | URL pattern analysis, thin content detection, index bloat identification, template analysis |
| **♟️ SEO Strategy Planning** | Strategic SEO planning with 5 industry templates (SaaS, E-commerce, Local, Healthcare, Media) |
| **📄 PDF/HTML Reports** | Professional audit reports with charts, severity breakdown, and actionable recommendations |
| **⚡ Parallel Orchestrator** | Run all SEO modules simultaneously using ThreadPoolExecutor for maximum speed |
| **📊 Site Performance** | Search Console/GA4-style dashboard with CWV tracking, score trends, and crawl monitoring |
| **🎭 SPA Renderer** | Render JavaScript-heavy pages (React, Next.js, Vue) using headless Chromium via Playwright |

### Infrastructure
| Feature | Description |
|---|---|
| **🐳 Docker** | Multi-stage Docker build with Playwright Chromium, PostgreSQL, and gunicorn |
| **🔐 User Management** | Multi-user with admin/user roles, database-backed auth, bcrypt password hashing |
| **🔔 Notifications** | Email (SMTP) and Slack webhook alerts for content calendar deadlines |
| **📦 Batch Audit** | Upload CSV of URLs, audit concurrently, get comparison tables and charts |
| **📊 CSV/PDF Export** | Download keyword data as CSV and audit reports as PDF |

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

**Docker:**
```bash
docker build -t rankivo .
docker run -p 5500:5500 rankivo
```

Opens at **http://localhost:5500**

**Default login:** `admin` / `admin12345`

---

## ⚙️ Configuration

### Authentication

| Setting | Default | Description |
|---|---|---|
| `ADMIN_USERNAME` | `admin` | Login username |
| `ADMIN_PASSWORD` | `admin12345` | Login password |
| `SECRET_KEY` | `rankivo-change-me-in-production` | Token signing key |

### AI Providers

| Provider | Cost | Setup |
|---|---|---|
| **Ollama** | Free | Install [Ollama](https://ollama.ai), run `ollama pull llama3` |
| **OpenAI** | ~$0.01/article | Set `OPENAI_API_KEY` in `.env` |
| **Claude** | ~$0.01/article | Set `ANTHROPIC_API_KEY` in `.env` |
| **Gemini** | Free tier available | Set `GOOGLE_API_KEY` in `.env` |

### Database

Rankivo supports **PostgreSQL** (production) with automatic **SQLite** fallback (local development).

**SQLite (default):** Data stored in `data/rankivo.db`

**PostgreSQL:**
```bash
DATABASE_URL=postgresql://user:password@localhost:5432/rankivo
```

---

## 📁 Project Structure

```
Rankivo/
├── app.py                    # Flask entry point
├── api.py                    # REST API (40+ endpoints)
├── config.py                 # Configuration & shared utilities
├── database.py               # PostgreSQL + SQLite persistence
├── users.py                  # User management & auth
├── keyword_research.py       # Keyword research & SERP scraping
├── pillar_cluster.py         # Keyword clustering & content planning
├── content_generator.py      # AI article generation (Ollama/OpenAI/Claude/Gemini)
├── seo_audit.py              # On-page SEO audit
├── technical_seo.py          # Technical SEO (robots.txt, sitemap, CWV)
├── batch_audit.py            # Multi-URL batch audit
├── seo_recommendations.py    # AI-powered recommendations
├── content_calendar.py       # Editorial calendar
├── google_trends.py          # Google Trends integration
├── seo_bing.py               # Bing SEO analysis
├── notifications.py          # Email & Slack notifications
├── llm_keyword_intelligence.py # LLM-powered keyword analysis
├── persian_intent_classifier.py # Persian search intent classification
├── persian_nlp.py             # Persian NLP utilities
├── content_gap.py            # Content gap analysis
├── topic_researcher.py       # Topic research via web search
├── eeat.py                   # E-E-A-T analysis
├── schema_audit.py           # Schema.org deep audit
├── geo_audit.py              # GEO / AI Search audit
├── backlinks.py              # Backlink analysis
├── seo_drift.py              # SEO drift monitoring
├── seo_images.py             # Image SEO analysis
├── sitemap_audit.py          # Sitemap audit
├── hreflang_audit.py         # Hreflang / i18n audit
├── local_seo.py              # Local SEO audit
├── ecommerce_seo.py          # E-commerce SEO audit
├── sxo_audit.py              # Search Experience Optimization
├── content_brief.py          # Content brief generator
├── programmatic_seo.py       # Programmatic SEO analysis
├── seo_plan.py               # Strategic SEO planning
├── pdf_report.py             # PDF/HTML report generation
├── parallel_orchestrator.py  # Parallel agent orchestration
├── site_performance.py       # Site performance monitoring
├── spa_renderer.py           # SPA/JS rendering via Playwright
├── static/
│   └── index.html            # Modern SPA dashboard
├── Dockerfile                # Multi-stage Docker build
├── docker-compose.yml        # Docker Compose with PostgreSQL
├── requirements.txt          # Python dependencies
└── test_new_modules.py       # Integration tests (16 tests)
```

---

## 🔌 API Endpoints (40+)

### Authentication
- `POST /api/auth/login` — Login
- `POST /api/auth/logout` — Logout
- `GET /api/auth/check` — Check auth
- `POST /api/auth/change-password` — Change password

### Keyword Research & Clustering
- `POST /api/keyword-research` — Run research
- `POST /api/pillar-cluster` — Build cluster map
- `POST /api/pipeline/run` — One-click pipeline

### Content
- `POST /api/article/generate` — Generate article
- `POST /api/content-gap/analyze` — Content gap analysis
- `POST /api/content-brief/generate` — Content brief

### SEO Audit & Technical
- `POST /api/audit` — SEO audit
- `POST /api/technical/audit` — Technical SEO audit
- `POST /api/batch-audit` — Batch audit from CSV

### Advanced SEO Modules
- `POST /api/eeat/analyze` — E-E-A-T analysis
- `POST /api/schema/audit` — Schema.org audit
- `POST /api/geo/audit` — GEO / AI Search audit
- `POST /api/backlinks/analyze` — Backlink analysis
- `POST /api/images/analyze` — Image SEO analysis
- `POST /api/sitemap/audit` — Sitemap audit
- `POST /api/hreflang/audit` — Hreflang audit
- `POST /api/local-seo/audit` — Local SEO audit
- `POST /api/ecommerce/audit` — E-commerce SEO audit
- `POST /api/sxo/audit` — SXO audit
- `POST /api/programmatic/audit` — Programmatic SEO audit
- `POST /api/plan/generate` — SEO strategy plan

### Parallel Orchestrator
- `POST /api/orchestrator/audit` — Full parallel audit (all modules)
- `POST /api/orchestrator/focused` — Focused audit (selected modules)
- `POST /api/report/full-audit` — Parallel audit + report generation

### Performance Monitoring
- `POST /api/performance/dashboard` — Performance dashboard data
- `POST /api/performance/fetch-cwv` — Fetch Core Web Vitals
- `POST /api/performance/save-snapshot` — Save score snapshot
- `GET /api/performance/tracked-sites` — List tracked sites

### Trends & Bing
- `POST /api/trends/interest-over-time` — Google Trends data
- `POST /api/bing/analyze` — Bing SEO analysis
- `POST /api/bing/trends` — Bing trends data

### Exports
- `POST /api/audit/export-pdf` — PDF report
- `POST /api/keyword-research/export-csv` — CSV export
- `POST /api/report/generate` — HTML/PDF report generation

---

## 🧪 Testing

```bash
# Run all integration tests
python test_new_modules.py

# Run original component tests (requires server running)
python test_components.py
```

---

## 🐳 Docker

```bash
# Build
docker build -t rankivo .

# Run standalone
docker run -p 5500:5500 rankivo

# Run with PostgreSQL (docker-compose)
docker-compose up -d
```

The Docker image includes:
- Python 3.12 with all dependencies
- Playwright Chromium for SPA rendering
- gunicorn with 4 workers
- Health check at `/health`

---

## 🛠️ Tech Stack

- **Frontend:** HTML5 / CSS3 / Vanilla JS (SPA), Chart.js, Font Awesome
- **Backend:** Python 3.10+, Flask, Flask-CORS, Flask-Limiter
- **AI:** Ollama (local, free), OpenAI, Anthropic Claude, Google Gemini
- **Database:** PostgreSQL (optional) + SQLite (default)
- **Exports:** ReportLab (PDF), matplotlib (charts), Python csv
- **Scraping:** Google Autocomplete API, BeautifulSoup, requests
- **Trends:** pytrends (Google Trends), Bing Webmaster API
- **Rendering:** Playwright (headless Chromium for SPA pages)
- **Threading:** ThreadPoolExecutor for parallel SEO analysis
- **Auth:** bcrypt password hashing, token-based authentication

---

## 📄 License

MIT

---

## 🤝 Contributing

Contributions welcome! Please open an issue or PR.
