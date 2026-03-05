# Triple I — Autonomous AI Marketing Command Center v4.0

> **Fear → ESRS Assessment → Fast-Track Sprint. In 6 weeks. Automatically.**
>
> 8 specialized AI agents. One loop. One goal: close a paid ESG compliance pilot.

---

## 🆕 What's New in v4.0

This version embeds Triple I's **complete product knowledge** and **Fear → Pilot → 6-Week Close** sales strategy directly into every agent's DNA.

### What changed and why

| Agent | Key changes |
|-------|-------------|
| 🧠 **CMO** | Briefs now lead with CSRD fear + deadline urgency; include Fast-Track Sprint as primary CTA; structure 6-week sales cycle plan |
| ✍️ **Content** | Fear-first hooks on every piece; EcoHub™, 80–90% cost reduction, Cambridge credibility baked in; ESRS Assessment and Sprint CTAs required |
| 🔍 **SEO** | Keywords split by funnel stage (fear / assessment / conversion); local language variants; ESRS Readiness Assessment landing page keywords |
| 🎯 **Ads** | 3 variants: Fear angle / Speed angle / Cost angle; CTAs tied to Assessment or Sprint; LinkedIn targeting by job title and company size |
| 🔬 **Research** | Regulatory briefings now include specific non-compliance penalties; competitor analysis highlights CSRD-native advantage |
| 📣 **Distribution** | 6-week sales cadence with 5-email nurture sequence from Assessment download to Sprint close |
| 📊 **Analytics** | KPIs mapped to pilot funnel: Assessment completions, discovery calls, pilot signed |
| 💰 **Budget** | Spend decisions tied to cost-per-pilot-lead; Cluster A priority; minimum viable budget to first pilot |
| 🔄 **Orchestrator** | New `fear_blitz` mode for rapid market entry; CMO synthesis after every loop |

### New shared context module

All agents import from `app/agents/triple_i_context.py` — a single source of truth for:
- Product capabilities and verified claims (80–90% cost reduction, EcoHub™, Cambridge)
- ICP definitions (SME vs. Advisory)
- Target markets with CSRD context
- Sales strategy (Fear → Assessment → Sprint → Close)
- Regulatory deadlines (CSRD Phase 1/2/3)
- Fear hooks library
- CTA library

**Change once. Propagate everywhere.**

---

## 🤖 The Agent Team

| # | Agent | Role |
|---|-------|------|
| 🧠 | **CMO Orchestrator** | Strategy · Fear-first briefs · 6-week sales cycle · Pipeline coordination |
| 🔬 | **Research Agent** | Regulatory urgency briefings · Competitor CSRD gaps · Objection handling |
| ✍️ | **Content Agent** | Fear-hook LinkedIn · CSRD blog · Sprint-CTA Twitter threads |
| 🔍 | **SEO Agent** | Fear-stage + conversion-stage keywords · ESRS Assessment landing pages |
| 🎯 | **Ads Agent** | Fear/Speed/Cost A/B variants · Google + LinkedIn · Sprint and Assessment CTAs |
| 📊 | **Analytics Agent** | Funnel health · Pilot conversion forecast · Fear-hook effectiveness |
| 💰 | **Budget Agent** | Cost-per-pilot-lead · Cluster A allocation · Pilot economics (€5K–€15K) |
| 📣 | **Distribution Agent** | 6-week sales cadence · 5-email nurture · Assessment → Sprint flow |

---

## 🔄 The Autonomous Loop (v4.0)

```
1.  CMO creates fear-first campaign brief (CSRD urgency + Fast-Track Sprint CTA)
2.  Research: regulatory briefing — specific deadlines + penalties for target country
3.  SEO: keyword clusters by funnel stage (fear → assessment → conversion)
4.  Content: LinkedIn post (fear hook → EcoHub™ proof → Sprint CTA)
5.  Content: Twitter/X thread (CSRD urgency → Triple I solution)
6.  Ads: Google Search (3 variants: fear / speed / cost angle)
7.  Ads: LinkedIn Sponsored (3 variants targeting CFO / Head of Sustainability)
8.  Content: Blog article expanded from LinkedIn (SEO-optimised, ESRS Assessment CTA)
9.  Distribution: 6-week deployment plan (Steps 1–5 of sales motion, email flows)
10. Research: competitor analysis (CSRD gaps Triple I fills)
11. Analytics: funnel performance + pilot conversion forecast
12. A/B test: which fear hooks and CTAs convert fastest
13. Budget: reallocate toward lowest cost-per-pilot-lead channels
→   CMO synthesises → prioritises next cycle
```

### Loop Modes

| Mode | Steps | Use case |
|------|-------|----------|
| `full` | All 13 steps | Weekly autonomous run |
| `generate_only` | Strategy + Content + Ads + Distribution | First run / new campaign |
| `analyze_only` | Analytics + A/B test | Mid-week performance check |
| `optimize_only` | Analytics + Budget | Budget reallocation only |
| `fear_blitz` | CMO + LinkedIn + Twitter + Google Ads + LinkedIn Ads | **NEW** — rapid market entry push |

---

## 🎯 The Sales Strategy (Baked into Every Agent)

### 1. Lead with Fear, Follow with Value
Every piece of content opens with CSRD urgency:
- *"Your first ESRS E1 report is due. Are you ready?"*
- Regulatory pressure → cost of non-compliance → Triple I solution

