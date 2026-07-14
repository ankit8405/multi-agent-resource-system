import uuid

import requests
import streamlit as st

BACKEND_URL = "http://localhost:8000/api/research"

st.set_page_config(
    page_title="Multi-Agent Research System",
    page_icon="📚",
    layout="wide",
)

st.title("📚 Multi-Agent Research System")
st.caption("AI-powered autonomous research using multiple specialized agents.")

# Persist a thread across reruns
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

if "conversation_summary" not in st.session_state:
    st.session_state.conversation_summary = ""

if "previous_query" not in st.session_state:
    st.session_state.previous_query = ""

query = st.text_area(
    "Research Query",
    placeholder="Example: Compare Retrieval-Augmented Generation and fine-tuning for enterprise AI systems.",
    height=150,
)

if st.button("Generate Report", type="primary", use_container_width=True):

    if not query.strip():
        st.warning("Please enter a research query.")
        st.stop()

    payload = {
        "query": query,
        "thread_id": st.session_state.thread_id,
        "previous_query": st.session_state.previous_query,
        "conversation_summary": st.session_state.conversation_summary,
    }

    with st.spinner("Research agents are working..."):

        try:
            response = requests.post(
                BACKEND_URL,
                json=payload,
                timeout=300,
            )

            response.raise_for_status()

            data = response.json()

            report = data["report"]

            st.markdown("---")
            st.markdown(report)

            st.session_state.previous_query = query

            # Placeholder until conversation summarization is implemented
            st.session_state.conversation_summary = report[:1000]

        except Exception as e:
            st.error(f"Request failed:\n\n{e}")