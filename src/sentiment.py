"""
sentiment.py
------------
Applies VADER and FinBERT sentiment labels.
"""

from __future__ import annotations
import pandas as pd, pathlib
from tqdm import tqdm

# ---------- VADER ----------
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
vader = SentimentIntensityAnalyzer()

def vader_label(text: str) -> tuple[str, float]:
    score = vader.polarity_scores(text)["compound"]
    if score >= 0.05:
        return "positive", score
    if score <= -0.05:
        return "negative", score
    return "neutral", score


# ---------- FinBERT ----------
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch

TOKENIZER = AutoTokenizer.from_pretrained("ProsusAI/finbert")
MODEL = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert")

def finbert_label(text: str) -> tuple[str, float]:
    inputs = TOKENIZER(text, return_tensors="pt", truncation=True)
    with torch.no_grad():
        logits = MODEL(**inputs).logits
    probs = torch.softmax(logits, dim=1)[0]
    idx = torch.argmax(probs).item()
    return ["negative", "neutral", "positive"][idx], probs[idx].item()


# ---------- Convenience wrapper ----------
def label_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    vader_out, fin_out, fin_score = [], [], []
    for title in tqdm(df["title"], desc="Sentiment"):
        v_lab, v_score = vader_label(title)
        f_lab, f_score = finbert_label(title)
        vader_out.append(v_lab)
        fin_out.append(f_lab)
        fin_score.append(f_score)
    df["vader_label"] = vader_out
    df["finbert_label"] = fin_out
    df["finbert_score"] = fin_score
    return df


if __name__ == "__main__":
    RAW = pathlib.Path(__file__).parents[1] / "data" / "raw"
    latest = sorted(RAW.glob("apple_wwdc_raw_*.csv"))[-1]
    df = pd.read_csv(latest)
    df_labeled = label_dataframe(df)
    out = pathlib.Path(__file__).parents[1] / "data" / "processed" / f"headlines_{latest.stem[-10:]}.csv"
    out.parent.mkdir(exist_ok=True, parents=True)
    df_labeled.to_csv(out, index=False)
    print(f"Labeled data → {out}")
