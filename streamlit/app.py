import streamlit as st
import os

st.title("🛡️ Merchant Sentry: System Status")
st.success("System Online: Streamlit is running.")

api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    st.info("✅ Gemini API Key Detected")
else:
    st.error("❌ Gemini API Key Missing")

st.write("Next Step: Connect to n8n via Webhook.")