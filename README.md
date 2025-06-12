# Apple WWDC 2025 — Headline‑Sentiment Dashboard 

This project scrapes **Google News RSS** for the past week of headlines about Apple’s WWDC 2025 announcements, labels each headline with **VADER** and **FinBERT** sentiment, and serves the results in a responsive **Streamlit** dashboard that auto‑refreshes every 10 minutes. A cron job (or Streamlit‑embedded refresh) keeps the dataset evergreen.

---

## ✨ Key Features

| Layer                | What it does                                                                              |
| -------------------- | ----------------------------------------------------------------------------------------- |
| **Scraper**          | Pulls `q="Apple WWDC 2025" when:7d` RSS, dedupes & timestamps headlines │ `src/scrape.py` |
| **Sentiment Engine** | VADER for quick polarity + FinBERT for finance‑tuned 3‑class score │ `src/sentiment.py`   |
| **Pipeline Driver**  | One command: _scrape → label → save CSV_ │ `src/main.py`                                  |
| **Dashboard**        | Word‑cloud, sentiment counts, daily trend line, filterable table │ `streamlit_app.py`     |
| **Scheduler**        | 1‑line macOS/Linux cron (or inline refresh) every 10 min                                  |

---

## 🚀 Quick Start

```bash
# clone & set‑up
git clone https://github.com/lunanguyen/watai-sentiment-analysis.git
cd watai-sentiment-analysis
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m nltk.downloader vader_lexicon punkt stopwords

# one‑off scrape + label
python -m src.main

# launch dashboard
streamlit run streamlit_app.py
```

### (Optional) 10‑minute cron

```cron
*/10 * * * * cd /Users/<you>/watai-sentiment-analysis && \
  /Users/<you>/watai-sentiment-analysis/.venv/bin/python -m src.main \
  >> /Users/<you>/watai-sentiment-analysis/logs/cron.log 2>&1
```

The dashboard uses `st_autorefresh` (600 s TTL) so new CSVs appear automatically.

---

## 📊 Current Findings  *(snapshot 2025‑06‑11)*

| Metric            |   Count |
| ----------------- | ------: |
| Headlines scraped | **100** |
| 😊 Positive       |  **94** |
| 😐 Neutral        |   **2** |
| ☹️ Negative       |   **4** |

### Sentiment Insights

- **Dominant positivity** — >90 % of coverage hails WWDC features (VisionOS, AI integration).
- **Brief negativity spike** on **9 June** linked to articles about potential M4 chip delays.
- **Word Clouds**

  - *Positive* — `upgrade`, `AI`, `breakthrough`, `developer`, `VisionOS`
  - *Neutral*  — generic terms like `live`, `event`, `recap`
  - _Negative_ — `delay`, `overhyped`, `shortage`, `price`

### Visual Preview _(generated in dashboard)_

```
image/barchart_sentiment_count.png   ← bar chart  |  image/line_chart_avg_sentiment_Score_finBERT.png  ← daily avg line
image/wordcloud_positive_headlines.png
```

(Add exported PNGs to the `image/` folder so GitHub displays them.)

---

## 🗂 Repo Structure

```
.
├─ data/                # raw & processed CSVs (git‑ignored)
├─ logs/                # cron output (git‑ignored)
├─ src/
│   ├─ scrape.py        # RSS download & clean
│   ├─ sentiment.py     # VADER & FinBERT labelling
│   ├─ main.py          # pipeline orchestrator
│   └─ viz.py           # matplotlib utilities (optional)
├─ streamlit_app.py     # dashboard UI
├─ requirements.txt     # Python deps
└─ README.md            # you’re reading it!
```

---

## 🛠 Future Work

- Overlay **AAPL intraday returns** vs. sentiment trend.
- Add **Reddit r/Apple** & X (Twitter) data sources.
- Deploy to **Streamlit Community Cloud** with scheduled jobs.

---

© 2025 Luna Nguyen — MIT License
