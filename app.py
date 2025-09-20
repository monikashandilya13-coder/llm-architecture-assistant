import streamlit as st
import os
from pathlib import Path
from datetime import date, datetime
from jinja2 import Template

# Groq client (fast Llama)
try:
    from groq import Groq
except ImportError:
    Groq = None

# ---------- Page ----------
st.set_page_config(page_title="LLM-Driven ADR Assistant", layout="wide")
st.title("LLM-Driven Architecture Decision Assistant (Groq-enabled)")

# ---------- Paths ----------
out_dir = Path("out")
out_dir.mkdir(exist_ok=True)

# ---------- Inputs (NFRs + Context) ----------
with st.form("inputs_form"):
    st.subheader("Context & NFRs for Digital Transformation")

    c1, c2, c3 = st.columns(3)
    with c1:
        availability = st.text_input("Availability", "99.9%")
    with c2:
        latency = st.text_input("Latency target", "P95 <= 250 ms")
    with c3:
        cost_cap = st.text_input("Monthly Cost Cap", "$9k/month")

    review_date = st.date_input(
        "Review Date",
        date.today().replace(year=date.today().year + 1),
    )

    st.markdown("### Transformation Context")

    app_context = st.selectbox(
        "Application Transformation",
        [
            "Legacy Monolith (Java EE, .NET, COBOL)",
            "SOA with ESB (point-to-point, SOAP/XML)",
            "Early Microservices (REST APIs, limited governance)",
            "Event-Driven Architecture (Kafka, RabbitMQ)",
            "Cloud-Native Microservices (12-Factor, CI/CD, containers)",
            "Serverless-First (Lambda/Functions, API Gateway)",
        ],
    )

    db_context = st.selectbox(
        "Database Transformation",
        [
            "Oracle / SQL Server on-prem (high licensing costs)",
            "Mainframe DB2 (batch-driven)",
            "Self-managed PostgreSQL / MySQL (on VMs)",
            "Managed Cloud DB (Aurora, Cloud SQL, CosmosDB)",
            "Distributed NoSQL (Cassandra, DynamoDB, MongoDB)",
            "Polyglot Persistence (mix of SQL + NoSQL + Streams)",
        ],
    )

    infra_context = st.selectbox(
        "Infrastructure Transformation",
        [
            "On-Prem Data Center (VMWare, bare metal)",
            "Private Cloud (OpenStack, Hyper-V)",
            "IaaS Lift-and-Shift (EC2, Azure VMs, GCP Compute)",
            "Containerized Workloads (Kubernetes, OpenShift)",
            "Hybrid Cloud (mix of on-prem + cloud workloads)",
            "Multi-Cloud Strategy (AWS + Azure + GCP)",
            "Serverless Infrastructure (FaaS + managed services)",
        ],
    )

    tradeoffs = st.multiselect(
        "Trade-off dimensions to evaluate",
        ["Cost", "Complexity", "Speed", "Reliability", "Security", "Operability", "Skill Fit", "Vendor Risk"],
        default=["Cost", "Reliability", "Operability"],
    )

    submitted = st.form_submit_button("Save Inputs")

if submitted:
    st.success("Inputs captured.")

nfrs_text = f"""- Availability: {availability}
- Latency: {latency}
- Cost Cap: {cost_cap}"""

context_text = f"""### Application Transformation
{app_context}

### Database Transformation
{db_context}

### Infrastructure Transformation
{infra_context}"""

# ---------- Mode ----------
mode = st.radio("Mode", ["Mock Mode", "Groq API"], horizontal=True)

# Read key in this order: Streamlit Secrets (gsk_2025) -> ENV (GROQ_API_KEY) -> Text box
api_key = ""
client = None
if mode == "Groq API":
  api_key = (
        st.secrets.get("gsk_2025", "")
        or os.getenv("GROQ_API_KEY", "")
        or st.text_input("Groq API Key", type="password")
    )
    if api_key and Groq:
        client = Groq(api_key=api_key)

