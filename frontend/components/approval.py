import streamlit as st
import requests
import os

BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")

def render_approval_ui():
    if st.session_state.get("pending_approval"):
        payload = st.session_state.pending_approval
        with st.chat_message("assistant"):
            st.warning(f"⚠️ The AI wants to use `{payload['tool']}` with args: {payload['args']}")
            col1, col2 = st.columns(2)
            if col1.button("✅ Approve"):
                with st.spinner("Executing..."):
                    res = requests.post(f"{BACKEND_URL}/chat/respond_interrupt", json={"thread_id": st.session_state.thread_id, "approved": True}, stream=True)
                    def stream_parser():
                        for chunk in res.iter_content(chunk_size=None, decode_unicode=True):
                            if chunk: yield chunk
                    final_text = st.write_stream(stream_parser())
                    st.session_state.messages.append({"role": "assistant", "content": final_text})
                    st.session_state.pending_approval = None
                    st.rerun()
                    
            if col2.button("❌ Reject"):
                with st.spinner("Rejecting..."):
                    res = requests.post(f"{BACKEND_URL}/chat/respond_interrupt", json={"thread_id": st.session_state.thread_id, "approved": False}, stream=True)
                    def stream_parser():
                        for chunk in res.iter_content(chunk_size=None, decode_unicode=True):
                            if chunk: yield chunk
                    final_text = st.write_stream(stream_parser())
                    st.session_state.messages.append({"role": "assistant", "content": final_text})
                    st.session_state.pending_approval = None
                    st.rerun()
