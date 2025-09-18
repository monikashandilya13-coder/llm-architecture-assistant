# 🧩 LLM-Driven Architecture Decision Assistant

[![Live App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://monikashandilya13-coder-llm-architecture-assistant.streamlit.app)  
[![Deploy to Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/deploy?repo=https://github.com/monikashandilya13-coder/llm-architecture-assistant)

A **Streamlit-based AI assistant** that generates **Architecture Decision Records (ADRs)**  
from system context + NFRs.

---

## ✨ Features
- **Mock Mode** → Demo-ready with no API key (pre-baked ADR + trade-off matrix).  
- **Real API Mode** → Connect to OpenAI API for live ADR generation.  
- **Downloadable ADRs** → Save generated decisions in Markdown format.  
- **Trade-off Matrix** → Compare Cost, Complexity, Speed, and Reliability.  

---

## 🚀 Run Locally
Clone the repo and install dependencies:
```bash
git clone https://github.com/monikashandilya13-coder/llm-architecture-assistant.git
cd llm-architecture-assistant
pip install -r requirements.txt
```

Run the Streamlit app:
```bash
streamlit run app.py
```

---

## 🌐 Run Online
- **Live Demo:** [Click here](https://[monikashandilya13-coder-llm-architecture-assistant.streamlit.app](https://llm-architecture-assistant.streamlit.app/))  
- **Deploy Your Own:** [One-click deploy on Streamlit Cloud](https://share.streamlit.io/deploy?repo=https://github.com/monikashandilya13-coder/llm-architecture-assistant)

---

## 📂 Project Structure
```
llm-architecture-assistant/
│
├── app.py                # Main Streamlit app
├── requirements.txt      # Dependencies
├── README.md             # Project documentation
├── seed/
│   ├── NFRs.md           # Example non-functional requirements
│   └── Current-Context.md# Example legacy system context
└── out/                  # Generated ADRs will be saved here
```

---

## 📑 ADR (Architecture Decision Record)
An **ADR** captures an important technical decision:
- **Context** → requirements, constraints, NFRs  
- **Options** → evaluated alternatives with pros/cons/risks  
- **Decision** → the chosen path and rationale  
- **Consequences** → positive & negative impacts  
- **Fitness Functions** → measurable success criteria  

---

## 🔮 Next Steps
- Add more decision templates (e.g., API Gateway, Messaging Bus).  
- Export ADRs back to GitHub automatically.  
- Switch from Mock → Real LLM mode once API access is available.  

---
