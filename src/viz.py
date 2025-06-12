"""
viz.py
------
Quick-and-dirty visuals for labeled headline data.
"""

import pandas as pd, matplotlib.pyplot as plt, seaborn as sns, pathlib
from wordcloud import WordCloud

def bar_chart(df, label_col="finbert_label"):
    ax = sns.countplot(x=label_col, data=df, order=["positive", "neutral", "negative"])
    ax.set_title("Headline Sentiment Counts")
    plt.show()

def line_plot(df, score_col="finbert_score"):
    df["date"] = pd.to_datetime(df["published"]).dt.date
    daily = df.groupby("date")[score_col].mean()
    daily.plot(marker="o")
    plt.title("Average Sentiment Score by Day (FinBERT)")
    plt.ylabel("Mean prob. of predicted class")
    plt.show()

def word_cloud(df, label="positive"):
    text = " ".join(df[df.finbert_label == label]["title"])
    wc = WordCloud(width=800, height=400, background_color="white").generate(text)
    plt.imshow(wc, interpolation="bilinear")
    plt.axis("off")
    plt.title(f"Word Cloud – {label.title()} Headlines")
    plt.show()

if __name__ == "__main__":
    DATA = pathlib.Path(__file__).parents[1] / "data" / "processed"
    latest = sorted(DATA.glob("headlines_*.csv"))[-1]
    df = pd.read_csv(latest)
    bar_chart(df)
    line_plot(df)
    word_cloud(df, "positive")
