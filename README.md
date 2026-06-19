# 🔍 Rankivo — SEO AI Tools

A powerful, all-in-one Python SEO toolkit with a Streamlit web dashboard. Research keywords, build content clusters, generate AI articles, audit websites, track performance, and plan your editorial calendar — all from free sources with a pluggable AI backend.

![Python](https://img.shields.io/badge/Python-3.10+-blue) ![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-red) ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-optional-blue) ![License](https://img.shields.io/badge/License-MIT-green)

---

## ✨ Features

| Feature | Description |
|---|---|
| **📊 Keyword Research** | Google autocomplete suggestions, modifier expansion, People Also Ask, related searches, SERP analysis, search intent classification |
| **🗺️ Pillar-Cluster Map** | Auto-groups keywords into topic clusters, identifies pillar vs. cluster articles, generates a full content plan with Plotly visualizations |
| **✍️ Article Generator** | Creates full SEO-optimized articles (Markdown) with H1/H3 structure, keyword placement, internal link suggestions |
| **🔍 SEO Audit** | Analyzes any URL — meta tags, headings hierarchy, word count, keyword density, internal/external links, image alt text, SEO score (0-100) |
| **📋 Batch Audit** | Upload a CSV of URLs, audit them concurrently, get comparison tables and charts |
| **📈 Keyword Tracking** | Save keyword research snapshots over time, visualize trends, persist data in PostgreSQL or SQLite |
| **📅 Content Calendar** | Generate editorial timelines from pillar-cluster plans, track status, manage deadlines |
| **🧠 AI Recommendations** | AI-powered SEO recommendations that analyze audit results and suggest specific fixes |
| **🔔 Notifications** | Email and Slack webhook alerts for upcoming content calendar deadlines |
| **📜 Audit History** | Full audit history stored in the database for trend analysis |

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

```bash
streamlit run app.py
```

Opens at **http://localhost:8501**

---

## ⚙️ Configuration

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
├── app.py                  # Streamlit dashboard (main entry point, 9 tabs)
├── config.py               # API keys, database URL, notification settings
├── database.py             # PostgreSQL + SQLite persistence layer
├── keyword_research.py     # Google autocomplete, SERP scraping, intent classification
├── pillar_cluster.py       # Keyword clustering, content planning
├── content_generator.py    # Pluggable AI article generation (Ollama/OpenAI/Claude/Gemini)
├── seo_audit.py            # URL analysis (meta tags, headings, density, links, images)
├── batch_audit.py          # Multi-URL CSV audit with comparison reports
├── keyword_tracker.py      # Keyword tracking with JSON file storage
├── content_calendar.py     # Editorial calendar with JSON file storage
├── seo_recommendations.py  # AI-powered SEO recommendations + quick wins
├── notifications.py        # Email and Slack webhook notifications
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variable template
├── .gitignore              # Git ignore rules
└── README.md               # This file
```

---

## 🧩 How It Works

1. **Enter a seed keyword** → Google autocomplete suggestions, question/commercial/informational modifiers, People Also Ask, related searches, SERP results
2. **Build a cluster map** → Keywords grouped by similarity into pillar + cluster articles with suggested titles
3. **Generate articles** → AI writes a full SEO article using your keyword research and SERP context
4. **Audit any URL** → Full SEO breakdown: title, meta description, headings, word count, keyword density, links, images, score
5. **Batch audit** → Compare multiple URLs side by side from a CSV upload
6. **Track keywords** → Save snapshots over time, visualize trends, persist in PostgreSQL/SQLite
7. **Plan content** → Generate editorial calendar from pillar-cluster plans, track status
8. **Get recommendations** → AI analyzes your audit and suggests specific fixes
9. **Stay notified** → Email/Slack alerts for upcoming content deadlines

---

## 🛠️ Tech Stack

- **Frontend:** Streamlit + Plotly (interactive charts)
- **Backend:** Python 3.10+
- **AI:** Ollama (local), OpenAI, Anthropic Claude, Google Gemini (pluggable)
- **Database:** PostgreSQL (optional) + SQLite (default)
- **Scraping:** Google Autocomplete API, BeautifulSoup, googlesearch-python
- **Notifications:** SMTP email, Slack webhooks

---

## ⚠️ Notes

- **Google scraping** is used for free keyword data. Avoid rapid repeated requests to prevent rate limiting.
- **Ollama** requires ~8GB+ RAM for LLaMA 3. Smaller models work on less RAM.
- Keyword research results are cached in the session for faster repeat searches.
- The tool uses heuristic intent classification — for production use, consider integrating a paid keyword data API.

---

## 📄 License

MIT

---

## 🤝 Contributing

Contributions welcome! Please open an issue or PR.
