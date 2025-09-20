
import streamlit as st
import os
from pathlib import Path
from datetime import date, datetime
from jinja2 import Template

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

# --- Streamlit Page Config ---
st.set_page_config(page_title="LLM-Driven ADR Assistant", layout="wide")
st.title("🧩 LLM-Driven Architecture Decision Assistant")

# --- Paths ---
out_dir = Path("out")
out_dir.mkdir(exist_ok=True)

# =============================
# 📥 INPUTS
# =============================
with st.form("inputs_form"):
    st.subheader("Context & NFRs for Digital Transformation")

    # NFRs
    col1, col2, col3 = st.columns(3)
    with col1:
        availability = st.text_input("Availability", "99.9%")
    with col2:
        latency = st.text_input("Latency target", "P95 ≤ 250 ms")
    with col3:
        cost_cap = st.text_input("Monthly Cost Cap", "$9k/month")

    review_date = st.date_input("Review Date", date.today().replace(year=date.today().year + 1))

    st.markdown("### Transformation Context")

    # Application Transformation
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
        index=0,
    )

    # Database Transformation
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
        index=0,
    )

    # Infrastructure Transformation
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
        index=0,
    )

    # Trade-off dimensions
    tradeoffs = st.multiselect(
        "Trade-off dimensions to evaluate",
        ["Cost", "Complexity", "Speed", "Reliability", "Security", "Operability", "Skill Fit", "Vendor Risk"],
        default=["Cost", "Reliability", "Operability"],
    )

    submitted = st.form_submit_button("Save Inputs")

if submitted:
    st.success("Inputs captured.")

# Build NFRs and context text
nfrs_text = f"""- Availability: {availability}
- Latency: {latency}
- Cost Cap: {cost_cap}"""

context_text = f"""### Application Transformation
{app_context}

### Database Transformation
{db_context}

### Infrastructure Transformation
{infra_context}"""

# =============================
# ⚙️ MODE TOGGLE
# =============================
mode = st.radio("Mode", ["Mock Mode", "Real API Mode"], horizontal=True)

api_key = ""
client = None
if mode == "Real API Mode":
    api_key = st.secrets.get("gsk_2025", "")
    if api_key and OpenAI:        
        client = OpenAI(api_key=api_key)

# =============================
# 🧠 MOCK TEMPLATE
# =============================
MOCK_TEMPLATE = Template(
    """# ADR-{{ adr_id }}: Digital Transformation Decision (App · DB · Infra)

**Status:** Proposed  
**Date:** {{ today }}  

## Context
{{ nfrs }}

{{ context }}

## Options
1. **Modernize Application First (Strangler + Modular Monolith)**
   - ✅ Pros: Reduces coupling risk; incremental value delivery; lower blast radius
   - ❌ Cons: Longer runway to full benefits; interim complexity
   - ⚠️ Risks: Incomplete strangling; shared DB hotspots

2. **Database First (Replatform to Managed PostgreSQL + Data Contracts)**
   - ✅ Pros: Cuts license cost; improves availability & backup/restore; platform stability
   - ❌ Cons: App changes required; PL/SQL migration complexity
   - ⚠️ Risks: Data integrity during cutover; performance regressions

3. **Infra First (Containerize on Kubernetes + GitOps)**
   - ✅ Pros: Standardized ops; scalability; path to cloud-native
   - ❌ Cons: Doesn't fix app/db design issues; cluster ops skill gap
   - ⚠️ Risks: Misconfigured clusters; cost overruns without autoscaling

## Trade-off Matrix
| Option                                      | {% for d in tradeoffs %}{{ d }} | {% endfor %}
|---------------------------------------------|{% for d in tradeoffs %}---------|{% endfor %}
| App First (Strangler + Modular Monolith)    | {% for d in tradeoffs %}4/5     |{% endfor %}
| DB First (Managed PostgreSQL + Contracts)   | {% for d in tradeoffs %}4/5     |{% endfor %}
| Infra First (Kubernetes + GitOps)           | {% for d in tradeoffs %}3/5     |{% endfor %}

*(Scores: 1 = poor, 5 = excellent — illustrative only for mock)*

## Decision
Start with **Database First** if licensing/cost pressure is immediate **or** RTO/RPO is the top priority.  
Start with **Application First** if coupling/velocity is the primary bottleneck.  
Infra-first suits orgs with strong platform teams and low app churn.

## Architecture (Mermaid)
```mermaid
flowchart TD
    subgraph Legacy
      A[Monolith App] --> B[(RDBMS)]
      A --> C[Batch Jobs]
    end

    subgraph Target
      D[Modular Services]
      E[(Managed Postgres)]
      F[Kubernetes Platform]
      D --> E
      D -->|Async Events| G[(Kafka)]
    end

    A -->|Strangler| D
    B -->|Data Migration| E
    C --> F
```

## Rollout & Rollback
- **Rollout:** Identify seams → modularize → dual-write → phased cutover → decommission legacy components.
- **Rollback:** Traffic switchback; restore from latest snapshot; replay messages; freeze toggles.

## Fitness Functions
- P95 latency < {{ latency }}
- Monthly infra cost < {{ cost_cap }}
- Error budget burn rate within SLOs
- Backup restore drill passes; RTO/RPO targets met

## Review
- Review date: {{ review_date }}
"""
)

# =============================
# 🚀 GENERATE ADR
# =============================
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
        st.subheader("📑 Draft ADR (Mock)")
        st.markdown(adr_output)
    elif mode == "Real API Mode" and client:
        prompt = f"""You are the Architecture Copilot.
Context:
{nfrs_text}

{context_text}

Decision space: Application, Database, and Infrastructure Transformation.

Tasks:
1) Propose 3 coherent transformation paths (App-first, DB-first, Infra-first). For each include: pros, cons, risks.
2) Provide a trade-off matrix over: {', '.join(tradeoffs)} with 1–5 scores and short justifications.
3) Draft an ADR in Markdown with: Title, Status, Date, Context, Options, Decision (and when to choose each), Mermaid diagram, Rollout & Rollback, Fitness Functions, Review date.
Keep it under ~700 words.
"""
        with st.spinner("Calling GPT model..."):
            resp = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.4,
            )
            adr_output = resp.choices[0].message.content
            st.subheader("📑 Draft ADR (Real LLM Output)")
            st.markdown(adr_output)
    else:
        st.warning("Provide an API key or use Mock Mode.")

    # Save & download
    if adr_output:
        fname = f"ADR-{adr_id}.md"
        adr_path = out_dir / fname
        adr_path.write_text(adr_output)
        st.download_button(
            "💾 Download ADR (Markdown)",
            data=adr_output,
            file_name=fname,
            mime="text/markdown",
        )

# =============================
# 📚 ADR REGISTRY
# =============================
st.subheader("📂 Past ADRs")
files = sorted(out_dir.glob("ADR-*.md"), reverse=True)
if not files:
    st.info("No ADRs yet. Generate one to see it here.")
for file in files:
    with st.expander(f"📄 {file.name}"):
        content = file.read_text()
        st.markdown(content)
        st.download_button(
            label=f"💾 Download {file.name}",
            data=content,
            file_name=file.name,
            mime="text/markdown",
        )
