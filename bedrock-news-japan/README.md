# Japan News Summarizer

Streamlit app that fetches **top 5 news from Japan** via NewsAPI and summarizes each using Amazon Bedrock's Titan Text G1‑Lite.

## Setup

1. `pip install -r requirements.txt`
2. Create `.env`:
3. Run with: `streamlit run app.py`


## Usage

- Sidebar: input country code (should be `jp`), refresh interval
- Summaries auto-refresh after interval or on push
- If country ≠ `jp`, app shows "I can only show you Japan news" and stops.

## Notes

- NewsAPI call: `GET /v2/top-headlines?country=jp` :contentReference[oaicite:1]{index=1}
- Titan Text Lightning-quick summarization via AWS Bedrock
- Clear enforcement ensures only Japanese news is shown
