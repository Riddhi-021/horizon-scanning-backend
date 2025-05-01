from fastapi import FastAPI
from fetch_news import fetch_google_news, save_articles_to_csv
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
from typing import Optional
from datetime import datetime
from contextlib import asynccontextmanager
import os
from fastapi.responses import FileResponse

# Initialize background scheduler
scheduler = BackgroundScheduler()

# Scheduled scan job
def scheduled_horizon_scan():
    print("⏰ Scheduled horizon scan started...")

    topics = ["AI engineer", "market trends", "digital transformation", "competitor PR"]
    all_articles = []

    for topic in topics:
        articles = fetch_google_news(topic, max_articles=10)
        all_articles.extend(articles)

    # Save CSV with timestamp
    filename = f"{datetime.now().strftime('%Y-%m-%d')}-horizon-scan.csv"
    save_articles_to_csv(all_articles, filename=filename)

    print(f"✅ {len(all_articles)} articles saved to {filename}")

# FastAPI app with modern lifespan hook
@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.add_job(scheduled_horizon_scan, trigger="cron", hour=6, minute=0)
    scheduler.start()
    print("🚀 Scheduler started")
    yield
    scheduler.shutdown()
    print("🛑 Scheduler stopped")

app = FastAPI(lifespan=lifespan)

# Allow API access from anywhere (for GPT)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================
# ✅ ROUTES
# ============================

# Live news fetch
@app.get("/latest-news")
def latest_news(query: Optional[str] = "AI market trends", max_articles: Optional[int] = 20):
    news = fetch_google_news(query, max_articles)
    return {"articles": news}

# List all saved reports
@app.get("/reports")
def list_reports():
    files = [f for f in os.listdir(".") if f.endswith("-horizon-scan.csv")]
    return {"reports": sorted(files)}

# Download individual report
@app.get("/reports/{filename}")
def download_report(filename: str):
    file_path = os.path.join(".", filename)
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="text/csv", filename=filename)
    return {"error": "File not found"}
