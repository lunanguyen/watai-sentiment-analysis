"""
main.py
-------
End-to-end driver: scrape → label → plots
"""

import datetime as dt, subprocess, pathlib, pandas as pd
from .scrape import google_news_rss, save_csv
from .sentiment import label_dataframe
from .viz import bar_chart, line_plot, word_cloud

def run_pipeline():
    today = dt.date.today().isoformat()
    raw_fname = f"apple_wwdc_raw_{today}.csv"
    proc_fname = f"headlines_{today}.csv"

    # 1, 2. scrape
    articles = google_news_rss("Apple WWDC 2025", days_back=7)
    save_csv(articles, raw_fname)

    # 3. label
    import pandas as pd, pathlib
    df_raw = pd.read_csv(pathlib.Path("data/raw") / raw_fname)
    df_labeled = label_dataframe(df_raw)
    out_path = pathlib.Path("data/processed") / proc_fname
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df_labeled.to_csv(out_path, index=False)

    # 4. visuals
    bar_chart(df_labeled)
    line_plot(df_labeled)
    word_cloud(df_labeled, "positive")

if __name__ == "__main__":
    run_pipeline()
