"""
app.py - Enterprise Deal Intelligence Agent UI
Streamlit web application for managing enterprise deals with Hindsight memory and Groq LLM.
"""

import os
import streamlit as st
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from memory import (
    retain_memory,
    recall_memory,
    get_all_memories,
    clear_memories,
    get_memory_manager
)
from agent import get_deal_agent, KNOWN_COMPANIES

# Page Configuration
st.set_page_config(
    page_title="Enterprise Deal Intelligence Agent",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    .main-header {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #312e81 100%);
        padding: 24px 30px;
        border-radius: 14px;
        color: #f8fafc;
        margin-bottom: 24px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.2);
    }
    
    .main-header h1 {
        margin: 0;
        font-size: 1.85rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        color: #ffffff;
    }
    
    .main-header p {
        margin: 6px 0 0 0;
        font-size: 0.95rem;
        color: #cbd5e1;
    }

    .badge-pill {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-right: 6px;
    }
    
    .badge-cloud { background: #dcfce7; color: #166534; border: 1px solid #86efac; }
    .badge-local { background: #fef3c7; color: #92400e; border: 1px solid #fde68a; }
    .badge-groq { background: #e0e7ff; color: #3730a3; border: 1px solid #c7d2fe; }

    .deal-card {
        background: #ffffff;
        border-radius: 12px;
        padding: 18px 22px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
        margin-bottom: 16px;
    }

    .memory-item {
        background: #f8fafc;
        border-left: 4px solid #6366f1;
        padding: 12px 16px;
        border-radius: 0 8px 8px 0;
        margin-bottom: 10px;
        font-size: 0.9rem;
    }

    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s ease;
    }

    .stButton>button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.2);
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session State
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "selected_company" not in st.session_state:
    st.session_state.selected_company = "TechNova"
if "deal_stage" not in st.session_state:
    st.session_state.deal_stage = "Negotiation"

mem_mgr = get_memory_manager()
deal_agent = get_deal_agent()

# Sidebar: System Settings & Deal Context
with st.sidebar:
    st.markdown("### 🏢 Enterprise Deal Cockpit")
    
    # Company selection
    all_companies = KNOWN_COMPANIES + ["+ Custom Company"]
    selected_comp = st.selectbox(
        "Active Deal / Account",
        all_companies,
        index=all_companies.index(st.session_state.selected_company) if st.session_state.selected_company in all_companies else 0
    )

    if selected_comp == "+ Custom Company":
        custom_name = st.text_input("Enter Company Name", "VertexBio").strip()
        current_company = custom_name if custom_name else "CustomCorp"
    else:
        current_company = selected_comp

    st.session_state.selected_company = current_company

    # Deal Stage
    stages = ["Lead", "Discovery", "Evaluation", "Negotiation", "Procurement", "Closed"]
    deal_stage = st.selectbox("Current Deal Stage", stages, index=3)
    st.session_state.deal_stage = deal_stage

    st.divider()

    # System Status Indicators
    st.markdown("#### ⚡ System Connections")
    
    # Hindsight status
    if mem_mgr.cloud_active:
        st.markdown('<span class="badge-pill badge-cloud">🟢 Hindsight Cloud Active</span>', unsafe_allow_html=True)
        st.caption(f"Bank ID: `{mem_mgr.bank_id}`")
    else:
        st.markdown('<span class="badge-pill badge-local">🟡 Hindsight Local Mirror</span>', unsafe_allow_html=True)
        st.caption("Operating in persistent local mirror mode")

    # Groq status
    if deal_agent.groq_active:
        st.markdown('<span class="badge-pill badge-groq">🟢 Groq LLaMA 3.3 Active</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="badge-pill badge-local">🟡 Groq API Key Needed</span>', unsafe_allow_html=True)
        st.caption("Provide key below or in `.env` to enable full LLaMA reasoning.")

    # API Key Input Expanders
    with st.expander("🔑 Configure API Keys"):
        groq_input = st.text_input("Groq API Key", value=os.getenv("GROQ_API_KEY", ""), type="password")
        hindsight_input = st.text_input("Hindsight API Key", value=os.getenv("HINDSIGHT_API_KEY", ""), type="password")
        
        if st.button("Save & Reconnect"):
            if groq_input:
                os.environ["GROQ_API_KEY"] = groq_input
                deal_agent.groq_api_key = groq_input
                deal_agent._init_groq()
            if hindsight_input:
                os.environ["HINDSIGHT_API_KEY"] = hindsight_input
                mem_mgr.api_key = hindsight_input
                mem_mgr._init_hindsight()
            st.success("Configuration updated!")
            st.rerun()

    st.divider()

    # Demo Dataset Loader
    st.markdown("#### 🚀 Demo Scenarios")
    if st.button("⚡ Load Benchmark Demo Deals", use_container_width=True):
        # 1. TechNova Scenario (Multiple stages & evolution)
        retain_memory("TechNova is interested in our AI platform. Their budget is ₹25 lakh. Rahul from IT is the decision maker. Their biggest concern is data security. They are also evaluating Microsoft.", "TechNova")
        retain_memory("Technical deep dive with Rahul from IT. We explained our SOC-2 and AES-256 compliance, resolving their initial data security concern.", "TechNova")
        retain_memory("TechNova completed the Microsoft evaluation. They now prefer our solution and have entered Negotiation stage. Target rollout in Q4.", "TechNova")

        # 2. Acme Corp Scenario
        retain_memory("Acme Corp is evaluating our platform for enterprise workflow automation. Their budget is ₹40 lakh. Priya is the chief decision maker. Main concern is Salesforce integration. Stage: Evaluation.", "Acme Corp")

        # 3. GlobalFin Scenario
        retain_memory("GlobalFin procurement meeting scheduled. Budget allocated is ₹85 lakh. Decision maker is Sanjay, VP Engineering. They dropped Oracle due to latency issues.", "GlobalFin")

        st.success("Loaded demo scenarios for TechNova, Acme Corp, and GlobalFin!")
        st.rerun()

    if st.button("🗑️ Reset All Memories", use_container_width=True):
        clear_memories("all")
        st.session_state.chat_history = []
        st.warning("All memory banks cleared.")
        st.rerun()

# Main Header
st.markdown(f"""
<div class="main-header">
    <h1>💼 Enterprise Deal Intelligence Agent</h1>
    <p>Persistent sales memory powered by <b>Hindsight Memory</b> (Retain & Recall) and <b>Groq LLaMA 3.3</b></p>
    <div style="margin-top: 12px;">
        <span style="background: rgba(255,255,255,0.15); padding: 4px 10px; border-radius: 6px; font-size: 0.85rem; margin-right: 8px;">🏢 Account: <b>{current_company}</b></span>
        <span style="background: rgba(255,255,255,0.15); padding: 4px 10px; border-radius: 6px; font-size: 0.85rem;">🎯 Stage: <b>{st.session_state.deal_stage}</b></span>
    </div>
</div>
""", unsafe_allow_html=True)

# Tabs
tab_chat, tab_brief, tab_risks, tab_email, tab_timeline, tab_memories = st.tabs([
    "💬 Deal Chat",
    "📋 Meeting Brief",
    "⚠️ Risk Analysis",
    "📧 Follow-up Email",
    "🔄 Timeline & Changes",
    "🧠 Memory Bank"
])

# ==========================================
# TAB 1: DEAL CHAT
# ==========================================
with tab_chat:
    st.markdown(f"#### Ask or update anything about **{current_company}**")

    # Quick Suggestion Chips
    col_q1, col_q2, col_q3, col_q4 = st.columns(4)
    with col_q1:
        if st.button("💰 What is the budget?", use_container_width=True):
            st.session_state.preset_query = f"What is the budget for {current_company}?"
    with col_q2:
        if st.button("👤 Who is the decision maker?", use_container_width=True):
            st.session_state.preset_query = f"Who is the decision maker at {current_company}?"
    with col_q3:
        if st.button("🏢 What competitors exist?", use_container_width=True):
            st.session_state.preset_query = f"What competitors are {current_company} evaluating?"
    with col_q4:
        if st.button("🔄 What changed in this deal?", use_container_width=True):
            st.session_state.preset_query = f"What changed recently in the {current_company} deal?"

    # Display Chat History
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                if "meta" in msg and msg["meta"]:
                    with st.expander("🔍 Memory Trace"):
                        st.json(msg["meta"])

    # Chat Input
    query_val = st.session_state.pop("preset_query", None)
    user_prompt = st.chat_input("Enter deal notes, updates, or questions (e.g., 'TechNova budget is ₹25 lakh')...") or query_val

    if user_prompt:
        # Display user message
        st.session_state.chat_history.append({"role": "user", "content": user_prompt})
        with st.chat_message("user"):
            st.markdown(user_prompt)

        # Process with Agent
        with st.chat_message("assistant"):
            with st.spinner("Recalling deal memories & reasoning with Groq..."):
                response = deal_agent.process_message(user_prompt, active_company=current_company)
                answer = response["answer"]
                st.markdown(answer)

                meta_info = {
                    "company": response["company"],
                    "recalled_items_count": len(response["recalled_memories"]),
                    "retained_to_memory": bool(response["retained_record"]),
                    "source": "Hindsight Retain + Recall"
                }

                if response["retained_record"]:
                    st.info(f"🧠 Hindsight Retained: Stored new deal intelligence into bank `{mem_mgr.bank_id}`")

                with st.expander("🔍 Recall Context & Metadata"):
                    st.write("**Recalled Memory Snippets:**")
                    st.code(response["context_used"])

                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": answer,
                    "meta": meta_info
                })