# ---------- Mock template ----------
MOCK_TEMPLATE = Template(
    """# ADR-{{ adr_id }}: Digital Transformation Decision (App · DB · Infra)

**Status:** Proposed  
**Date:** {{ today }}  

## Context
{{ nfrs }}

{{ context }}

## Options
1. **Modernize Application First (Strangler + Modular Monolith)**
   - Pros: Reduces coupling; incremental value; lower blast radius
   - Cons: Longer runway; interim complexity
   - Risks: Incomplete strangling; shared DB hotspots

2. **Database First (Replatform to Managed PostgreSQL + Data Contracts)**
   - Pros: License cost reduction; availability; platform stability
   - Cons: App refactors; PL/SQL migration complexity
   - Risks: Cutover integrity; perf regressions

3. **Infra First (Containerize on Kubernetes + GitOps)**
   - Pros: Standardized ops; scalability; path to cloud-native
   - Cons: Does not fix app/db design; platform skill gap
   - Risks: Misconfig; cost overruns without autoscaling

## Trade-off Matrix
| Option  | {% for d in tradeoffs %}{{ d }} | {% endfor %}
|---------|{% for d in tradeoffs %}---------|{% endfor %}
| App     | {% for d in tradeoffs %}4/5     |{% endfor %}
| DB      | {% for d in tradeoffs %}4/5     |{% endfor %}
| Infra   | {% for d in tradeoffs %}3/5     |{% endfor %}

## Decision
Start DB-first if licensing/RTO pressure is highest.  
Start App-first if velocity/coupling is the bottleneck.  
Infra-first fits mature platform teams with low app churn.

## Mermaid Diagram
```mermaid
flowchart TD
  subgraph Legacy
    A[Monolith] --> B[(RDBMS)]
    A --> C[Batch Jobs]
  end
  subgraph Target
    D[Modular Services] --> E[(Managed Postgres)]
    D -->|Async| G[(Kafka)]
    F[Kubernetes Platform]
  end
  A -->|Strangler| D
  B -->|Data Migration| E
  C --> F
```

## Rollout & Rollback
- Rollout: seams -> modularize -> dual-write -> phased cutover -> decommission
- Rollback: switchback traffic; restore snapshot; replay messages

## Fitness Functions
- P95 latency < {{ latency }}
- Monthly infra cost < {{ cost_cap }}
- Error budget burn rate within SLOs
- Backup restore drill meets RTO/RPO

## Review
- Review date: {{ review_date }}
"""
)

# ---------- Generate ----------
if st.button("Generate ADR"):
    adr_output = ""
    adr_id = datetime.now().strftime("%Y%m%d-%H%M%S")

    if mode == "Mock Mode":
        adr_output = MOCK_TEMPLATE.render(
            adr_id=adr_id,
            today=date.today(),
            nfrs=nfrs_text,
            context=context_text,
            tradeoffs=tradeoffs,
            latency=latency,
            cost_cap=cost_cap,
            review_date=review_date,
        )
        st.subheader("Draft ADR (Mock)")
        st.markdown(adr_output)

    elif mode == "Groq API" and client:
        prompt = f"""
You are an Architecture Copilot.

Context:
{nfrs_text}

{context_text}

Evaluate three strategies (App-first, DB-first, Infra-first):
- Provide Pros, Cons, Risks for each
- Build a trade-off matrix for: {', '.join(tradeoffs)} (scores 1–5 with short justification)
- Output a complete ADR in Markdown with: Title, Status, Date, Context, Options, Decision, Mermaid diagram, Rollout & Rollback, Fitness Functions, Review date.
Keep it concise and actionable.
"""
        with st.spinner("Calling Groq (Llama 3)…"):
            resp = client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,max_tokens=900,
            )
            adr_output = resp.choices[0].message.content
            st.subheader("Draft ADR (Groq Output)")
            st.markdown(adr_output)

    else:
        st.warning("Provide a Groq API key or use Mock Mode.")

    if adr_output:
        fname = f"ADR-{adr_id}.md"
        (out_dir / fname).write_text(adr_output)
        st.download_button("Download ADR", adr_output, file_name=fname, mime="text/markdown")

# ---------- ADR Registry ----------
st.subheader("Past ADRs")
files = sorted(out_dir.glob("ADR-*.md"), reverse=True)
if not files:
    st.info("No ADRs yet. Generate one to see it here.")
for f in files:
    with st.expander(f"{f.name}"):
        content = f.read_text()
        st.markdown(content)
        st.download_button(f"Download {f.name}", content, f.name, mime="text/markdown")
