import streamlit as st
import os
from pathlib import Path
from datetime import date
from jinja2 import Template

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

# --- Streamlit Page Config ---
st.set_page_config(page_title="LLM-Driven ADR Assistant", layout="wide")
st.title("🧩 LLM-Driven Architecture Decision Assistant (Dynamic Version)")

# --- Paths ---
templates_dir = Path("templates")
out_dir = Path("out")
out_dir.mkdir(exist_ok=True)

# --- Input Form for NFRs & Context ---
with st.form("nfr_form"):
    st.subheader("📥 Enter Context & NFRs")
    availability = st.text_input("Availability", "99.9%")
    latency = st.text_input("Latency", "P95 ≤ 250 ms")
    cost_cap = st.text_input("Cost Cap", "$9k/month")
    context_text = st.text_area("System Context", "Legacy: Monolith on Oracle DB, SOAP APIs...")
    review_date = st.date_input("Review Date", date.today().replace(year=date.today().year + 1))

    submitted = st.form_submit_button("Save Inputs")

if submitted:
    st.success("Inputs captured successfully.")

# --- Mode Selector ---
mode = st.radio("Choose Mode", ["Mock Mode", "Real API Mode"])

# --- Trade-offs ---
tradeoffs = st.multiselect(
    "Which trade-off dimensions matter most?",
    ["Cost", "Complexity", "Speed", "Reliability", "Security", "Skill Fit"],
    default=["Cost", "Reliability"]
)

# --- API Key (only needed for real mode) ---
api_key = ""
if mode == "Real API Mode":
    api_key = st.text_input("🔑 Enter your OpenAI API key", type="password")
    if api_key and OpenAI:
        os.environ["OPENAI_API_KEY"] = api_key
        client = OpenAI()

# --- Generate ADR ---
if st.button("⚡ Generate ADR"):
    nfrs = f"- Availability: {availability}\n- Latency: {latency}\n- Cost Cap: {cost_cap}"

    if mode == "Mock Mode":
        template = Template(open(templates_dir / "db_migration_mock.md").read())
        adr_output = template.render(
            decision_title="Oracle → PostgreSQL Migration",
            date=date.today(),
            nfrs=nfrs,
            context=context_text,
            tradeoffs=tradeoffs,
            review_date=review_date
        )
        st.subheader("📑 Draft ADR (Mock Data)")
        st.markdown(adr_output)
    elif mode == "Real API Mode" and api_key:
        prompt = f"""
        You are an Architecture Copilot.
        Context:
        {nfrs}
        {context_text}

        Task:
        1. Propose 3 options for Oracle migration.
        2. Provide a trade-off matrix for {', '.join(tradeoffs)}.
        3. Draft an ADR in Markdown.
        """
        with st.spinner("Calling GPT model..."):
            resp = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.4
            )
            adr_output = resp.choices[0].message.content
            st.subheader("📑 Draft ADR (Real LLM Output)")
            st.markdown(adr_output)
    else:
        st.warning("⚠️ Please provide an API key for Real API Mode.")
        adr_output = ""

    # Save ADR
    if adr_output:
        adr_path = out_dir / f"ADR-{date.today()}.md"
        adr_path.write_text(adr_output)
        st.download_button(
            label="💾 Download ADR (Markdown)",
            data=adr_output,
            file_name=adr_path.name,
            mime="text/markdown"
        )

# --- ADR Registry ---
st.subheader("📂 Past ADRs")
for file in sorted(out_dir.glob("ADR-*.md")):
    st.markdown(f"- [📄 {file.name}]({file})")
