import os, json, time, feedparser, streamlit as st, logging
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

load_dotenv()
TOKEN = os.getenv("AWS_BEARER_TOKEN_BEDROCK")
REGION = "eu-central-1"
MODEL = "amazon.titan-text-lite-v1"

# Initialize Bedrock runtime client
try:
    bedrock = boto3.client(
        "bedrock-runtime",
        region_name=REGION,
        aws_session_token=TOKEN,
        config=Config(retries={"max_attempts": 3})
    )
    logger.info("Initialized Bedrock client.")
except Exception as e:
    logger.error("Failed to initialize Bedrock client: %s", e)
    st.error("⚠️ Could not connect to AWS Bedrock. Check your token and region.")
    st.stop()

def invoke_bedrock(prompt: str) -> str:
    payload = {"inputText": prompt}
    try:
        resp = bedrock.invoke_model(
            modelId=MODEL,
            body=json.dumps(payload),
            contentType="application/json"
        )
        result = json.loads(resp["body"].read())
        text = result["results"][0]["outputText"].strip()
        logger.info("Bedrock invocation successful.")
        return text
    except ClientError as err:
        logger.error("Bedrock API error: %s", err)
        return "❗ Translation failed (API error)."
    except Exception as e:
        logger.error("Unexpected error: %s", e)
        return "❗ Translation failed."

def translate_text(text: str) -> str:
    prompt = f"Translate the following text to English:\n\n{text}"
    return invoke_bedrock(prompt)

st.title("🗾 Japan RSS News Summarizer")

# Controls
interval = st.sidebar.number_input("Refresh every X seconds", min_value=30, value=300, step=30)
if "feed" not in st.session_state:
    st.session_state.feed = []
    st.session_state.last = 0

def fetch_japan_rss():
    url = "https://www3.nhk.or.jp/rss/news/cat0.xml"
    logger.info("Fetching RSS feed from %s", url)
    return feedparser.parse(url).entries[:5]

# Refresh logic
if st.sidebar.button("Refresh Now") or time.time() - st.session_state.last > interval:
    st.session_state.feed = fetch_japan_rss()
    st.session_state.last = time.time()

# Display each news with translate option
for idx, entry in enumerate(st.session_state.feed):
    with st.container():
        st.markdown(f"### {entry.title}")
        st.write(entry.summary)
        
        # Translate button per row
        trans_key = f"trans_{idx}"
        if st.button("Translate", key=trans_key):
            st.write("📝 Translating…")
            translated = translate_text(entry.summary)
            st.write(f"**Translation:** {translated}")

        st.write("---")
