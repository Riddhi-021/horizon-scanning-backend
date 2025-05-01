from fastapi import FastAPI
from fetch_news import fetch_google_news, save_articles_to_csv
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
from typing import Optional
from datetime import datetime
from contextlib import asynccontextmanager

# Initialize the scheduler
scheduler = BackgroundScheduler()

# ✅ This function will run at 6 AM daily
def scheduled_horizon_scan():
    print("⏰ Scheduled horizon scan started...")

    topics = ["AI engineer", "market trends", "digital transformation", "competitor PR"]
    all_articles = []

    for topic in topics:
        articles = fetch_google_news(topic, max_articles=10)
        all_articles.extend(articles)

    # Save with timestamped filename
    filename = f"{datetime.now().strftime('%Y-%m-%d')}-horizon-scan.csv"
    save_articles_to_csv(all_articles, filename=filename)

    print(f"✅ {len(all_articles)} articles saved to {filename}")

# ✅ Use modern FastAPI lifespan handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.add_job(scheduled_horizon_scan, trigger="cron", hour=6, minute=0)
    scheduler.start()
    print("🚀 Scheduler started")
    yield
    scheduler.shutdown()
    print("🛑 Scheduler stopped")

# ✅ Create FastAPI app with lifespan
app = FastAPI(lifespan=lifespan)

# ✅ Enable CORS (needed for GPT API calling)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Manual query endpoint
@app.get("/latest-news")
def latest_news(query: Optional[str] = "AI market trends", max_articles: Optional[int] = 20):
    news = fetch_google_news(query, max_articles)
    return {"articles": news}
