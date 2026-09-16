import streamlit as st
import requests
import uuid


st.set_page_config(
    page_title="AI Productivity Assistant", 
    layout="centered"
)

st.title("AI Productivity Assistant")
st.markdown("Manage your tasks using natural language! Try saying: *'Add a task to buy groceries'*")


with st.sidebar:
    st.header("📋 Your Task Board")
    
   
    st.button("🔄 Refresh Task Board")
    
    try:
        task_res = requests.get("http://localhost:8000/tasks")
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

if "messages" not in st.session_state:
    st.session_state.messages = []
if "thread_id" not in st.session_state:
    
    st.session_state.thread_id = str(uuid.uuid4())


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
                    "http://localhost:8000/chat",
                    json={"user_input": prompt, "thread_id": st.session_state.thread_id}
                )
                res.raise_for_status()
                
               
                assistant_response = res.json()["response"]
                st.markdown(assistant_response)
                
                
                st.session_state.messages.append({"role": "assistant", "content": assistant_response})
                
               
                st.rerun()
                
            except requests.exceptions.ConnectionError:
                st.error("🚨 Could not connect to the backend! Is FastAPI running?")
            except Exception as e:
                st.error(f"An error occurred: {e}")
