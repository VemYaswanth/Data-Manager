import streamlit as st
import requests
import json

API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="AI Assistant",
    page_icon="🤖",
    layout="wide"
)

# -------------------------
# Title & Description
# -------------------------
st.title("🤖 Local AI Assistant — Secure File Vault")

st.markdown("""
Ask anything about your encrypted files.  
Your AI runs **100% offline** on your MiniPC.

Use the filters in the sidebar to restrict the AI
to a specific project, tag, or file type.
""")

# -------------------------
# Chat history session state
# -------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "last_sources" not in st.session_state:
    st.session_state.last_sources = []


# -------------------------
# Backend Communication
# -------------------------
def ask_ai(question: str, project_id=None, tag=None, ext=None):
    """Send request to FastAPI AI engine with filters."""
    params = {"q": question}

    if project_id:
        params["project_id"] = project_id
    if tag:
        params["tag"] = tag
    if ext:
        params["ext"] = ext

    try:
        response = requests.get(f"{API_URL}/ai/ask", params=params)
        return response.json()
    except Exception as e:
        return {"answer": "Error contacting server.", "error": str(e), "sources": []}


# -------------------------
# Sidebar filters
# -------------------------
st.sidebar.header("🔍 AI Filters")

project_input = st.sidebar.text_input("Project ID (optional)").strip()
project_id = int(project_input) if project_input.isdigit() else None

tag = st.sidebar.text_input("Tag (optional)").strip() or None
ext = st.sidebar.text_input("File Type (pdf, docx, txt, etc.)").strip() or None


# -------------------------
# Chat input area
# -------------------------
user_input = st.text_area("Ask something:", height=80, key="input_box")

col1, col2 = st.columns([1, 5])
with col1:
    send = st.button("Ask")
with col2:
    clear = st.button("Clear Chat")


# -------------------------
# Clear chat
# -------------------------
if clear:
    st.session_state.chat_history = []
    st.session_state.last_sources = []
    st.rerun()


# -------------------------
# Handle user question
# -------------------------
if send and user_input.strip():
    with st.spinner("Thinking..."):
        ai_response = ask_ai(
            user_input,
            project_id=project_id,
            tag=tag,
            ext=ext
        )

    st.session_state.chat_history.append(
        {"role": "user", "message": user_input}
    )
    st.session_state.chat_history.append(
        {"role": "assistant", "message": ai_response.get("answer", "Error")}
    )

    st.session_state.last_sources = ai_response.get("sources", [])


# -------------------------
# Render chat messages
# -------------------------
for msg in st.session_state.chat_history:
    if msg["role"] == "user":
        st.markdown(f"### 🧑 You:\n{msg['message']}")
    else:
        st.markdown(f"### 🤖 Assistant:\n{msg['message']}")

# -------------------------
# Render sources
# -------------------------
if st.session_state.last_sources:
    st.markdown("---")
    st.markdown("### 📄 Files used in this answer:")
    for f in st.session_state.last_sources:
        st.markdown(f"- **{f}**")
