# Triple I — Autonomous AI Marketing Command Center v3.0

> **8 specialized AI agents. One autonomous loop. Zero manual marketing work.**
>
> Goal → Research → Generate → Deploy → Measure → Auto-adjust → Repeat

---

## 🤖 The Agent Team

| # | Agent | Role | New? |
|---|-------|------|------|
| 🧠 | **CMO Orchestrator** | Strategy · ICP · Goal-setting · Pipeline coordination | ✅ |
| 🔬 | **Research Agent** | Competitor analysis · Regulatory briefings · Market intel | ✅ |
| ✍️ | **Content Agent** | LinkedIn · Blog · Twitter · Persona-aware copy | ✅ |
| 🔍 | **SEO Agent** | Keyword clusters · Content gaps · CSRD/ESRS targeting | ✅ |
| 🎯 | **Ads Agent** | Google Ads + LinkedIn Ads · 3× A/B variants | ✅ |
| 📊 | **Analytics Agent** | KPI tracking · Anomaly detection · A/B winner analysis · Score /10 | 🆕 |
| 💰 | **Budget Agent** | ROI optimization · Channel reallocation · Auto-pause · Forecasting | 🆕 |
| 📣 | **Distribution Agent** | 7-day schedule · Optimal posting times · Email flows · Amplification | 🆕 |

---

## 🔄 The Autonomous Loop

```
1. CMO sets goal & brief
2. Research agent finds opportunity
3. SEO agent finds keywords
4. Content agent generates LinkedIn + Blog + Twitter
5. Ads agent generates Google + LinkedIn Ads (3 variants each)
6. Distribution agent plans deployment schedule + email flows
7. Analytics agent measures performance, scores /10, detects anomalies
8. A/B test analysis — winner detected
9. Budget agent reallocates spend, generates auto-rules
10. CMO synthesizes loop → feeds next cycle
```

**One button. Runs everything. Self-improves every cycle.**

---

## 🏗 Project Structure

```
triple_i/
├── main.py                          ← FastAPI entry point
├── requirements.txt
├── .env.example                     ← Copy to .env
├── frontend/
│   └── index.html                   ← Full Command Center UI (open in browser)
└── app/
    ├── config.py
    ├── database.py
    ├── models/
    │   ├── persona.py
    │   ├── country.py
    │   ├── campaign.py
    │   └── generated_content.py
    ├── schemas/
    │   ├── persona.py
    │   ├── country.py
    │   ├── campaign.py
    │   └── generated_content.py
    ├── agents/
    │   ├── base_agent.py            ← Shared LLM calls, cost tracking, DB persist
    │   ├── cmo_agent.py             ← Strategy, briefs, pipeline, chat
    │   ├── content_agent.py         ← LinkedIn, Blog, Twitter
    │   ├── seo_agent.py             ← Keywords, optimization
    │   ├── ads_agent.py             ← Google Ads, LinkedIn Ads (A/B)
    │   ├── research_agent.py        ← Competitors, regulatory
    │   ├── analytics_agent.py       ← KPIs, A/B analysis, scoring  [NEW]
    │   ├── budget_agent.py          ← ROI, reallocation, forecasting [NEW]
    │   ├── distribution_agent.py    ← Deploy schedule, email flows  [NEW]
    │   └── autonomous_orchestrator.py ← Full loop coordinator       [NEW]
    └── api/
        ├── persona.py               ← CRUD + /seed
        ├── country.py               ← CRUD + /seed
        ├── campaign.py              ← CRUD
        ├── content.py               ← List, filter, stats
        └── generate.py              ← All agent endpoints + autonomous loop
```

---

## ⚡ Quick Start (5 minutes)

### 1. Prerequisites
- Python 3.10+
- PostgreSQL running locally
- OpenAI API key

### 2. Install dependencies
```bash
cd triple_i
pip install -r requirements.txt
```

### 3. Configure environment
```bash
cp .env.example .env
```

Edit `.env`:
```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/triple_i
OPENAI_API_KEY=sk-your-openai-key-here
OPENAI_MODEL=gpt-4o
```

### 4. Create the database
```bash
createdb triple_i
# or with explicit credentials:
createdb -U postgres -h localhost triple_i
```

### 5. Start the API
```bash
uvicorn main:app --reload --port 8000
```

You should see:
```
INFO: Uvicorn running on http://127.0.0.1:8000
INFO: Triple I Autonomous Marketing AI — ONLINE
```

### 6. Open the UI
Open `frontend/index.html` in your browser.
*(Or visit `http://localhost:8000/ui`)*

### 7. Seed data
In the UI: **Setup → 🌱 Seed Personas + Countries**

This creates:
- 2 Personas: **SME** + **ADVISORY**
- 7 Markets: Spain, France, Netherlands, Belgium, Sweden (Cluster A) + UAE, Japan (Cluster B)

### 8. Create a campaign
In **Setup → ➕ Create Campaign**, fill in:
- Campaign name
- Persona (SME or Advisory)
- Country
- Framework focus (Carbon / Interoperability / Full ESG)
- Channel (LinkedIn / Google / Both)
- Goal

