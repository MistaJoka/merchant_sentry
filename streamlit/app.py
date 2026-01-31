import streamlit as st
import google.generativeai as genai
import requests
import os
import json
from dotenv import load_dotenv

# --- CONFIGURATION ---
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL")

# Configure Gemini
if not GEMINI_API_KEY:
    st.error("❌ GEMINI_API_KEY not found in environment variables.")
    st.stop()

genai.configure(api_key=GEMINI_API_KEY)

# --- AI LOGIC (The Cleaner) ---
def parse_with_gemini(raw_text):
    """Uses local Gemini to structure messy text into JSON."""
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"""
    Extract Merchant KYC details from the text below.
    Return ONLY valid JSON. Keys: candidate_name, business_name, address, phone, email.
    If missing, use null.
    
    RAW TEXT:
    {raw_text}
    """
    try:
        response = model.generate_content(prompt)
        clean_json = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean_json)
    except Exception as e:
        return {"error": str(e)}

# --- UI LAYOUT ---
st.set_page_config(page_title="Merchant Sentry", layout="wide")
st.title("🛡️ Merchant Sentry: Agentic Workflow")

col1, col2 = st.columns(2)

# LEFT COLUMN: Ingestion
with col1:
    st.subheader("1. Raw Data Ingestion")
    raw_input = st.text_area("Paste Salesforce/Stripe Data:", height=300, 
        placeholder="Name: John Doe\nBusiness: JD Tech LLC\n...")
    
    if st.button("🚀 Parse Data"):
        if raw_input:
            with st.spinner("Gemini is structuring the data..."):
                extracted = parse_with_gemini(raw_input)
                st.session_state['extracted_data'] = extracted
                st.session_state['step'] = 1
        else:
            st.warning("Please paste some text first.")

# RIGHT COLUMN: Verification
with col2:
    st.subheader("2. Verification Agents")
    
    if 'extracted_data' in st.session_state:
        data = st.session_state['extracted_data']
        
        # specific form container
        with st.form("verify_form"):
            # Allow user to edit AI mistakes before sending to agents
            c_name = st.text_input("Candidate Name", value=data.get('candidate_name'))
            b_name = st.text_input("Business Name", value=data.get('business_name'))
            
            # HIDDEN PAYLOAD
            payload = {"candidate_name": c_name, "business_name": b_name}
            
            verify_btn = st.form_submit_button("⚡ Run Agent Swarm (Verify)")
            
            if verify_btn:
                with st.spinner("Agents are investigating (OpenCorporates + OFAC)..."):
                    try:
                        # Send to n8n Webhook
                        response = requests.post(N8N_WEBHOOK_URL, json=payload)
                        if response.status_code == 200:
                            st.success("Analysis Complete")
                            st.json(response.json())
                        else:
                            st.error(f"Agent Error: {response.status_code}")
                    except Exception as e:
                        st.error(f"Connection Failed: {e}")