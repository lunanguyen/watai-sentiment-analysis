"""
scrape.py
---------
Pull recent Google News headlines for a search query.
"""

from __future__ import annotations
import feedparser, pathlib, datetime as dt, csv, re

DATA_DIR = pathlib.Path(__file__).parents[1] / "data" / "raw"
DATA_DIR.mkdir(parents=True, exist_ok=True)

USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/126.0 Safari/537.36"
)

def google_news_rss(query: str, days_back: int = 7) -> list[dict]:
    url = (
        "https://news.google.com/rss/search?"
        f"q={query.replace(' ', '+')}+when:{days_back}d&hl=en&gl=US&ceid=US:en"
    )
    feed = feedparser.parse(url, request_headers={"User-Agent": USER_AGENT})
    articles: list[dict] = []
    for entry in feed.entries:
        articles.append(
            {
                "title": re.sub(r"\s+", " ", entry.title.strip()),
                "link": entry.link,
                "published": entry.published,  # e.g. 'Tue, 10 Jun 2025 14:03:00 GMT'
                "source": entry.get("source", {}).get("title", "Unknown"),
            }
        )
    return articles


def save_csv(records: list[dict], fname: str) -> None:
    path = DATA_DIR / fname
    if not records:
        print("No records to save.")
        return
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=records[0].keys())
        writer.writeheader()
        writer.writerows(records)
    print(f"Saved {len(records)} rows → {path}")


if __name__ == "__main__":
    query = "Apple WWDC 2025"
    articles = google_news_rss(query, days_back=7)
    today = dt.date.today().isoformat()
    save_csv(articles, f"apple_wwdc_raw_{today}.csv")
