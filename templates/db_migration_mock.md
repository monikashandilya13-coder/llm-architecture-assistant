# ADR-001: {{ decision_title }}

**Status:** Proposed  
**Date:** {{ date }}  

## Context
{{ nfrs }}

{{ context }}

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
| Option                        | {% for d in tradeoffs %}{{ d }} | {% endfor %}
|-------------------------------|{% for d in tradeoffs %}---------|{% endfor %}
| Aurora PostgreSQL (Managed)   | {% for d in tradeoffs %}4/5     |{% endfor %}
| Self-managed PostgreSQL (VMs) | {% for d in tradeoffs %}3/5     |{% endfor %}
| PostgreSQL on Kubernetes      | {% for d in tradeoffs %}2/5     |{% endfor %}

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
- Review date: {{ review_date }}
