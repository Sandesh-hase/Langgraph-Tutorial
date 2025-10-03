import streamlit as st
import pandas as pd
from main import process_claims
import io

# Page config
st.set_page_config(page_title="AaiTech Warranty Fraud Detector", layout="wide")


# --- Styles and header ---
st.markdown(
        """
        <style>
        /* Page background: mostly white with a very light blue tint for light-mode friendliness */
        .stApp {
            background: linear-gradient(180deg, #ffffff 0%, #fbfdff 40%, #f5fbff 100%);
            background-attachment: fixed;
            color: #0b1220; /* darker text for readability in light mode */
        }
        .header {
                background: linear-gradient(90deg, rgba(14,165,167,0.12) 0%, rgba(15,23,42,0.06) 100%);
                padding: 24px 18px;
                border-radius: 10px;
                color: #071127;
                text-align: center;
                box-shadow: 0 6px 18px rgba(2,6,23,0.06);
                margin-bottom: 12px;
                border: 1px solid rgba(10,25,47,0.04);
        }
        .subtle-box { background: rgba(10,20,34,0.02); padding:12px; border-radius:8px }
        .small { font-size:13px; color:#475569 }

        /* Style Streamlit buttons to be more prominent */
        .stButton>button {
                background: linear-gradient(90deg,#06b6d4,#7c3aed);
                color: white;
                border: none;
                padding: 10px 18px;
                font-weight: 600;
                border-radius: 8px;
                box-shadow: 0 6px 14px rgba(124,58,237,0.12);
        }
        .stButton>button:hover { filter: brightness(1.03) }

        /* KPI card styling */
        .kpi-card { padding: 14px; border-radius: 8px; color: white; text-align: center }
        .kpi-approve { background: linear-gradient(90deg,#16a34a,#60a5fa) }
        .kpi-reject { background: linear-gradient(90deg,#ef4444,#fb923c) }
        .kpi-escalate { background: linear-gradient(90deg,#f59e0b,#f97316) }
        /* Total KPI: light background with dark text so it stands out on the page background */
        .kpi-total { background: linear-gradient(90deg,#e6f7ff,#eef2ff); color: #071127; box-shadow: 0 4px 10px rgba(2,6,23,0.04); border: 1px solid rgba(10,25,47,0.04) }
        </style>
        <div class="header">
            <h1 style="margin:0">AaiTech Warranty Fraud Detector</h1>
            <div class="small">Upload warranty claims, run the detector, review results and export.</div>
        </div>
        """,
        unsafe_allow_html=True,
)

st.write("")

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("## Upload claims CSV")
    uploaded_file = st.file_uploader("Choose a CSV file with warranty claims", type=["csv"])
    st.markdown("<div class='small'>Expected: one claim per row. The app will add policy_check, fraud_score, evidence, and decision columns.</div>", unsafe_allow_html=True)

with col2:
    st.markdown("## Actions")
    # Generate button (styled via global CSS above)
    generate_button = st.button("Generate Results", key="generate", use_container_width=True)

results_df = None
uploaded_df = None

# restore previous results (so widgets that cause reruns keep showing the data)
if 'results_df' in st.session_state:
    results_df = st.session_state['results_df']

if uploaded_file is not None:
    try:
        uploaded_df = pd.read_csv(uploaded_file)
    except Exception as e:
        st.error(f"Could not read CSV: {e}")

    if uploaded_df is not None:
        st.markdown("### Preview uploaded data")
        st.dataframe(uploaded_df.head(10))

        # only run when user presses generate
        if generate_button:
            # progress UI
            placeholder = st.empty()
            progress_bar = st.progress(0)
            status_text = st.empty()

            def progress_cb(current, total):
                pct = int(current / total * 100)
                progress_bar.progress(pct)
                status_text.info(f"Processing {current}/{total}")

            with st.spinner("Analyzing claims — this may take a few moments..."):
                results_df = process_claims(uploaded_df, progress_callback=progress_cb)

            # persist results so subsequent widget interactions (selectbox, expanders) survive reruns
            st.session_state['results_df'] = results_df

            progress_bar.progress(100)
            status_text.success("Processing complete")

        else:
            st.info("Upload a file and press 'Generate Results' to start processing.")

else:
    st.info("Please upload a CSV file to get started.")

# If we have results from a previous run (stored in session_state), render them here so
# widget interactions (like selecting a row) don't cause the app to fall back to the upload prompt.
if results_df is not None:
    # show summary KPIs (styled cards)
    st.markdown("## Results summary")
    if not results_df.empty:
        total = len(results_df)
        approves = int((results_df['decision'] == 'Approve claim').sum())
        rejects = int((results_df['decision'] == 'Reject claim').sum())
        escalates = int((results_df['decision'] == 'Escalate to HITL').sum())

        k1, k2, k3, k4 = st.columns([1,1,1,2])
        k1.markdown(f"<div class='kpi-card kpi-total'><strong>Total</strong><div style='font-size:28px'>{total}</div></div>", unsafe_allow_html=True)
        k2.markdown(f"<div class='kpi-card kpi-approve'><strong>Approved</strong><div style='font-size:28px'>{approves}</div></div>", unsafe_allow_html=True)
        k3.markdown(f"<div class='kpi-card kpi-reject'><strong>Rejected</strong><div style='font-size:28px'>{rejects}</div></div>", unsafe_allow_html=True)
        k4.markdown(f"<div class='kpi-card kpi-escalate'><strong>Escalated</strong><div style='font-size:28px'>{escalates}</div><div class='small'>Claims flagged for manual review</div></div>", unsafe_allow_html=True)

    # styled results table
    st.markdown("### Detailed Results")

    def style_decision(val):
        if val == 'Approve claim':
            return 'background-color: #d1fae5; color: #065f46'
        if val == 'Reject claim':
            return 'background-color: #fee2e2; color: #7f1d1d'
        if val == 'Escalate to HITL':
            return 'background-color: #fff7ed; color: #92400e'
        return ''

    styled = results_df.style.applymap(style_decision, subset=['decision'])
    st.dataframe(styled, use_container_width=True)

    # enable download with actual data
    csv_bytes = results_df.to_csv(index=False).encode('utf-8')
    st.download_button("Download Results as CSV", data=csv_bytes, file_name="processed_claims.csv", mime="text/csv")

    # Agent conversation trace viewer
    st.markdown("---")
    st.markdown("### Agent conversation trace")
    sel_idx = st.selectbox(
        "Select a claim to inspect the agent conversation",
        options=list(range(len(results_df))),
        format_func=lambda i: f"Row {i} - {results_df.index[i]}",
    )

    trace = results_df.iloc[sel_idx].get('agent_trace', [])

    if not trace:
        st.info("No agent trace available for this claim.")
    else:
        for step in trace:
            agent = step.get('agent')
            prompt = step.get('prompt', '')
            response = step.get('response', '')
            with st.expander(f"{agent}"):
                st.markdown("**Prompt**")
                st.code(prompt, language='')
                st.markdown("**Response**")
                st.code(response, language='')