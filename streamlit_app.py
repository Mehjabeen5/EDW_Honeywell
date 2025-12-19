import streamlit as st

from app.analytics import fetch_views
from app.routing import classify_question
from app.planning import plan_steps
from app.reasoning import simple_answer, reasoning_answer

st.set_page_config(page_title="EDW-2 Reasoning Assistant", layout="wide")
st.title("EDW-2 Reasoning Assistant (Snowflake Native)")

question = st.text_input("Ask a business question (e.g., 'Why was revenue down last quarter?')")
run = st.button("Run Analysis")

if run and question:
    route = classify_question(question)
    st.subheader("Step 1 — Routing")
    st.markdown(f"**Route:** `{route}`")

    st.subheader("Step 2 — Snowflake Analytics")
    rev, reg, prod = fetch_views()
    st.success("Analytics successfully generated from Snowflake.")

    with st.expander("Preview: Revenue by Quarter"):
        st.dataframe(rev)
    with st.expander("Preview: Revenue by Region"):
        st.dataframe(reg)
    with st.expander("Preview: Revenue by Product"):
        st.dataframe(prod)

    if route == "simple":
        st.markdown("_Simple question detected: using direct analytics with no explicit planning._")
        st.subheader("Step 3 — Direct AI Answer")
        final_answer = simple_answer(question, rev, reg, prod)

        st.subheader("Final AI Explanation")
        st.markdown(
            f"""<div style="background-color:#ecf7ee;padding:20px;border-radius:8px;font-size:16px;line-height:1.6;">
{final_answer}
</div>""",
            unsafe_allow_html=True,
        )
    else:
        st.markdown("_Reasoning question detected: using planning + multi-step reasoning._")

        st.subheader("Step 3 — Planning")
        plan = plan_steps(question)
        steps = plan.get("steps", [])
        subqs = plan.get("sub_questions", [])

        if steps:
            st.markdown("**Planned Steps:**")
            for s in steps:
                st.markdown(
                    f"- `{s.get('id', '')}` "
                    f"[{s.get('dimension', '')}] – {s.get('description', '')}"
                )
        if subqs:
            with st.expander("Generated Sub-Questions"):
                for sq in subqs:
                    st.markdown(
                        f"- **{sq.get('id', '')}** "
                        f"(_{sq.get('dimension', '')}_): {sq.get('question', '')} "
                        f"— _{sq.get('focus', '')}_"
                    )

        st.subheader("Step 4 — AI Reasoning (Cortex)")
        final_answer = reasoning_answer(question, plan, rev, reg, prod)

        st.subheader("Final AI Explanation")
        st.markdown(
            f"""<div style="background-color:#ecf7ee;padding:20px;border-radius:8px;font-size:16px;line-height:1.6;">
{final_answer}
</div>""" ,
            unsafe_allow_html=True,
        )
