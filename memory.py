"""
memory.py - Enterprise Deal Intelligence Memory Layer
Handles persistent memory retain, recall, and reflect using Hindsight Cloud SDK
with an automatic persistent local fallback mirror for 100% offline & demo reliability.
"""

import os
import json
import uuid
import re
import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

try:
    from hindsight_client import Hindsight
    HINDSIGHT_INSTALLED = True
except ImportError:
    HINDSIGHT_INSTALLED = False

DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
LOCAL_MEMORY_FILE = DATA_DIR / "enterprise_deals_memory.json"

DEFAULT_BANK_ID = "enterprise-deals"

class MemoryManager:
    def __init__(self):
        self.api_key = os.getenv("HINDSIGHT_API_KEY", "").strip()
        self.base_url = os.getenv("HINDSIGHT_API_URL", "https://api.hindsight.vectorize.io").strip()
        self.bank_id = os.getenv("HINDSIGHT_BANK_ID", DEFAULT_BANK_ID).strip()
        self.client: Optional[Any] = None
        self.cloud_active = False
        self.last_status_message = ""

        self._init_local_store()
        self._init_hindsight()

    def _init_local_store(self):
        """Ensures local storage file exists."""
        if not LOCAL_MEMORY_FILE.exists():
            initial_data = {
                "banks": {
                    self.bank_id: []
                },
                "metadata": {
                    "created_at": datetime.datetime.now().isoformat(),
                    "system": "Enterprise Deal Intelligence Persistent Memory"
                }
            }
            with open(LOCAL_MEMORY_FILE, "w", encoding="utf-8") as f:
                json.dump(initial_data, f, indent=2)

    def _init_hindsight(self):
        """Initializes connection to Hindsight Cloud SDK if configured."""
        if not HINDSIGHT_INSTALLED:
            self.last_status_message = "Hindsight SDK not installed. Running on local persistent memory mirror."
            return

        is_placeholder = (
            not self.api_key
            or "your_" in self.api_key.lower()
            or "here" in self.api_key.lower()
            or len(self.api_key) < 8
        )
        if is_placeholder:
            self.last_status_message = "HINDSIGHT_API_KEY not set. Running in resilient local persistent memory mode."
            return

        try:
            self.client = Hindsight(
                base_url=self.base_url,
                api_key=self.api_key
            )
            # Try ensuring bank exists
            try:
                self.client.create_bank(
                    bank_id=self.bank_id,
                    name="Enterprise Deals"
                )
            except Exception:
                # Bank may already exist, which is expected
                pass

            self.cloud_active = True
            self.last_status_message = f"Connected to Hindsight Cloud (Bank: {self.bank_id})"
        except Exception as e:
            self.cloud_active = False
            self.last_status_message = f"Hindsight Cloud init failed: {e}. Using local persistent mirror."

    def _load_local_memories(self) -> List[Dict[str, Any]]:
        try:
            if LOCAL_MEMORY_FILE.exists():
                with open(LOCAL_MEMORY_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data.get("banks", {}).get(self.bank_id, [])
        except Exception as e:
            print(f"[Memory] Error loading local memories: {e}")
        return []

    def _save_local_memories(self, memories: List[Dict[str, Any]]):
        try:
            data = {
                "banks": {self.bank_id: memories},
                "updated_at": datetime.datetime.now().isoformat()
            }
            with open(LOCAL_MEMORY_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"[Memory] Error saving local memories: {e}")

    def retain(self, content: str, company: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Retains deal intelligence into persistent memory.
        Uses Hindsight Cloud retain() and simultaneously persists to local storage.
        """
        now = datetime.datetime.now()
        timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
        
        meta = metadata or {}
        if company:
            meta["company"] = company
        meta["timestamp"] = timestamp

        tags = [company.strip()] if company else ["General"]

        memory_record = {
            "id": f"mem_{uuid.uuid4().hex[:8]}",
            "content": content.strip(),
            "company": company.strip() if company else "General",
            "metadata": meta,
            "timestamp": timestamp,
            "synced_to_cloud": False
        }

        # 1. Hindsight Cloud retain
        if self.cloud_active and self.client:
            try:
                # Official Hindsight retain call
                # Convert string metadata to dict[str, str]
                str_metadata = {str(k): str(v) for k, v in meta.items()}
                self.client.retain(
                    bank_id=self.bank_id,
                    content=content,
                    timestamp=now,
                    tags=tags,
                    metadata=str_metadata
                )
                memory_record["synced_to_cloud"] = True
            except Exception as e:
                print(f"[Memory] Hindsight Cloud retain warning: {e}")

        # 2. Local mirror retain
        memories = self._load_local_memories()
        memories.append(memory_record)
        self._save_local_memories(memories)

        return memory_record

    def recall(self, query: str, company: Optional[str] = None, limit: int = 8) -> List[Dict[str, Any]]:
        """
        Recalls relevant memories for a given query and company.
        Queries Hindsight Cloud and complements with local mirror.
        """
        cloud_results: List[Dict[str, Any]] = []

        # 1. Hindsight Cloud recall
        if self.cloud_active and self.client:
            try:
                tags = [company.strip()] if company and company.lower() not in ["all", "general", ""] else None
                response = self.client.recall(
                    bank_id=self.bank_id,
                    query=query,
                    tags=tags
                )
                items = getattr(response, "results", response)
                if isinstance(items, list):
                    for item in items:
                        text = getattr(item, "text", None) or getattr(item, "content", None) or str(item)
                        item_meta = getattr(item, "metadata", {}) or {}
                        cloud_results.append({
                            "content": text,
                            "source": "Hindsight Cloud",
                            "metadata": item_meta,
                            "timestamp": getattr(item, "occurred_start", None) or datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        })
            except Exception as e:
                print(f"[Memory] Hindsight Cloud recall warning: {e}")

        # 2. Local mirror recall with intelligent filtering
        local_memories = self._load_local_memories()
        query_tokens = [w.lower() for w in re.findall(r'\w+', query)]
        company_filter = company.strip().lower() if company and company.lower() not in ["all", "general", ""] else None

        ranked = []
        for mem in local_memories:
            c_name = mem.get("company", "").lower()
            text = mem.get("content", "").lower()

            # Strict company filter if specified
            if company_filter:
                if company_filter != c_name and company_filter not in text:
                    continue

            # Calculate match score based on token frequency and company prominence
            score = 0
            if company_filter and (company_filter in text or company_filter == c_name):
                score += 5

            for token in query_tokens:
                if len(token) > 2 and token in text:
                    score += 1

            ranked.append((score, mem))

        # Sort by relevance score first, then timestamp descending
        ranked.sort(key=lambda x: (x[0], x[1].get("timestamp", "")), reverse=True)
        top_local = [item[1] for item in ranked[:limit]]

        # Merge results, removing exact duplicates
        combined = []
        seen = set()

        for cr in cloud_results:
            text = cr.get("content", "").strip()
            if text and text not in seen:
                seen.add(text)
                combined.append(cr)

        for lr in top_local:
            text = lr.get("content", "").strip()
            if text and text not in seen:
                seen.add(text)
                combined.append(lr)

        return combined

    def get_all_memories(self, company: Optional[str] = None) -> List[Dict[str, Any]]:
        """Returns all memories sorted chronologically."""
        memories = self._load_local_memories()
        if company and company.lower() not in ["all", "general", ""]:
            comp_lower = company.lower()
            memories = [
                m for m in memories
                if m.get("company", "").lower() == comp_lower or comp_lower in m.get("content", "").lower()
            ]
        return sorted(memories, key=lambda x: x.get("timestamp", ""))

    def clear_memories(self, company: Optional[str] = None):
        """Clears memory for a company or all companies."""
        if not company or company.lower() in ["all", "everything"]:
            self._save_local_memories([])
        else:
            comp_lower = company.lower()
            memories = self._load_local_memories()
            remaining = [
                m for m in memories
                if m.get("company", "").lower() != comp_lower and comp_lower not in m.get("content", "").lower()
            ]
            self._save_local_memories(remaining)


# Singleton accessor
_manager: Optional[MemoryManager] = None

def get_memory_manager() -> MemoryManager:
    global _manager
    if _manager is None:
        _manager = MemoryManager()
    return _manager

def retain_memory(content: str, company: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    return get_memory_manager().retain(content=content, company=company, metadata=metadata)

def recall_memory(query: str, company: Optional[str] = None, limit: int = 8) -> List[Dict[str, Any]]:
    return get_memory_manager().recall(query=query, company=company, limit=limit)

def get_all_memories(company: Optional[str] = None) -> List[Dict[str, Any]]:
    return get_memory_manager().get_all_memories(company=company)

def clear_memories(company: Optional[str] = None):
    return get_memory_manager().clear_memories(company=company)
