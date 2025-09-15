import os
import requests
import streamlit as st

st.set_page_config(page_title="Frontend Demo", page_icon="🔢")
st.title("Frontend Demo")

backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")

st.subheader("Counter")
if st.button("Increment"):
    try:
        r = requests.get(f"{backend_url}/count", timeout=5)
        r.raise_for_status()
        st.success(f"Count: {r.json().get('count')}")
    except Exception as e:
        st.error(f"Error: {e}")