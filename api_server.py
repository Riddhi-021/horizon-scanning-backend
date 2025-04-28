# api_server.py

from fastapi import FastAPI
from fetch_news import fetch_google_news
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow public access for now
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/latest-news")
def latest_news(query: Optional[str] = "AI market trends", max_articles: Optional[int] = 20):
    news = fetch_google_news(query, max_articles)
    return {"articles": news}
