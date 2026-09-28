# 💼 Enterprise Deal Intelligence Agent

An AI sales intelligence agent powered by **Hindsight Persistent Memory** and **Groq LLaMA 3.3**, engineered to remember prospect details, track evolving enterprise deals across meetings, identify deal risks, and instantly generate executive meeting briefs.

---

## 🎯 The Problem

Enterprise sales cycles last months and involve dozens of stakeholders, shifting requirements, and competitor evaluations. Sales professionals frequently lose critical context between meetings:
- Forgetting confirmed budgets or key decision makers.
- Missing shifts in prospect sentiment (e.g. competitor evaluation completed).
- Starting from scratch before every customer interaction.

---

## 💡 The Solution

The **Enterprise Deal Intelligence Agent** acts as an institutional memory co-pilot. It uses **Hindsight** biomimetic persistent memory to store every deal interaction (`retain`) and retrieve relevant context (`recall`), allowing **Groq LLaMA 3.3** to reason accurately without hallucinating unconfirmed facts.

```
                    USER / SALES REP
                           │
                           ▼
                  ┌─────────────────┐
                  │  Streamlit UI   │
                  └────────┬────────┘
                           │
                           ▼
               ┌───────────────────────┐
               │ Deal Intelligence     │
               │        Agent          │
               └───────────┬───────────┘
                           │
             ┌─────────────┴─────────────┐
             ▼                           ▼
    ┌─────────────────┐         ┌─────────────────┐
    │ Hindsight Memory│         │    Groq LLM     │
    │ (Recall Memory) │         │ (LLaMA 3.3 70B) │
    └────────┬────────┘         └────────┬────────┘
             │                           │
             └─────────────┬─────────────┘
                           │
                           ▼
                      AI Response
                           │
                           ▼
                  ┌─────────────────┐
                  │ Hindsight Retain│ (Store new deal updates)
                  └─────────────────┘
```

---

## 🚀 Key Features

1. **Persistent Deal Memory (`Hindsight retain & recall`)**:
   - Retains facts across sessions (budget, decision makers, objections, competitors).
   - Recalls relevant history even after full application restarts.
2. **Anti-Hallucination Guardrails**:
   - Strictly refuses to invent budgets or contacts if not in recalled memory.
3. **📋 Executive Meeting Preparation (`Prepare Me`)**:
   - Generates a full briefing document: Deal Stage, Budget, Key Stakeholders, Pain Points, Competitors, Objections, Strategic Questions to Ask, and Recommended Focus.
4. **⚠️ Deal Risk & Qualification Assessment**:
   - Evaluates active risks, missing MEDDPICC qualifiers, and tactical mitigation actions.
5. **🔄 "What Changed?" & Timeline Tracking**:
   - Compares previous memory states with current status (e.g., "Was evaluating Microsoft; completed evaluation and now prefers our solution").
6. **📧 Contextual Follow-up Email Generator**:
   - Generates personalized follow-up emails grounded in the latest discussion points.
7. **🧠 Live Hindsight Memory Inspector**:
   - Real-time transparency viewer displaying all retained memory records, timestamps, and cloud sync status.
8. **🏢 Multi-Account Support**:
   - Pre-configured accounts (`TechNova`, `Acme Corp`, `GlobalFin`, `HealthPlus`, `RetailX`) and custom account creation.

---

## 🛠️ Tech Stack

- **Framework**: Python 3.10+
- **Frontend UI**: [Streamlit](https://streamlit.io/)
- **Reasoning Engine**: [Groq](https://groq.com/) (`llama-3.3-70b-versatile`)
- **Memory Engine**: [Hindsight](https://vectorize.io/) (`hindsight-client` retain & recall)
- **Environment**: `python-dotenv`

---

## 📦 Project Structure

```text
enterprise-deal-intelligence/
├── .env                  # API keys for Groq and Hindsight (git-ignored)
├── .gitignore            # Git ignore file
├── app.py                # Streamlit enterprise dashboard UI
├── agent.py              # Deal intelligence agent logic & Groq integration
├── memory.py             # Hindsight Cloud SDK retain/recall + persistent mirror
├── prompts.py            # Prompt engineering & anti-hallucination templates
├── requirements.txt      # Python dependencies
├── README.md             # Documentation & benchmark test guide
└── venv/                 # Virtual environment
```

---

## ⚡ Quick Start Guide

### 1. Activate the Virtual Environment

On Windows:
```powershell
cd enterprise-deal-intelligence
.\venv\Scripts\activate
```

On macOS/Linux:
```bash
cd enterprise-deal-intelligence
source venv/bin/activate
```

### 2. Configure Your API Keys

Edit the `.env` file in `enterprise-deal-intelligence/`:
```ini
GROQ_API_KEY=gsk_your_groq_api_key_here
HINDSIGHT_API_KEY=your_hindsight_api_key_here
HINDSIGHT_API_URL=https://api.hindsight.vectorize.io
```

*(Note: If API keys are not supplied initially, the agent automatically runs in a resilient persistent demo mode, enabling you to test the complete workflow immediately).*

### 3. Launch the Application

```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`.

---

## 🧪 Validation & Benchmark Test Scenarios

### Scenario 1 — Store & Retain
1. Select **TechNova** from the sidebar.
2. In the chat, send:
   > *"TechNova is interested in our AI platform. Their budget is ₹25 lakh. Rahul from IT is the decision maker. Their biggest concern is data security. They are also evaluating Microsoft."*
3. Notice Hindsight confirms retention of the deal update.

### Scenario 2 — Persistent Recall Across Sessions
1. Refresh your browser or restart the Streamlit server.
2. Ask:
   > *"What is TechNova's budget and who is the decision maker?"*
3. Expected Output:
   > *"Budget is ₹25 lakh and Rahul from IT is the decision maker."*

### Scenario 3 — Multi-Company Isolation
1. Switch account to **Acme Corp**.
2. Send:
   > *"Acme Corp budget is ₹40 lakh. Priya is evaluating Salesforce."*
3. Ask:
   > *"What is Acme's budget?"*
4. Expected: Returns ₹40 lakh (isolated from TechNova's ₹25 lakh).

### Scenario 4 — Temporal "What Changed?"
1. Under **TechNova**, send:
   > *"TechNova completed the Microsoft evaluation. They now prefer our solution and have entered Negotiation stage."*
2. Switch to the **Timeline & Changes** tab and click **Analyze 'What Changed?'**.
3. Expected: Recognizes that Microsoft evaluation is now complete and stage progressed to Negotiation.

### Scenario 5 — Executive Meeting Preparation
1. Click the **Meeting Brief** tab.
2. Click **Generate Brief for TechNova**.
3. View the structured briefing document with deal stage, decision maker, budget, pain points, competitor status, and strategic questions to ask.

---

## 🛡️ Anti-Hallucination Guarantee

If a query asks about unrecorded details (e.g. asking for HealthPlus budget before anything is stored), the agent guarantees:
> *"I don't have a confirmed budget in the available deal memory."*
It will never fabricate numbers or stakeholder titles.
