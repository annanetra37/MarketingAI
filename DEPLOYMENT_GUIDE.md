# 🚀 Triple I — Complete Deployment Guide
## Free Deployment on Railway (GitHub Auto-Deploy)

Railway gives you:
- ✅ Free tier (500 hrs/month — enough for a dev/demo environment)
- ✅ PostgreSQL database included FREE
- ✅ GitHub auto-deploy on every push
- ✅ HTTPS URLs out of the box
- ✅ No credit card required to start

---

## Architecture on Railway

```
GitHub Repo
    ↓ (auto-deploy on push)
Railway
    ├── Web Service  (FastAPI + serves frontend/index.html)
    └── PostgreSQL   (managed database, free tier)
```

---

## Step-by-Step Deployment

### Step 1 — Push all v4.0 files to GitHub

Make sure your repo has:
```
triple_i/
├── main.py
├── requirements.txt
├── Procfile              ← NEW (created below)
├── runtime.txt           ← NEW (created below)
├── railway.toml          ← NEW (created below)
├── .env.example
├── frontend/
│   └── index.html
└── app/
    ├── agents/
    │   ├── triple_i_context.py   ← NEW v4.0
    │   ├── cmo_agent.py          ← UPDATED v4.0
    │   └── ... (all updated agents)
    └── ...
```

### Step 2 — Create a Railway account

1. Go to **https://railway.app**
2. Click **"Start a New Project"**
3. Sign in with **GitHub** (this links your repos automatically)

### Step 3 — Deploy from GitHub

1. Click **"Deploy from GitHub repo"**
2. Select your `triple_i` (or `marketingAI`) repository
3. Railway will detect it's a Python app and deploy automatically

### Step 4 — Add PostgreSQL database

1. In your Railway project, click **"+ New"**
2. Select **"Database" → "Add PostgreSQL"**
3. Railway creates a free Postgres instance and sets `DATABASE_URL` automatically
   - You do NOT need to set DATABASE_URL manually — Railway injects it

### Step 5 — Set environment variables

In Railway dashboard → your web service → **"Variables"** tab, add:

```
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o
```

That's it. Railway auto-injects `DATABASE_URL` from the linked Postgres service.

### Step 6 — Done! 🎉

Your app will be live at:
```
https://your-project-name.up.railway.app
```

The UI is at: `https://your-project-name.up.railway.app/ui`
The API docs are at: `https://your-project-name.up.railway.app/docs`

---

## Auto-Deploy on GitHub Push

Every time you push to your **main** branch:
1. Railway detects the push automatically
2. Builds the new version
3. Zero-downtime deploy
4. Live within ~60 seconds

To deploy a new version:
```bash
git add .
git commit -m "feat: update agents v4.0"
git push origin main
# Railway auto-deploys ✅
```

---

## Free Tier Limits

| Resource | Free Tier | Notes |
|----------|-----------|-------|
| Hours    | 500/month | ~16 hrs/day — enough for demo/MVP |
| RAM      | 512 MB    | Sufficient for FastAPI + agents |
| Postgres | 1 GB      | Plenty for content storage |
| Bandwidth| 100 GB    | No issue |

To stay within free tier: Railway sleeps the service when inactive (cold start ~5 sec).

---

## Custom Domain (Optional)

In Railway → Settings → Custom Domain → add your domain.
Free SSL certificate included automatically.

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Build fails | Check `requirements.txt` has all dependencies |
| `DATABASE_URL` error | Make sure Postgres service is linked in Railway |
| App crashes on start | Check Railway logs → usually missing env variable |
| CORS errors | Already fixed — `allow_origins=["*"]` in main.py |
| Frontend can't reach API | Update `API` const in `frontend/index.html` to Railway URL |
