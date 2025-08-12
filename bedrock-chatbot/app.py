import os
import json
import streamlit as st
import boto3
from botocore.config import Config
from dotenv import load_dotenv

load_dotenv()

# Use the bearer token from environment
TOKEN = os.getenv("AWS_BEARER_TOKEN_BEDROCK")
REGION = "eu-central-1"
MODEL_ID = "amazon.titan-text-lite-v1"

config = Config(
    region_name=REGION,
    retries={"max_attempts": 3},
)

bedrock = boto3.client(
    "bedrock-runtime",
    region_name=REGION,
    aws_session_token=TOKEN,
    config=config,
)

st.title("💬 Bedrock + Titan Text G1 Lite Chatbot")

if "history" not in st.session_state:
    st.session_state.history = []

def invoke_bedrock(prompt: str) -> str:
    payload = json.dumps({"inputText": prompt})
    resp = bedrock.invoke_model(
        modelId=MODEL_ID,
        body=payload,
        contentType="application/json"
    )
    result = json.loads(resp["body"].read())
    return result["results"][0]["outputText"]

def chat():
    user_input = st.text_input("You:", key="input")
    if user_input:
        st.session_state.history.append(("You", user_input))
        prompt = "\n".join(f"{u}: {m}" for u, m in st.session_state.history) + "\nAssistant:"
        reply = invoke_bedrock(prompt)
        st.session_state.history.append(("Assistant", reply))
    for speaker, msg in st.session_state.history:
        if speaker == "You":
            st.markdown(f"**You**: {msg}")
        else:
            st.markdown(f"**Assistant**: {msg}")

def clear_chat():
    st.session_state.history = []

st.sidebar.button("Clear chat", on_click=clear_chat)
chat()
