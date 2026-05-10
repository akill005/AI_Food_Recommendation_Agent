import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000/agent"

st.set_page_config(
    page_title="Swiggy AI Food Recommendation Agent",
    page_icon="🍛"
)

st.title("🍛 Swiggy AI Food Recommendation Agent")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:

    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

prompt = st.chat_input("What do you want to eat?")

if prompt:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    try:

        res = requests.get(
            API_URL,
            params={"query": prompt}
        )

        data = res.json()

        reply = data["response"]

    except Exception as e:

        reply = f"Backend Error: {str(e)}"

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": reply
        }
    )

    with st.chat_message("assistant"):
        st.markdown(reply)