# ==========================================
# TAB 2: MEETING BRIEF
# ==========================================
with tab_brief:
    st.markdown(f"### 📋 Executive Meeting Preparation: **{current_company}**")
    st.caption("Synthesizes all verified deal facts from persistent memory into an actionable executive brief.")

    if st.button(f"Generate Brief for {current_company}", type="primary", use_container_width=True):
        with st.spinner(f"Retrieving memories and building meeting brief for {current_company}..."):
            brief = deal_agent.prepare_meeting(current_company)
            st.markdown(brief)
            
            # Download button
            st.download_button(
                label="📥 Download Brief (Markdown)",
                data=brief,
                file_name=f"{current_company}_Meeting_Brief.md",
                mime="text/markdown"
            )

# ==========================================
# TAB 3: RISK ANALYSIS
# ==========================================
with tab_risks:
    st.markdown(f"### ⚠️ Deal Risk & Qualification Assessment: **{current_company}**")
    st.caption("Identifies known blockers, missing MEDDPICC qualifiers, and tactical mitigation recommendations.")

    if st.button(f"Run Risk Analysis for {current_company}", type="primary", use_container_width=True):
        with st.spinner(f"Analyzing risks for {current_company}..."):
            risks = deal_agent.analyze_risks(current_company)
            st.markdown(risks)

