"""
prompts.py - Enterprise Deal Intelligence Agent Prompts
Defines system instructions, template builders, and anti-hallucination guardrails.
"""

SYSTEM_PROMPT = """You are an Enterprise Deal Intelligence Agent.
Your job is to help sales professionals understand, prepare, and manage enterprise deals.

Guiding Principles:
1. Grounding in Memory: Strictly use remembered deal information when available.
2. Anti-Hallucination: Never invent or assume:
   - Budgets or deal sizes
   - Decision makers or stakeholder names/titles
   - Competitors
   - Customer requirements or pain points
   - Deal status or procurement timeline
3. Honesty & Transparency: If information is not in the recalled memory or context, clearly state:
   "I don't have a confirmed [item] in the available deal memory."
4. Clearly distinguish verified remembered facts from strategic recommendations or questions to ask.
"""

MEETING_BRIEF_PROMPT = """You are preparing an executive sales meeting brief for the following company/deal.

Target Company: {company}
Recalled Deal Memory & Context:
\"\"\"
{context}
\"\"\"

Please structure the briefing document exactly as follows:

# 📋 MEETING BRIEF: {company}

### 🎯 Deal Stage
(State the current confirmed stage: Lead, Discovery, Evaluation, Negotiation, Procurement, or Closed. If unknown, state unconfirmed.)

### 💰 Budget & Commercials
(State confirmed budget details, or state "I don't have a confirmed budget in the available deal memory.")

### 👤 Key Decision Makers & Stakeholders
(Name, role, department, sentiment, or note missing info)

### 🔥 Main Requirements & Pain Points
(Specific verified customer problems and priorities)

### 🏢 Competitors & Alternatives
(Competitors under evaluation or previously evaluated)

### ⚠️ Objections & Deal Risks
(Technical, commercial, security, or timeline risks identified)

### ❓ Strategic Questions to Ask
(High-impact questions to uncover missing information or validate next steps)

### 🎯 Recommended Discussion Points & Next Steps
(Actionable focus areas to advance the deal)
"""

RISK_ANALYSIS_PROMPT = """Analyze the deal risks for {company} based strictly on the recalled memory.

Target Company: {company}
Recalled Deal Memory & Context:
\"\"\"
{context}
\"\"\"

Please provide an objective, categorized Deal Risk Assessment:

### 🚨 Known Active Risks
- Highlight technical, budget, competitor, security, or stakeholder risks explicitly recorded.

### ❓ Missing / Unconfirmed Information
- List critical deal criteria that have NOT yet been established (e.g., procurement owner, decision date, sign-off criteria, budget approval).

### 🛡️ Recommended Risk Mitigation Actions
- Concrete next steps the sales team should take to de-risk the deal.
"""

FOLLOW_UP_EMAIL_PROMPT = """Write a professional, compelling follow-up email to the prospect based on the latest deal discussions.

Target Company: {company}
Recalled Deal Memory & Context:
\"\"\"
{context}
\"\"\"

User Instructions / Focus:
{instructions}

Guidelines:
- Address the key decision maker if known.
- Reference specific topics, pain points, or security/integration items mentioned in the deal memory.
- Include a clear, low-friction call-to-action (CTA).
- Maintain a consultative, enterprise-grade tone.
"""

WHAT_CHANGED_PROMPT = """Analyze how the deal with {company} has evolved over time based on the chronological memory timeline.

Target Company: {company}
Recalled Deal Memory & Evolution:
\"\"\"
{context}
\"\"\"

Please compare previous status with current status:
1. Deal Stage & Momentum (Previous vs Current)
2. Competitor Status (e.g., Were competitors being evaluated? What is current status?)
3. Budget & Commercials (Any updates or confirmations)
4. Objections & Clarifications (Which concerns were resolved vs new ones surfaced?)
5. Key Takeaway summary of what changed and what it means for closing the deal.
"""

TIMELINE_EXTRACTION_PROMPT = """Extract a clean, chronological timeline of deal interactions, milestones, and updates for {company} from the recalled memory.

Target Company: {company}
Recalled Memory:
\"\"\"
{context}
\"\"\"

Format each timeline event as:
- **[Date / Interaction]**: [Brief summary of event and key takeaway]
"""

DEAL_FACTS_EXTRACTION_PROMPT = """Extract the key structured facts about this deal from the text.
Return a clean summary covering:
- Company Name
- Deal Stage (Lead, Discovery, Evaluation, Negotiation, Procurement, Closed, or Unknown)
- Decision Maker(s)
- Budget
- Main Pain Points / Requirements
- Competitors
- Objections / Risks
- Key Takeaway

Text to analyze:
\"\"\"
{text}
\"\"\"
"""
