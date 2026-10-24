import os
import requests
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Mini AI BI Assistant", page_icon="📊", layout="wide")
API_URL = os.getenv("BI_API_URL", "http://127.0.0.1:8000")

st.title("📊 Mini AI Business Intelligence Assistant")
st.caption("Ask questions about sales. Answers are calculated from the SQLite database.")

with st.sidebar:
    st.subheader("Try an example")
    examples = [
        "What is the total revenue?",
        "Which product generated the highest revenue?",
        "What is the monthly revenue trend?",
        "Which region generated the highest sales?",
        "Compare January 2026 and February 2026",
    ]
    for example in examples:
        if st.button(example, use_container_width=True):
            st.session_state["question"] = example

question = st.text_input(
    "Your question",
    key="question",
    placeholder="e.g. Which product generated the highest revenue?"
)
if st.button("Ask question", type="primary") and question.strip():
    try:
        response = requests.post(
    	    f"{API_URL}/ask",
    	    json={"question": question},
    	    timeout=90
	)
        if response.ok:
            data = response.json()
            st.subheader("Answer")
            st.write(data["answer"])
            if data.get("supporting_data"):
                st.subheader("Supporting figures")
                st.dataframe(pd.DataFrame(data["supporting_data"]), use_container_width=True, hide_index=True)
            if data.get("summary"):
                st.json(data["summary"])
            st.caption(f"Analysis: {data['intent']} · Metric: {data.get('metric', 'n/a')}")
        else:
            try:
                detail = response.json().get("detail", "Request failed.")
            except Exception:
                detail = "Request failed."
            st.warning(detail)
    except requests.Timeout:
    	st.error("The request timed out. The backend or AI model took too long to respond.")
    except requests.ConnectionError:
    	st.error("Cannot reach the backend. Check that FastAPI is running at " + API_URL)
    except requests.RequestException as e:
    	st.error(f"Request failed: {e}")

with st.expander("Revenue calculation and data policy"):
    st.markdown("""
    - Net revenue = quantity × unit price − discount amount.
    - Only transactions marked **Completed** are included.
    - Rows with a missing/invalid unit price or quantity less than or equal to zero are excluded from analytics.
    - Returned transactions are excluded.
    - Desk rows with a unit price of zero remain eligible under the current rule; this is a dataset ambiguity worth reviewing with the business owner.
    - The interface displays supporting figures so answers can be checked.
    """)