**OR use the AI Goal Generator** in the Loop panel — let the CMO define goals automatically!

### 9. 🚀 Launch the Autonomous Loop
Go to **🔄 Loop** → select campaign → **Launch Autonomous Loop**

Watch all 13 steps execute automatically in real-time.

---

## 📡 API Reference

### Core CRUD
```
GET  /personas/
POST /personas/
POST /personas/seed          ← Create default SME + Advisory personas

GET  /countries/
POST /countries/
POST /countries/seed         ← Create all 7 target markets

GET  /campaigns/
POST /campaigns/
PATCH /campaigns/{id}/status

GET  /content/               ← filter: ?type=&status=
GET  /content/stats/summary  ← aggregate analytics
PATCH /content/{id}/status
```

### Generate — All POST
```
# Content Agent
/generate/linkedin/{campaign_id}
/generate/blog-from-linkedin/{content_id}
/generate/twitter/{campaign_id}

# SEO Agent
/generate/seo/keywords/{campaign_id}
/generate/seo/optimize/{content_id}

# Ads Agent
/generate/ads/google/{campaign_id}
/generate/ads/linkedin/{campaign_id}

# CMO Agent
/generate/cmo/brief/{campaign_id}
/generate/cmo/pipeline/{campaign_id}     ← Classic 5-step pipeline
/generate/cmo/chat                        ← POST {message, context}

# Research Agent
/generate/research/competitors/{campaign_id}
/generate/research/regulatory/{campaign_id}

# Analytics Agent  [NEW]
/generate/analytics/performance/{campaign_id}
/generate/analytics/ab-test/{campaign_id}

# Budget Agent  [NEW]
/generate/budget/optimize/{campaign_id}

# Distribution Agent  [NEW]
/generate/distribution/plan/{campaign_id}

# Autonomous Loop  [NEW]
/generate/autonomous/loop/{campaign_id}   ← POST {loop_mode: "full"}
/generate/autonomous/generate-goals       ← POST {persona_id, country_id}
```

### Loop Modes
| Mode | Steps | Use case |
|------|-------|----------|
| `full` | All 13 steps | Weekly autonomous run |
| `generate_only` | Strategy + Content + Ads + Distribution | First run / new campaign |
| `analyze_only` | Analytics + A/B test | Quick performance check |
| `optimize_only` | Analytics + Budget | Budget reallocation only |

---

## 💡 Usage Tips

### First campaign ever?
1. Seed data
2. Create campaign (or use AI Goal Generator)
3. Run `generate_only` loop first to build content library
4. Run `full` loop weekly

### Weekly rhythm
```
Monday:   full loop → review Loop Synthesis report
Wednesday: analyze_only → check if anything needs adjustment  
Friday:   optimize_only → confirm budget allocation for next week
```

### Changing AI model
In `.env`:
```
OPENAI_MODEL=gpt-4o-mini    # cheaper, faster
OPENAI_MODEL=gpt-4o         # best quality (default)
OPENAI_MODEL=gpt-4-turbo    # alternative
```

### Cost tracking
Every generated piece tracks tokens and USD cost.
View aggregate stats: `GET /content/stats/summary`

---

## 🏛 Architecture

```
Frontend (index.html)
    ↓ HTTP/REST
FastAPI (main.py)
    ↓
API Routes (app/api/)
    ↓
Agents (app/agents/)
    ↓  ↓  ↓  ↓  ↓  ↓  ↓  ↓
   CMO Res Cnt SEO Ads Ana Bud Dis
    ↓
OpenAI GPT-4o (structured JSON output)
    ↓
PostgreSQL (all content persisted)
```

- All agents inherit `BaseAgent` — shared OpenAI client, cost tracking, DB persistence
- Structured JSON via OpenAI `json_object` format for reliable parsing
- Campaign context (persona + country) flows automatically into every agent
- Autonomous orchestrator coordinates all agents, captures errors gracefully
- Frontend connects to `http://localhost:8000` — update `API` constant in index.html for production

---

## 🔧 Extending the System

### Add a new agent
1. Create `app/agents/my_agent.py` extending `BaseAgent`
2. Implement methods using `self._call_model()` and `self._save_content()`
3. Add endpoints in `app/api/generate.py`
4. Add agent to `AutonomousOrchestrator.run_autonomous_loop()` if it should run in the loop

### Add a new market / persona
Use the API endpoints or the Setup panel in the UI to add custom personas and countries.

---

## ⚠️ Troubleshooting

| Issue | Fix |
|-------|-----|
| `connection refused` on startup | Check PostgreSQL is running and DATABASE_URL is correct |
| `OpenAI API error` | Check OPENAI_API_KEY in .env |
| Loop step fails | Check the Live Agent Log in the Loop panel for the specific error |
| `table not found` | Tables auto-create on startup — check DB connection |
| UI shows no campaigns | Run Seed Data first, then create a campaign |
| CORS error in browser | Make sure API is running on port 8000 |

---

*Triple I Autonomous Marketing AI v3.0 — Built for ESG & Carbon Reporting companies.*
*8 agents. One loop. Infinite marketing leverage.*