# ==========================================
# TAB 4: FOLLOW-UP EMAIL
# ==========================================
with tab_email:
    st.markdown(f"### 📧 Automated Follow-up Email Generator: **{current_company}**")
    st.caption("Drafts a tailored email addressing discussed points, pain points, and specific next steps.")

    custom_instructions = st.text_area(
        "Custom Instructions / Context (Optional)",
        placeholder="e.g. Propose a call for Thursday at 3 PM to review the implementation timeline."
    )

    if st.button(f"Draft Follow-up Email for {current_company}", type="primary", use_container_width=True):
        with st.spinner("Drafting contextual email..."):
            email_draft = deal_agent.generate_followup_email(current_company, instructions=custom_instructions)
            st.markdown(email_draft)

# ==========================================
# TAB 5: TIMELINE & WHAT CHANGED
# ==========================================
with tab_timeline:
    st.markdown(f"### 🔄 Deal Evolution & What Changed: **{current_company}**")
    
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        if st.button(f"🔍 Analyze 'What Changed?' for {current_company}", use_container_width=True):
            with st.spinner("Comparing historical memory states..."):
                changed_text = deal_agent.what_changed(current_company)
                st.markdown(changed_text)

    with col_t2:
        if st.button(f"📅 Extract Timeline for {current_company}", use_container_width=True):
            with st.spinner("Extracting chronological deal milestones..."):
                timeline_text = deal_agent.get_timeline(current_company)
                st.markdown(timeline_text)

# ==========================================
# TAB 6: MEMORY BANK VIEWER
# ==========================================
with tab_memories:
    st.markdown("### 🧠 Hindsight Deal Memory Inspector")
    st.caption("Inspect all persistent deal facts stored across sessions.")

    col_m1, col_m2 = st.columns([3, 1])
    with col_m1:
        filter_opt = st.selectbox("Filter Memory by Account", ["All Accounts"] + KNOWN_COMPANIES, index=0)
    with col_m2:
        if st.button("🔄 Refresh"):
            st.rerun()

    active_filter = None if filter_opt == "All Accounts" else filter_opt
    all_stored = get_all_memories(company=active_filter)

    st.write(f"Total Memory Records: **{len(all_stored)}**")

    # Manual Memory Addition Tool
    with st.expander("➕ Manually Add Memory Record"):
        with st.form("manual_retain_form"):
            mem_text = st.text_area("Memory Content / Notes", placeholder="e.g. Spoke with Rahul. Budget approved for ₹25 lakh.")
            target_acc = st.text_input("Company Tag", value=current_company)
            submitted = st.form_submit_button("Retain to Hindsight")
            if submitted and mem_text.strip():
                record = retain_memory(mem_text.strip(), company=target_acc.strip())
                st.success(f"Retained to memory bank with ID: {record['id']}")
                st.rerun()

    # Memory list cards
    if not all_stored:
        st.info("No memories stored yet. Click '⚡ Load Benchmark Demo Deals' in the sidebar or type a deal update in Deal Chat.")
    else:
        for idx, item in enumerate(reversed(all_stored), 1):
            with st.container():
                st.markdown(f"""
                <div class="memory-item">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                        <span style="font-weight: 700; color: #4338ca;">🏢 {item.get('company', 'General')}</span>
                        <span style="font-size: 0.8rem; color: #64748b;">🕒 {item.get('timestamp', 'Recent')}</span>
                    </div>
                    <div>{item.get('content', '')}</div>
                    <div style="margin-top: 6px; font-size: 0.75rem; color: #94a3b8;">
                        ID: <code>{item.get('id', 'N/A')}</code> | Cloud Synced: <code>{item.get('synced_to_cloud', False)}</code>
                    </div>
                </div>
                """, unsafe_allow_html=True)
