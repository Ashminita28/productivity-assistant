import streamlit as st
import requests
import uuid
import os

BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")

def render_sidebar():
    with st.sidebar:
        st.header("Chat History")
        
        if st.button("💬 New Chat", use_container_width=True):
            st.session_state.thread_id = str(uuid.uuid4())
            st.query_params["thread_id"] = st.session_state.thread_id
            st.session_state.messages = []
            st.rerun()
            
        st.divider()
        st.header("Your Task Board")
        st.button("Refresh Task Board")
        
        try:
            task_res = requests.get(f"{BACKEND_URL}/tasks")
            if task_res.status_code == 200:
                tasks = task_res.json()
                if not tasks:
                    st.info("Your board is empty! Add a task to get started.")
                else:
                    for t in tasks:
                        status_icon = "✅" if str(t.get("status", "")).lower() == "completed" else "⏳"
                        st.markdown(f"""
                        <div style='padding: 10px; margin-bottom: 10px; border-radius: 5px; border: 1px solid #ddd;'>
                            <span style='font-size: 1.2em;'>{status_icon}</span> <strong>{t['description']}</strong><br/>
                            <small style='color: gray;'>ID: {t['id']} | Status: {t['status']}</small>
                        </div>
                        """, unsafe_allow_html=True)
        except Exception:
            st.error("Could not load tasks from database.")
