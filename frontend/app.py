import streamlit as st
from utils.state import initialize_session_state
from components.sidebar import render_sidebar
from components.chat import render_chat_interface
from components.approval import render_approval_ui

st.set_page_config(
    page_title="AI Productivity Assistant", 
    layout="centered"
)

st.title("AI Productivity Assistant")
st.markdown("Manage your tasks using natural language! Try saying: *'Add a task to buy groceries'*")

initialize_session_state()
render_sidebar()
render_chat_interface()
render_approval_ui()
