import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Healthcare AI Platform",
    page_icon="🏥",
    layout="wide"
)

st.title("🏥 Healthcare AI Platform")
st.caption("Healthcare data engineering + AI platform")

st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Go to",
    [
        "🏠 Dashboard",
        "🔎 Clinical Search",
        "👤 Patient Explorer",
        "🤖 AI Assistant"
    ]
)

# -----------------------------
# Dashboard
# -----------------------------

if page == "🏠 Dashboard":

    st.header("Healthcare Data Dashboard")

    try:
        response = requests.get(f"{API_URL}/analytics")

        if response.status_code == 200:

            data = response.json()

            col1, col2, col3, col4 = st.columns(4)

            col1.metric(
                "Patients",
                data.get("total_patients", 0)
            )

            col2.metric(
                "Claims",
                data.get("total_claims", 0)
            )

            col3.metric(
                "Clinical Notes",
                data.get("total_clinical_notes", 0)
            )

            col4.metric(
                "Total Charges",
                f"${data.get('total_charges', 0.0):,.2f}"
            )

            st.divider()

            st.subheader("Claim Status")

            # FIX: Extract claim_statuses from data payload
            claim_statuses = data.get("claim_statuses", {})

            if claim_statuses:
                chart_data = {
                    "Status": list(claim_statuses.keys()),
                    "Claims": list(claim_statuses.values())
                }

                st.bar_chart(
                    chart_data,
                    x="Status",
                    y="Claims"
                )
            else:
                st.info("No claim status data available.")

        else:
            st.error("Unable to retrieve analytics.")

    except requests.exceptions.ConnectionError:
        st.error("FastAPI server is not running.")


# -----------------------------
# Clinical Search
# -----------------------------

elif page == "🔎 Clinical Search":

    st.header("Clinical Note Search")

    query = st.text_input(
        "Search clinical documentation",
        placeholder="Example: diabetes"
    )

    if st.button("Search"):

        if query:

            response = requests.post(
                f"{API_URL}/search",
                json={"query": query}
            )

            if response.status_code == 200:

                data = response.json()

                st.write(
                    f"Found **{data['match_count']}** matching notes."
                )

                for note in data["matches"]:

                    with st.expander(
                        f"{note['note_id']} — Patient {note['patient_id']}"
                    ):

                        st.write(
                            f"**Note Type:** {note['note_type']}"
                        )

                        st.write(
                            f"**Clinical Documentation:** {note['note_text']}"
                        )

            else:
                st.warning("No matching clinical documentation found.")

        else:
            st.warning("Enter a search term.")


# -----------------------------
# AI Assistant
# -----------------------------

elif page == "🤖 AI Assistant":

    st.header("Clinical AI Assistant")

    question = st.text_input(
        "Ask a clinical question",
        placeholder="Which patient has documented elevated blood glucose?"
    )

    if st.button("Ask Healthcare AI"):

        if question:

            with st.spinner("Analyzing clinical documentation..."):

                response = requests.post(
                    f"{API_URL}/ask",
                    json={"question": question}
                )

            if response.status_code == 200:

                result = response.json()

                # Handle SAFE_RESPONSE output from clinical validator
                if result.get("status") == "SAFE_RESPONSE":
                    st.warning(result.get("message"))
                else:
                    st.subheader("AI Response")

                    col1, col2 = st.columns(2)

                    col1.metric(
                        "Patient ID",
                        result.get("patient_id", "N/A")
                    )

                    col2.metric(
                        "Note ID",
                        result.get("note_id", "N/A")
                    )

                    st.info(
                        f"**Evidence:** {result.get('evidence', 'N/A')}"
                    )

            else:
                st.warning(
                    "No clinical evidence found."
                )

        else:
            st.warning("Enter a clinical question.")
