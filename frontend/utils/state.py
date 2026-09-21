import streamlit as st
import uuid
import requests
import os

BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")

def initialize_session_state():
    if "thread_id" not in st.session_state:
        if "thread_id" in st.query_params:
            st.session_state.thread_id = st.query_params["thread_id"]
        else:
            st.session_state.thread_id = str(uuid.uuid4())
            st.query_params["thread_id"] = st.session_state.thread_id

    if "messages" not in st.session_state:
        st.session_state.messages = []
        try:
            res = requests.get(f"{BACKEND_URL}/chat/history/{st.session_state.thread_id}")
            if res.status_code == 200:
                st.session_state.messages = res.json().get("messages", [])
        except Exception:
            pass 
