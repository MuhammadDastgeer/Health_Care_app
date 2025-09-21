import streamlit as st
import uuid
from backend import generate_response, get_chat_history
from pdfminer.high_level import extract_text
from PIL import Image
import io

st.set_page_config(page_title="Doctor AI Chatbot", layout="wide", page_icon="🩺")

# Initialize session state
if "chat_id" not in st.session_state:
    st.session_state.chat_id = str(uuid.uuid4())

if "tabs" not in st.session_state:
    st.session_state.tabs = [st.session_state.chat_id]

if "chat_histories" not in st.session_state:
    st.session_state.chat_histories = {st.session_state.chat_id: []}

if "uploaded_file" not in st.session_state:
    st.session_state.uploaded_file = None

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sidebar-header {
        font-size: 1.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sidebar .sidebar-content {
        background-color: #f0f2f6;
    }
    .chat-button {
        background-color: #1f77b4;
        color: white;
        border-radius: 5px;
        padding: 0.5rem;
        margin: 0.25rem 0;
        text-align: center;
        cursor: pointer;
    }
    .chat-button:hover {
        background-color: #1668a5;
    }
    .upload-box {
        border: 2px dashed #1f77b4;
        border-radius: 5px;
        padding: 1rem;
        text-align: center;
        margin: 1rem 0;
        background-color: #f9f9f9;
    }
    .stButton button {
        width: 100%;
    }
    .active-chat {
        background-color: #1f77b4 !important;
        color: white !important;
        border-left: 4px solid #ff4b4b !important;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("<h2 class='sidebar-header'>🩺 Doctor AI</h2>", unsafe_allow_html=True)

    # New Chat
    if st.button("➕ New Chat", use_container_width=True):
        new_id = str(uuid.uuid4())
        st.session_state.chat_id = new_id
        if new_id not in st.session_state.tabs:
            st.session_state.tabs.append(new_id)
        if new_id not in st.session_state.chat_histories:
            st.session_state.chat_histories[new_id] = []
        st.session_state.uploaded_file = None
        st.rerun()

    # Chat tabs
    st.markdown("### Your Chats")
    for i, cid in enumerate(st.session_state.tabs):
        label = f"Chat {i+1}"
        is_active = cid == st.session_state.chat_id
        if st.button(label, key=cid, use_container_width=True):
            st.session_state.chat_id = cid
            st.rerun()

    # File Upload Section
    st.markdown("---")
    st.markdown("### Upload Files")
    st.markdown("<div class='upload-box'>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Upload PDF or Image", 
        type=["pdf", "png", "jpg", "jpeg"],
        label_visibility="collapsed"
    )
    st.markdown("</div>", unsafe_allow_html=True)

    if uploaded_file:
        st.session_state.uploaded_file = uploaded_file
        st.success("File uploaded successfully!")

        if st.button("Analyze File", type="primary", use_container_width=True):
            try:
                if uploaded_file.type == "application/pdf":
                    text = extract_text(io.BytesIO(uploaded_file.read()))
                    with st.spinner("Analyzing PDF..."):
                        response = generate_response(st.session_state.chat_id, f"Analyze this document: {text[:1000]}")
                    st.session_state.chat_histories[st.session_state.chat_id].append(("user", "Uploaded a PDF"))
                    st.session_state.chat_histories[st.session_state.chat_id].append(("assistant", response))
                else:
                    img = Image.open(uploaded_file)
                    with st.spinner("Analyzing Image..."):
                        response = generate_response(st.session_state.chat_id, "Analyze this image.")
                    st.session_state.chat_histories[st.session_state.chat_id].append(("user", "Uploaded an image"))
                    st.session_state.chat_histories[st.session_state.chat_id].append(("assistant", response))
            except Exception as e:
                error_msg = f"Error processing file: {str(e)}"
                st.session_state.chat_histories[st.session_state.chat_id].append(("assistant", error_msg))
                st.error(error_msg)
            st.rerun()

# Main chat area
st.markdown("<h1 class='main-header'>Doctor AI - Smart Assistant</h1>", unsafe_allow_html=True)

if st.session_state.chat_id in st.session_state.chat_histories:
    for role, msg in st.session_state.chat_histories[st.session_state.chat_id]:
        with st.chat_message(role):
            st.write(msg)

# Chat input
user_input = st.chat_input("Ask me anything...")

if user_input:
    st.session_state.chat_histories[st.session_state.chat_id].append(("user", user_input))
    with st.spinner("Thinking..."):
        response = generate_response(st.session_state.chat_id, user_input)
    st.session_state.chat_histories[st.session_state.chat_id].append(("assistant", response))
    st.rerun()

# Footer
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: #666;'>Doctor AI - For informational purposes only. Not a substitute for professional advice.</p>", 
    unsafe_allow_html=True
)
