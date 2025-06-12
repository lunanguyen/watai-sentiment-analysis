# streamlit_app.py  — 4-column header + same-size charts
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import pathlib, datetime as dt
from streamlit_autorefresh import st_autorefresh

# ------------------------------------------------- page config
st.set_page_config(page_title="WWDC-25 Headline Sentiment",
                   page_icon="🍎", layout="wide")

st_autorefresh(interval=600_000, key="datarefresh")   # 10-min refresh

# inside load_latest_dataframe()
@st.cache_data(ttl=600)
def load_latest_dataframe():
    data_dir = pathlib.Path("data/processed")
    data_dir.mkdir(parents=True, exist_ok=True)      # make sure folder exists
    files = sorted(data_dir.glob("headlines_*.csv"))

    # If no processed CSV yet, run the scraper/labeler once
    if not files:
        with st.spinner("⏳ First-time run: scraping headlines…"):
            subprocess.run([sys.executable, "-m", "src.main"], check=True)
            files = sorted(data_dir.glob("headlines_*.csv"))
        if not files:
            st.error("Failed to create initial dataset.")
            st.stop()

    latest = files[-1]
    df = pd.read_csv(latest)
    df["date"] = pd.to_datetime(df["published"]).dt.date
    last_mtime = dt.datetime.fromtimestamp(latest.stat().st_mtime)
    return df, last_mtime

df, last_mtime = load_latest_dataframe()

# ------------------------------------------------- header
st.title("🍎 Apple WWDC 2025 — Headline Sentiment")

tot = len(df)
pos = (df["finbert_label"] == "positive").sum()
neu = (df["finbert_label"] == "neutral").sum()
neg = (df["finbert_label"] == "negative").sum()

h_tot, h_pos, h_neu, h_neg = st.columns(4)
h_tot.metric("📰 Total",   f"{tot:,}")
h_pos.metric("😊 Positive", f"{pos:,}")
h_neu.metric("😐 Neutral",  f"{neu:,}")
h_neg.metric("☹️ Negative", f"{neg:,}")

st.markdown("---")

# ------------------------------------------------- sidebar filters
st.sidebar.header("🔍 Filters")
dmin, dmax = df["date"].min(), df["date"].max()
date_rng = st.sidebar.slider("Headline date", dmin, dmax, (dmin, dmax),
                             format="YYYY-MM-DD")

sentims = st.sidebar.multiselect("Sentiment category",
                                 ["positive", "neutral", "negative"],
                                 default=["positive", "neutral", "negative"])

kw = st.sidebar.text_input("Keyword search (optional)").strip().lower()

mask = df["date"].between(*date_rng) & df["finbert_label"].isin(sentims)
if kw:
    mask &= df["title"].str.lower().str.contains(kw)
df_filt = df.loc[mask]

# ------------------------------------------------- KPI cards (filtered)
f_pos, f_neu, f_neg = (
    (df_filt["finbert_label"] == lab).sum()
    for lab in ("positive", "neutral", "negative")
)
k1, k2, k3 = st.columns(3)
k1.metric("😊 Positive (filtered)", f_pos)
k2.metric("😐 Neutral (filtered)",  f_neu)
k3.metric("☹️ Negative (filtered)", f_neg)
st.markdown("---")

# ------------------------------------------------- charts (equal size)
FIG_W, FIG_H = 6, 4
c_left, c_right = st.columns(2)

with c_left:
    st.subheader("Sentiment Counts")
    fig1, ax1 = plt.subplots(figsize=(FIG_W, FIG_H))
    sns.countplot(x="finbert_label", data=df_filt,
                  order=["positive", "neutral", "negative"],
                  palette=["#2ecc71", "#f1c40f", "#e74c3c"], ax=ax1)
    ax1.set_xlabel(""); ax1.set_ylabel("Headlines")
    st.pyplot(fig1, use_container_width=True)

with c_right:
    st.subheader("Daily Avg. Sentiment Score")
    daily = (df_filt.groupby("date")["finbert_score"]
             .mean()
             .reindex(pd.date_range(dmin, dmax), fill_value=None))
    fig2, ax2 = plt.subplots(figsize=(FIG_W, FIG_H))
    daily.plot(marker="o", ax=ax2, color="#3498db")
    ax2.set_ylabel("Mean class prob."); ax2.set_xlabel("")
    st.pyplot(fig2, use_container_width=True)

# ------------------------------------------------- word cloud
st.subheader("Word Cloud")
wc_choice = st.radio("Choose sentiment:",
                     ["positive", "neutral", "negative"], horizontal=True)
cloud_text = " ".join(df_filt[df_filt.finbert_label == wc_choice]["title"])
if cloud_text:
    wc = WordCloud(width=900, height=400,
                   background_color="white").generate(cloud_text)
    fig3, ax3 = plt.subplots(figsize=(9, 4))
    ax3.imshow(wc, interpolation="bilinear"); ax3.axis("off")
    st.pyplot(fig3)
else:
    st.info("No headlines match the current filters.")

st.markdown("---")

# ------------------------------------------------- data table
st.subheader("Headline Details")
st.dataframe(df_filt[["title", "source", "finbert_score",
                      "finbert_label", "published"]]
             .rename(columns={
                 "title": "Headline",
                 "source": "Source",
                 "finbert_score": "Score",
                 "finbert_label": "Sentiment",
                 "published": "Published (UTC)",
             }),
             use_container_width=True, height=450)

# ------------------------------------------------- footer
last_dt = last_mtime.astimezone().strftime("%Y-%m-%d %H:%M %Z")
st.caption(f"Showing **{len(df_filt):,d}** of {len(df):,d} headlines • "
           f"last scraped: **{last_dt}** • auto-refresh 10 min")
