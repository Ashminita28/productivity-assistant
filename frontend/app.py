import os
import streamlit as st
import requests
import uuid
import json

BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")

st.set_page_config(
    page_title="AI Productivity Assistant", 
    layout="centered"
)

st.title("AI Productivity Assistant")
st.markdown("Manage your tasks using natural language! Try saying: *'Add a task to buy groceries'*")


with st.sidebar:
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
    except Exception as e:
        st.error("Could not load tasks from database.")

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
    except Exception as e:
        pass 


for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


if prompt := st.chat_input("What do you want to do today?"):
  
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    
   
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                
                
                res = requests.post(
                    f"{BACKEND_URL}/chat/stream",
                    json={"user_input": prompt, "thread_id": st.session_state.thread_id},
                    stream=True
                )
                res.raise_for_status()
                
                def stream_parser():
                   
                    for chunk in res.iter_content(chunk_size=None, decode_unicode=True):
                        if chunk:
                            yield chunk
                           
                assistant_response = st.write_stream(stream_parser())
                
               
                if '{"requires_approval": true' in assistant_response:
                    parts = assistant_response.split('{"requires_approval": true')
                    display_text = parts[0].strip()
                    payload = json.loads('{"requires_approval": true' + parts[1])
                    
                    if display_text:
                        st.session_state.messages.append({"role": "assistant", "content": display_text})
                    st.session_state.pending_approval = payload
                    st.rerun()
                else:
                    st.session_state.messages.append({"role": "assistant", "content": assistant_response})
                    st.rerun()
                
            except requests.exceptions.ConnectionError:
                st.error("Could not connect to the backend! Is FastAPI running?")
            except Exception as e:
                st.error(f"An error occurred: {e}")

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
