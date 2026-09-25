import streamlit as st
import requests
import json
import os

BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")

def render_chat_interface():
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("What do you want to do today?"):
        pass 

   
    if "auto_prompt" in st.session_state and st.session_state.auto_prompt:
        prompt = st.session_state.auto_prompt
        st.session_state.auto_prompt = None
        
    if prompt:
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("assistant"):
            try:
                res = requests.post(
                    f"{BACKEND_URL}/chat/stream",
                    json={"user_input": prompt, "thread_id": st.session_state.thread_id},
                    stream=True
                )
                res.raise_for_status()
                
                def stream_parser():
                    for chunk in res.iter_content(chunk_size=1, decode_unicode=True):
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
