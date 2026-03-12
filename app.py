import streamlit as st

from services.character_service import get_all_characters
from services.prompt_builder import build_character_prompt
from services.chat_engine import chat


st.set_page_config(page_title="AI Character Chat", layout="wide")

st.title("AI Character Chat")


# =========================
# Fetch Characters
# =========================
characters = get_all_characters()

unique_ids = [c["uniqueId"] for c in characters]

selected = st.selectbox("Choose Character", unique_ids)

character = next(c for c in characters if c["uniqueId"] == selected)

system_prompt = build_character_prompt(character)


# =========================
# Reset chat when character changes
# =========================
if "current_character" not in st.session_state:
    st.session_state.current_character = selected

if selected != st.session_state.current_character:
    st.session_state.history = []
    st.session_state.current_character = selected


# =========================
# Initialize chat history
# =========================
if "history" not in st.session_state:
    st.session_state.history = []


# =========================
# Inject welcome message
# =========================
if len(st.session_state.history) == 0:

    welcome_message = character.get("welcomeMessage")

    if welcome_message:
        st.session_state.history.append({
            "role": "assistant",
            "content": welcome_message
        })


# =========================
# Sidebar Prompt Viewer
# =========================
with st.sidebar:

    st.header("System Prompt")

    st.code(system_prompt, language="text")

    st.caption(f"Prompt length: {len(system_prompt)} characters")


# =========================
# Display Chat Messages
# =========================
for msg in st.session_state.history:
    st.chat_message(msg["role"]).write(msg["content"])


# =========================
# User Input
# =========================
user_message = st.chat_input("Say something...")


if user_message:

    st.session_state.history.append({
        "role": "user",
        "content": user_message
    })

    reply = chat(system_prompt, st.session_state.history, user_message)

    st.session_state.history.append({
        "role": "assistant",
        "content": reply
    })

    st.rerun()