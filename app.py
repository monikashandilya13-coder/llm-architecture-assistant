import streamlit as st
import os
from pathlib import Path
from datetime import date

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

# --- Streamlit Page Config ---
st.set_page_config(page_title="LLM-Driven ADR Assistant", layout="wide")
st.title("🧩 LLM-Driven Architecture Decision Assistant")

# --- Load synthetic inputs ---
seed_dir = Path("seed")
nfrs = (seed_dir / "NFRs.md").read_text()
context = (seed_dir / "Current-Context.md").read_text()

# --- Decision Question ---
decision = st.text_input("Decision question", "Oracle → PostgreSQL migration options")

# --- Mode Selector ---
mode = st.radio("Choose Mode", ["Mock Mode", "Real API Mode"])

# --- API Key (only needed for real mode) ---
api_key = ""
if mode == "Real API Mode":
    api_key = st.text_input("🔑 Enter your OpenAI API key", type="password")
    if api_key and OpenAI:
        os.environ["OPENAI_API_KEY"] = api_key
        client = OpenAI()

# --- Mock ADR content ---
MOCK_ADR = f"""
# ADR-001: Oracle → PostgreSQL Migration

**Status:** Proposed  
**Date:** {date.today()}  

## Context
{nfrs}

{context}

## Options
1. **Amazon Aurora PostgreSQL (managed)**
   - ✅ Pros: Managed service, auto-scaling, built-in HA
   - ❌ Cons: Vendor lock-in, cost
   - ⚠️ Risks: Migration complexity, skill gap

2. **Self-managed PostgreSQL on VMs**
   - ✅ Pros: Full control, cheaper infra
   - ❌ Cons: Ops overhead, patching
   - ⚠️ Risks: Reliability, SRE burden

3. **PostgreSQL on Kubernetes**
   - ✅ Pros: Portable, modern
   - ❌ Cons: Complexity, steep learning curve
   - ⚠️ Risks: Cluster reliability, DR gaps

## Trade-off Matrix
| Option                        | Cost 💰 | Complexity ⚙️ | Speed 🚀 | Reliability 🔒 |
|-------------------------------|---------|---------------|----------|----------------|
| Aurora PostgreSQL (Managed)   | 3/5     | 2/5           | 4/5      | 5/5            |
| Self-managed PostgreSQL (VMs) | 4/5     | 4/5           | 3/5      | 3/5            |
| PostgreSQL on Kubernetes      | 5/5     | 5/5           | 2/5      | 4/5            |

*(Scores: 1 = poor, 5 = excellent)*

## Decision
Choose **Aurora PostgreSQL** because it balances availability, scaling, and reduced ops overhead.  
Team prefers managed service given limited bandwidth.

## Consequences
+ Reduced ops burden  
+ Predictable scaling  
- Vendor lock-in  
- Higher monthly spend  

## Architecture (Mermaid)
```mermaid
flowchart TD
    A[Legacy Oracle DB] -->|Migration| B[Aurora PostgreSQL]
    B --> C[Order Service API]
    C --> D[Partner Systems]
```

## Rollout & Rollback
- Rollout: Dual-write, migrate in phases, cutover at low traffic
- Rollback: Re-point apps to Oracle, replay recent logs

## Fitness Functions
- P95 latency < 250 ms
- Monthly infra cost < $9k
- Backup restore drill passes RTO=2h, RPO=15 min
- Zero data loss during migration

## Review
- Review date: {date.today().replace(year=date.today().year+1)}
"""

# --- Generate ADR ---
if st.button("⚡ Generate ADR"):
    if mode == "Mock Mode":
        st.subheader("📑 Draft ADR (Mock Data)")
        st.markdown(MOCK_ADR)
        output = MOCK_ADR
    elif mode == "Real API Mode" and api_key:
        prompt = f"""
        You are an Architecture Copilot.
        Context:

        {nfrs}

        {context}

        Task:
        1. Propose exactly 3 database migration options for replacing Oracle.
           For each: Pros, Cons, Risks, and 2 proof-points to de-risk.
        2. Provide a trade-off matrix (Cost, Complexity, Speed, Reliability).
        3. Draft an ADR in Markdown with: Title, Status, Date, Context, Options, Decision,
           Consequences, Architecture diagram (Mermaid), Rollout & Rollback, Fitness Functions, Review date.
        """
        with st.spinner("Calling GPT model..."):
            resp = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.4
            )
            output = resp.choices[0].message.content
            st.subheader("📑 Draft ADR (Real LLM Output)")
            st.markdown(output)
    else:
        st.warning("⚠️ Please provide an API key for Real API Mode.")
        output = ""

    if output:
        out_dir = Path("out")
        out_dir.mkdir(exist_ok=True)
        adr_path = out_dir / "ADR-001.md"
        adr_path.write_text(output)

        st.download_button(
            label="💾 Download ADR (Markdown)",
            data=output,
            file_name="ADR-001.md",
            mime="text/markdown"
        )