### 2. Pilot as the Primary Sales Motion
The **Fast-Track Compliance Sprint** is not a product stage — it's the sales weapon:
- Scope: ESRS E1 (climate/GHG) + S1 (workforce)
- Duration: 6–8 weeks
- Deliverable: a draft ESRS-ready report they can actually use
- Price: **€5K–€15K** (paid pilot filters serious buyers)
- Always includes upgrade path to full platform

### 3. Sub-6-Week Sales Cycle
```
Week 1: Outreach → CSRD fear hook → ESRS Readiness Assessment CTA
Week 2: Discovery call (30 min) — qualify: deadline? spreadsheets?
Week 3: Live demo (45 min) — show E1+S1 workflow
Week 4: Pilot proposal — scoped, priced, with conversion clause
Week 5: Negotiate / address objections
Week 6: Close
```

---

## 🏗 Project Structure

```
triple_i/
├── main.py
├── requirements.txt
├── .env.example
├── frontend/
│   └── index.html
└── app/
    ├── config.py
    ├── database.py
    ├── models/
    ├── schemas/
    ├── agents/
    │   ├── triple_i_context.py      ← ⭐ NEW: single source of truth for all agents
    │   ├── base_agent.py
    │   ├── cmo_agent.py             ← UPDATED v4.0
    │   ├── content_agent.py         ← UPDATED v4.0
    │   ├── seo_agent.py             ← UPDATED v4.0
    │   ├── ads_agent.py             ← UPDATED v4.0
    │   ├── research_agent.py        ← UPDATED v4.0
    │   ├── analytics_agent.py       ← UPDATED v4.0
    │   ├── budget_agent.py          ← UPDATED v4.0
    │   ├── distribution_agent.py    ← UPDATED v4.0
    │   └── autonomous_orchestrator.py ← UPDATED v4.0
    └── api/
```

---

## ⚡ Quick Start

### 1. Prerequisites
- Python 3.10+
- PostgreSQL running locally
- OpenAI API key

### 2. Install
```bash
cd triple_i
pip install -r requirements.txt
cp .env.example .env
# Edit .env: DATABASE_URL, OPENAI_API_KEY, OPENAI_MODEL=gpt-4o
createdb triple_i
uvicorn main:app --reload --port 8000
```

### 3. Open the UI
Open `frontend/index.html` → **Setup → 🌱 Seed Personas + Countries**

### 4. 🚀 Fastest path to first pilot content

**For immediate European market entry, use `fear_blitz` mode:**
```
Go to 🔄 Loop → select Spain or France campaign → Loop Mode: fear_blitz → Launch
```
This generates: CMO brief + LinkedIn fear post + Twitter thread + Google Ads + LinkedIn Ads
in one shot. Ready to deploy in minutes.

### 5. Weekly rhythm
```
Monday:    full loop → review Loop Synthesis + deploy content
Wednesday: analyze_only → check funnel health, booking rates
Friday:    optimize_only → budget reallocation for next week
```

---

## 📡 API Reference

All existing endpoints work unchanged. New additions:

```
# Loop modes
POST /generate/autonomous/loop/{campaign_id}
     Body: { "loop_mode": "full" | "generate_only" | "analyze_only" | "optimize_only" | "fear_blitz" }

# Goal generator (CMO-powered)
POST /generate/autonomous/generate-goals
     Body: { "persona_id": "...", "country_id": "..." }
```

---

## 🌍 Target Market Priority

**Focus on Cluster A FIRST for fast results:**

1. 🇪🇸 **Spain** — CSRD transposed, FY2025 reports due NOW, manufacturing/retail hot
2. 🇫🇷 **France** — Advanced ESG awareness + CSRD, strong advisory market
3. 🇳🇱 **Netherlands** — ESG culture + multinationals, high framework interop demand
4. 🇧🇪 **Belgium** — Mid-market density, EU HQ proximity
5. 🇸🇪 **Sweden** — Voluntary reporters now needing formal CSRD structure

**Cluster B** (UAE, Japan) — secondary priority, ISSB alignment pathway

---

## 💡 Key Product Claims (Always Use These)

| Claim | Use for |
|-------|---------|
| 80–90% cost reduction vs. manual | All content, ads, and pitches |
| EcoHub™ — Innovation Award-winning AI engine | Credibility and differentiation |
| Cambridge Sustainability Leadership Ecosystem | Social proof |
| 6-week Fast-Track Compliance Sprint | Primary CTA / pilot offer |
| €5K–€15K pilot price | Qualifying buyers + urgency |
| No IT dependency | SME audience |
| ESRS E1 + S1 native — no custom mapping | Product differentiation |
| Data in once → ESRS + GRI + ISSB + GHG Protocol | Framework interoperability |
| Audit-ready, traceable, multi-language PDF | Compliance credibility |

---

## ⚠️ Troubleshooting

| Issue | Fix |
|-------|-----|
| `connection refused` | Check PostgreSQL + DATABASE_URL |
| `OpenAI API error` | Check OPENAI_API_KEY in .env |
| Loop step fails | Check Live Agent Log in Loop panel |
| `table not found` | Tables auto-create on startup — check DB connection |
| UI shows no campaigns | Run Seed Data first |
| CORS error | Make sure API is on port 8000 |

---

*Triple I Autonomous Marketing AI v4.0*
*8 agents. One loop. One mission: close a Fast-Track Compliance Sprint pilot in 6 weeks.*
*Fear → Assessment → Demo → Pilot → Close. Automatically.*
