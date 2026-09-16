import re
import streamlit as st
from agent import run_agent


# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="Financial Decision Agent",
    page_icon="💰",
    layout="centered",
)


# -----------------------------
# CUSTOM STYLING
# -----------------------------
st.markdown(
    """
    <style>
        .main-title {
            font-size: 2.6rem;
            font-weight: 800;
            margin-bottom: 0.2rem;
        }

        .subtitle {
            font-size: 1.05rem;
            opacity: 0.75;
            margin-bottom: 1.5rem;
        }

        .decision-card {
            padding: 1.4rem;
            border-radius: 16px;
            border: 1px solid rgba(128,128,128,0.25);
            margin: 1rem 0;
        }

        .decision-label {
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            opacity: 0.7;
        }

        .decision-value {
            font-size: 2rem;
            font-weight: 800;
            margin-top: 0.3rem;
        }

        .info-card {
            padding: 1rem;
            border-radius: 12px;
            border: 1px solid rgba(128,128,128,0.2);
            margin-bottom: 0.8rem;
        }

        .small-note {
            font-size: 0.85rem;
            opacity: 0.65;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# -----------------------------
# HELPER FUNCTIONS
# -----------------------------
def extract_amount(text, label):
    """
    Extract an amount only from the exact structured summary line.
    This prevents numbers from the agent's explanation being mistaken
    for financial values.
    """
    pattern = rf"(?im)^\s*{re.escape(label)}\s*:\s*₹?\s*([\d,]+(?:\.\d+)?)\s*$"

    matches = re.findall(pattern, text)

    if not matches:
        return None

    try:
        return float(matches[-1].replace(",", ""))
    except ValueError:
        return None


def extract_decision(text):
    """
    Extract the decision only from the exact structured summary line.
    """
    matches = re.findall(
        r"(?im)^\s*Decision:\s*(CAN_AFFORD|TIGHT_LOW_BUFFER|CANNOT_AFFORD)\s*$",
        text,
    )

    if not matches:
        return None

    return matches[-1].upper()

def format_inr(value):
    if value is None:
        return "—"

    return f"₹{value:,.0f}"


# -----------------------------
# HEADER
# -----------------------------
st.markdown(
    '<div class="main-title">💰 Financial Decision Agent</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">'
    "AI-powered financial decision support using Gemini + Python tools"
    "</div>",
    unsafe_allow_html=True,
)

st.divider()


# -----------------------------
# INPUT SECTION
# -----------------------------
st.subheader("📝 Describe your financial situation")

st.markdown(
    "Tell the agent about your income, expenses, commitments, and the "
    "purchase or financial commitment you want to evaluate."
)

user_request = st.text_area(
    "Financial situation",
    key="user_request",
    placeholder=(
        "Example:\n"
        "I earn ₹50,000 per month, spend ₹20,000 on essentials, "
        "have ₹5,000 in existing monthly commitments, "
        "and want to buy a laptop for ₹10,000."
    ),
    height=160,
    label_visibility="collapsed",
)


# -----------------------------
# QUICK EXAMPLE
# -----------------------------
st.markdown(
    '<div class="small-note">'
    "💡 Tip: Include monthly income, essential expenses, existing commitments, "
    "and the purchase price for the most complete evaluation."
    "</div>",
    unsafe_allow_html=True,
)

st.write("")

evaluate_clicked = st.button(
    "🔍 Evaluate Financial Decision",
    type="primary",
    use_container_width=True,
)


# -----------------------------
# RUN AGENT
# -----------------------------
if evaluate_clicked:

    if not user_request.strip():
        st.warning("Please describe your financial situation first.")

    else:
        with st.spinner("🤖 Agent is analyzing your financial situation..."):

            try:
                response = run_agent(user_request)

            except Exception as error:
                st.error(
                    "⚠️ The AI agent encountered an error while processing "
                    "your request."
                )
                st.caption(str(error))
                response = None

        if response:

            # Save response so it remains visible after Streamlit reruns
            st.session_state["agent_response"] = response


# -----------------------------
# RESULTS
# -----------------------------
if "agent_response" in st.session_state:

    response = st.session_state["agent_response"]

    st.divider()

    st.subheader("🤖 Agent Decision")

    decision = extract_decision(response)

    # -------------------------
    # DECISION CARD
    # -------------------------
    if decision:

        if decision == "CAN_AFFORD":
            decision_icon = "✅"
            decision_text = "CAN AFFORD"

        elif decision == "TIGHT_LOW_BUFFER":
            decision_icon = "⚠️"
            decision_text = "TIGHT / LOW BUFFER"

        else:
            decision_icon = "🛑"
            decision_text = "CANNOT AFFORD"

        st.markdown(
            f"""
            <div class="decision-card">
                <div class="decision-label">Agent recommendation</div>
                <div class="decision-value">
                    {decision_icon} {decision_text}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


    # -------------------------
    # FINANCIAL METRICS
    # -------------------------
    income = extract_amount(response, "Monthly Income")
    essentials = extract_amount(response, "Essential Expenses")
    commitments = extract_amount(
        response,
        "Existing Monthly Commitments",
    )
    remaining = extract_amount(response, "Remaining Money")
    safety_buffer = extract_amount(response, "Safety Buffer")
    remaining_after = extract_amount(
        response,
        "Remaining after purchase",
    )

    if any(
        value is not None
        for value in [
            income,
            essentials,
            commitments,
            remaining,
            safety_buffer,
            remaining_after,
        ]
    ):

        st.subheader("📊 Financial Breakdown")

        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "Monthly Income",
                format_inr(income),
            )

            st.metric(
                "Essential Expenses",
                format_inr(essentials),
            )

            st.metric(
                "Existing Commitments",
                format_inr(commitments),
            )

        with col2:
            st.metric(
                "Remaining Money",
                format_inr(remaining),
            )

            st.metric(
                "Safety Buffer",
                format_inr(safety_buffer),
            )

            st.metric(
                "After Purchase",
                format_inr(remaining_after),
            )


    # -------------------------
    # FULL EXPLANATION
    # -------------------------
    st.subheader("💬 Agent Explanation")

    st.markdown(response)


    # -------------------------
    # HOW IT WORKS
    # -------------------------
    st.divider()

    with st.expander("⚙️ How this AI Agent works", expanded=False):

        st.markdown(
            """
            **1. User provides a financial situation**

            The user describes their income, expenses, commitments,
            and intended purchase in natural language.

            **2. Gemini interprets the request**

            Gemini acts as the agent's reasoning and orchestration layer.

            **3. The agent calls Python tools**

            The agent can call specialized tools for:

            - Financial information extraction
            - Input validation
            - Financial position calculation
            - Safety-buffer calculation
            - Commitment evaluation

            **4. Python performs deterministic calculations**

            Important financial calculations are handled by Python
            rather than being left to the language model.

            **5. The agent explains the result**

            Gemini uses the tool results to produce an understandable
            decision and explanation.
            """
        )


# -----------------------------
# FOOTER
# -----------------------------
st.divider()

st.caption(
    "Prototype decision-support tool • Not professional financial advice"
)