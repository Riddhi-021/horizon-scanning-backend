# fetch_news.py

import feedparser
import pandas as pd

def fetch_google_news(query, max_articles=20):
    base_url = "https://news.google.com/rss/search?q="
    query_encoded = query.replace(' ', '+')
    feed_url = f"{base_url}{query_encoded}"

    feed = feedparser.parse(feed_url)
    articles = []

    for entry in feed.entries[:max_articles]:
        article = {
            'title': entry.title,
            'link': entry.link,
            'published': entry.published if 'published' in entry else 'N/A',
            'summary': entry.summary if 'summary' in entry else 'N/A',
            'source': entry.source.title if 'source' in entry else 'N/A'
        }
        articles.append(article)

    return articles

def save_articles_to_csv(articles, filename="news_articles.csv"):
    df = pd.DataFrame(articles)
    df.to_csv(filename, index=False)
    print(f"Saved {len(articles)} articles to {filename}")

if __name__ == "__main__":
    query = input("Enter a topic for news search: ")  # e.g., "AI market trends"
    news = fetch_google_news(query, max_articles=20)
    save_articles_to_csv(news)
