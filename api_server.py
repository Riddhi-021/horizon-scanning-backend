from fastapi import FastAPI
from fetch_news import fetch_google_news, save_articles_to_csv
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
from typing import Optional
from datetime import datetime
from contextlib import asynccontextmanager

# Initialize the scheduler globally so it can be controlled in lifespan
scheduler = BackgroundScheduler()

# Define the scanning task
def scheduled_horizon_scan():
    print("⏰ Scheduled scan running...")

    topics = ["AI engineer", "market trends", "digital transformation", "competitor PR"]
    all_articles = []

    for topic in topics:
        articles = fetch_google_news(topic, max_articles=10)
        all_articles.extend(articles)

    timestamp = datetime.now().strftime("%Y-%m-%d")
    filename = f"{timestamp}-horizon-scan.csv"
    save_articles_to_csv(all_articles, filename=filename)
    print(f"✅ {len(all_articles)} articles saved to {filename}")

# ✅ Modern FastAPI lifespan handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.add_job(scheduled_horizon_scan, trigger="cron", hour=6, minute=0)
    scheduler.start()
    print("🚀 Scheduler started")
    yield
    scheduler.shutdown()
    print("🛑 Scheduler shutdown")

# ✅ App initialized with new lifespan
app = FastAPI(lifespan=lifespan)

# CORS (so Custom GPT can call it if needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Your main endpoint (unchanged)
@app.get("/latest-news")
def latest_news(query: Optional[str] = "AI market trends", max_articles: Optional[int] = 20):
    news = fetch_google_news(query, max_articles)
    return {"articles": news}
