# LLM-Driven Architecture Decision Assistant

A **Streamlit-based AI assistant** that generates **Architecture Decision Records (ADRs)**  
from system context + NFRs.

## 🚀 Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## 🌐 Run online
- **Replit**: import this repo → `streamlit run app.py`
- **GitHub Codespaces**: open in Codespace → run Streamlit
- **Streamlit Cloud**: deploy directly from this GitHub repo

### Features
- Mock Mode (no API key needed) with pre-baked ADR + trade-off matrix
- Real API Mode (requires OpenAI API key) for live ADR generation
