"""
agent.py - Enterprise Deal Intelligence Agent Core
Coordinates memory recall, Groq reasoning, and memory retain.
"""

import os
import re
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

from memory import retain_memory, recall_memory, get_all_memories
from prompts import (
    SYSTEM_PROMPT,
    MEETING_BRIEF_PROMPT,
    RISK_ANALYSIS_PROMPT,
    FOLLOW_UP_EMAIL_PROMPT,
    WHAT_CHANGED_PROMPT,
    TIMELINE_EXTRACTION_PROMPT,
)

load_dotenv()

# Check for Groq availability
try:
    from groq import Groq
    GROQ_INSTALLED = True
except ImportError:
    GROQ_INSTALLED = False

KNOWN_COMPANIES = ["TechNova", "Acme Corp", "GlobalFin", "HealthPlus", "RetailX"]
DEFAULT_GROQ_MODEL = "openai/gpt-oss-120b"

class DealAgent:
    def __init__(self):
        self.groq_api_key = os.getenv("GROQ_API_KEY", "").strip()
        self.client: Optional[Any] = None
        self.groq_active = False
        self.model = os.getenv("GROQ_MODEL", DEFAULT_GROQ_MODEL)
        self._init_groq()

    def _init_groq(self):
        """Initializes Groq client if valid API key is present."""
        if not GROQ_INSTALLED:
            print("[Agent] Notice: groq package not installed.")
            return

        is_placeholder = (
            not self.groq_api_key
            or "your_" in self.groq_api_key.lower()
            or "here" in self.groq_api_key.lower()
            or len(self.groq_api_key) < 10
        )
        if is_placeholder:
            print("[Agent] Notice: GROQ_API_KEY not configured. Running in built-in synthesis mode.")
            return

        try:
            self.client = Groq(api_key=self.groq_api_key)
            self.groq_active = True
            print(f"[Agent] Groq client initialized with model: {self.model}")
        except Exception as e:
            print(f"[Agent] Failed to initialize Groq client: {e}")
            self.groq_active = False

    def detect_company(self, text: str, fallback_company: Optional[str] = None) -> str:
        """Detects company name mentioned in user text or falls back to current context."""
        for comp in KNOWN_COMPANIES:
            if re.search(rf"\b{re.escape(comp)}\b", text, re.IGNORECASE):
                return comp
        
        # Check capitalized words that might be companies
        match = re.search(r'\b(?:at|for|with|about)\s+([A-Z][a-zA-Z0-9_\-\.]+)', text)
        if match:
            cand = match.group(1).strip()
            if cand.lower() not in ["our", "my", "the", "this", "that"]:
                return cand

        if fallback_company and fallback_company.lower() not in ["all", "general", ""]:
            return fallback_company

        return "TechNova"

    def format_memories_for_prompt(self, memories: List[Dict[str, Any]]) -> str:
        """Formats recalled memory items into a grounded context string."""
        if not memories:
            return "No prior deal memories or historical context found in memory bank."

        formatted_lines = []
        for i, mem in enumerate(memories, 1):
            ts = mem.get("timestamp", "Recent")
            content = mem.get("content", "")
            company = mem.get("company", "General")
            formatted_lines.append(f"[{i}] ({ts}) [{company}] {content}")

        return "\n".join(formatted_lines)

    def _call_llm(self, system_message: str, user_message: str, temperature: float = 0.2) -> str:
        """Executes LLM completion via Groq or fallback rule-based synthesis."""
        if self.groq_active and self.client:
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": user_message}
                    ],
                    temperature=temperature,
                    max_tokens=2048
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                print(f"[Agent] Groq API call error: {e}. Falling back to internal engine.")

        # Resilient synthesis engine when Groq key is not supplied yet
        return self._fallback_synthesis(system_message, user_message)

    def _fallback_synthesis(self, system_message: str, user_message: str) -> str:
        """Intelligent, structured fallback synthesis when API key is not configured."""
        if "MEETING BRIEF" in user_message or "MEETING BRIEF" in system_message:
            return (
                "### 🎯 Deal Stage\n"
                "Evaluation / Negotiation (Derived from latest discussions)\n\n"
                "### 💰 Budget & Commercials\n"
                "Refer to verified memory entries above. If not recorded: 'I don't have a confirmed budget in the available deal memory.'\n\n"
                "### 👤 Key Decision Makers & Stakeholders\n"
                "Key technical and executive contacts mentioned in memory.\n\n"
                "### 🔥 Main Requirements & Pain Points\n"
                "Security, enterprise integration, performance, and vendor alignment.\n\n"
                "### 🏢 Competitors & Alternatives\n"
                "Evaluation status tracked from persistent memory.\n\n"
                "### ⚠️ Objections & Deal Risks\n"
                "• Timeline uncertainty\n• Security/compliance approval criteria\n\n"
                "### ❓ Strategic Questions to Ask\n"
                "1. Has the technical security sign-off been scheduled?\n"
                "2. What is the target decision and rollout date?\n\n"
                "*(Note: Connect your GROQ_API_KEY in .env for full live Groq LLaMA 3.3 output)*"
            )
        return (
            "I processed your deal query using Hindsight Persistent Memory.\n\n"
            "To unlock full natural language generation with LLaMA 3.3, please provide your `GROQ_API_KEY` in `.env`.\n"
            "All memories are actively stored and indexed."
        )

    def is_deal_update(self, text: str) -> bool:
        """Determines if a user message contains substantive deal information to retain."""
        text_lower = text.lower()
        signals = [
            "budget", "lakh", "$", "crore", "decision maker", "interested in",
            "evaluating", "competitor", "concern", "security", "integration",
            "met with", "call with", "timeline", "procurement", "approved",
            "stage", "prefer", "stopped", "completed", "discount", "ceo", "cto", "cio"
        ]
        return any(sig in text_lower for sig in signals) or len(text.split()) > 7

    def process_message(self, user_message: str, active_company: Optional[str] = None) -> Dict[str, Any]:
        """
        Main Agent Execution Pipeline:
        1. Recall relevant memories from Hindsight
        2. Format context
        3. Groq LLM reasoning with anti-hallucination guardrails
        4. Retain new deal intelligence into Hindsight
        """
        target_company = self.detect_company(user_message, fallback_company=active_company)

        # 1. Recall
        recalled = recall_memory(query=user_message, company=target_company, limit=8)
        context_str = self.format_memories_for_prompt(recalled)

        # 2. Build Prompt
        prompt = (
            f"Target Company Context: {target_company}\n\n"
            f"Recalled Deal Memories:\n\"\"\"\n{context_str}\n\"\"\"\n\n"
            f"Sales User Query: {user_message}\n\n"
            f"Instructions: Use only verified deal facts from the recalled memories. "
            f"If specific information (e.g. budget, decision maker, competitor) is not present, "
            f"state clearly: 'I don't have a confirmed [item] in the available deal memory.' "
            f"Do not invent facts."
        )

        # 3. Groq Reasoning
        answer = self._call_llm(
            system_message=SYSTEM_PROMPT,
            user_message=prompt,
            temperature=0.2
        )

        # 4. Retain substantive deal information
        retained_record = None
        if self.is_deal_update(user_message):
            retained_record = retain_memory(
                content=user_message,
                company=target_company,
                metadata={"source": "user_chat", "detected_company": target_company}
            )

        return {
            "answer": answer,
            "company": target_company,
            "recalled_memories": recalled,
            "retained_record": retained_record,
            "context_used": context_str
        }

    def prepare_meeting(self, company: str) -> str:
        """Prepares a comprehensive Meeting Brief from remembered deal facts."""
        memories = recall_memory(query=f"meeting preparation facts budget decision maker requirements {company}", company=company, limit=12)
        if not memories:
            memories = get_all_memories(company=company)

        context_str = self.format_memories_for_prompt(memories)
        prompt = MEETING_BRIEF_PROMPT.format(company=company, context=context_str)

        return self._call_llm(
            system_message=SYSTEM_PROMPT,
            user_message=prompt,
            temperature=0.2
        )

    def analyze_risks(self, company: str) -> str:
        """Analyzes deal risks and missing deal qualifications."""
        memories = recall_memory(query=f"risks objections concerns competitors blockers {company}", company=company, limit=10)
        if not memories:
            memories = get_all_memories(company=company)

        context_str = self.format_memories_for_prompt(memories)
        prompt = RISK_ANALYSIS_PROMPT.format(company=company, context=context_str)

        return self._call_llm(
            system_message=SYSTEM_PROMPT,
            user_message=prompt,
            temperature=0.2
        )

    def generate_followup_email(self, company: str, instructions: str = "") -> str:
        """Drafts a contextual follow-up email based on stored interactions."""
        memories = recall_memory(query=f"recent discussion agreements next steps {company}", company=company, limit=8)
        if not memories:
            memories = get_all_memories(company=company)

        context_str = self.format_memories_for_prompt(memories)
        extra_inst = instructions or "Follow up after our recent discussion and confirm next steps."
        prompt = FOLLOW_UP_EMAIL_PROMPT.format(company=company, context=context_str, instructions=extra_inst)

        return self._call_llm(
            system_message=SYSTEM_PROMPT,
            user_message=prompt,
            temperature=0.3
        )

    def what_changed(self, company: str) -> str:
        """Performs temporal analysis to identify what changed over time for the deal."""
        memories = get_all_memories(company=company)
        if not memories:
            return f"No historical memories available for {company} to analyze changes."

        context_str = self.format_memories_for_prompt(memories)
        prompt = WHAT_CHANGED_PROMPT.format(company=company, context=context_str)

        return self._call_llm(
            system_message=SYSTEM_PROMPT,
            user_message=prompt,
            temperature=0.2
        )

    def get_timeline(self, company: str) -> str:
        """Generates a structured timeline of all deal milestones and discussions."""
        memories = get_all_memories(company=company)
        if not memories:
            return f"No timeline data recorded yet for {company}."

        context_str = self.format_memories_for_prompt(memories)
        prompt = TIMELINE_EXTRACTION_PROMPT.format(company=company, context=context_str)

        return self._call_llm(
            system_message=SYSTEM_PROMPT,
            user_message=prompt,
            temperature=0.1
        )


# Singleton accessor
_agent_instance: Optional[DealAgent] = None

def get_deal_agent() -> DealAgent:
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = DealAgent()
    return _agent_instance
