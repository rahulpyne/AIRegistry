"""
Storage abstraction for the AI Registry.

One interface, three backends:
    * SupabaseStore  - primary (used when SUPABASE_URL + SUPABASE_KEY are set)
    * LocalJSONStore - zero-config dev/seed fallback (JSON files under ./data)
    * CosmosStore     - documented stub for the later Azure migration

Swapping Supabase -> Cosmos later is a single class, because every backend
implements the same methods:

    save_entry / list_entries / get_entry
    save_document / list_documents / update_document_status
    set_approval / list_approvals

Entries are stored as JSON documents keyed by a string id (`entryId` in Cosmos
terms). A few columns are extracted alongside the JSON payload purely to make
filtering/listing cheap; the payload remains the source of truth.
"""
from __future__ import annotations

import os
import json
import uuid
import logging
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_id(prefix: str = "IDEA") -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"{prefix}-{stamp}-{uuid.uuid4().hex[:6].upper()}"


# Columns lifted out of the JSON payload for cheap listing/filtering.
_EXTRACTED = ("title", "organization", "business_area",
              "lifecycle_phase", "status", "data_classification")


def _extract_columns(payload: dict) -> dict:
    return {
        "title":               payload.get("use_case_title") or payload.get("title", ""),
        "organization":        payload.get("rda_organization") or payload.get("organization", ""),
        "business_area":       payload.get("business_area", ""),
        "lifecycle_phase":     payload.get("lifecycle_phase", ""),
        "status":              payload.get("status", ""),
        "data_classification": payload.get("data_classification", ""),
    }


# ---------------------------------------------------------------------------
# Local JSON store (default fallback)
# ---------------------------------------------------------------------------
class LocalJSONStore:
    """File-backed store. Each collection is one JSON file under ./data."""

    def __init__(self, data_dir: str = "./data"):
        self.dir = Path(data_dir)
        self.dir.mkdir(parents=True, exist_ok=True)
        self._files = {
            "entries":   self.dir / "registry_entries.json",
            "documents": self.dir / "documents.json",
            "approvals": self.dir / "approvals.json",
        }
        for f in self._files.values():
            if not f.exists():
                f.write_text("[]", encoding="utf-8")

    def _read(self, name: str) -> list:
        return json.loads(self._files[name].read_text(encoding="utf-8"))

    def _write(self, name: str, rows: list) -> None:
        self._files[name].write_text(
            json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")

    # --- entries ---
    def save_entry(self, payload: dict, entry_id: str | None = None) -> dict:
        rows = self._read("entries")
        entry_id = entry_id or payload.get("id") or new_id()
        record = {
            "id": entry_id,
            "created_at": _now(),
            "payload": payload,
            **_extract_columns(payload),
        }
        rows = [r for r in rows if r["id"] != entry_id]
        rows.append(record)
        self._write("entries", rows)
        return record

    def list_entries(self) -> list:
        return sorted(self._read("entries"),
                      key=lambda r: r.get("created_at", ""), reverse=True)

    def get_entry(self, entry_id: str) -> dict | None:
        return next((r for r in self._read("entries") if r["id"] == entry_id), None)

    # --- documents ---
    def save_document(self, entry_id: str, phase: int, artifact: str,
                      file_name: str, storage_path: str) -> dict:
        rows = self._read("documents")
        record = {
            "id": uuid.uuid4().hex,
            "entry_id": entry_id,
            "phase": phase,
            "artifact": artifact,
            "file_name": file_name,
            "storage_path": storage_path,
            "status": "UPLOADED",
            "uploaded_at": _now(),
            "reviewed_at": None,
        }
        rows.append(record)
        self._write("documents", rows)
        return record

    def list_documents(self, entry_id: str) -> list:
        return [r for r in self._read("documents") if r["entry_id"] == entry_id]

    def update_document_status(self, doc_id: str, status: str) -> dict | None:
        rows = self._read("documents")
        updated = None
        for r in rows:
            if r["id"] == doc_id:
                r["status"] = status
                r["reviewed_at"] = _now() if status != "UPLOADED" else None
                updated = r
        self._write("documents", rows)
        return updated

    # --- approvals ---
    def set_approval(self, entry_id: str, phase: int, team: str,
                     status: str, approver: str = "") -> dict:
        rows = self._read("approvals")
        rows = [r for r in rows
                if not (r["entry_id"] == entry_id and r["phase"] == phase and r["team"] == team)]
        record = {
            "id": uuid.uuid4().hex,
            "entry_id": entry_id,
            "phase": phase,
            "team": team,
            "status": status,
            "approver": approver,
            "decided_at": _now() if status == "APPROVED" else None,
        }
        rows.append(record)
        self._write("approvals", rows)
        return record

    def list_approvals(self, entry_id: str) -> list:
        return [r for r in self._read("approvals") if r["entry_id"] == entry_id]


# ---------------------------------------------------------------------------
# Supabase store (primary)
# ---------------------------------------------------------------------------
class SupabaseStore:
    def __init__(self, url: str, key: str):
        from supabase import create_client  # lazy import so app runs without the SDK
        self.client = create_client(url, key)
        self.t_entries = os.environ.get("SUPABASE_TABLE_ENTRIES", "registry_entries")
        self.t_docs = os.environ.get("SUPABASE_TABLE_DOCUMENTS", "documents")
        self.t_appr = os.environ.get("SUPABASE_TABLE_APPROVALS", "approvals")
        self.bucket = os.environ.get("SUPABASE_BUCKET", "airegistry-documents")

    # --- entries ---
    def save_entry(self, payload: dict, entry_id: str | None = None) -> dict:
        entry_id = entry_id or payload.get("id") or new_id()
        record = {
            "id": entry_id,
            "created_at": _now(),
            "payload": payload,
            **_extract_columns(payload),
        }
        self.client.table(self.t_entries).upsert(record).execute()
        return record

    def list_entries(self) -> list:
        res = (self.client.table(self.t_entries)
               .select("*").order("created_at", desc=True).execute())
        return res.data or []

    def get_entry(self, entry_id: str) -> dict | None:
        res = (self.client.table(self.t_entries)
               .select("*").eq("id", entry_id).limit(1).execute())
        return (res.data or [None])[0]

    # --- documents ---
    def save_document(self, entry_id: str, phase: int, artifact: str,
                      file_name: str, storage_path: str) -> dict:
        record = {
            "id": uuid.uuid4().hex,
            "entry_id": entry_id,
            "phase": phase,
            "artifact": artifact,
            "file_name": file_name,
            "storage_path": storage_path,
            "status": "UPLOADED",
            "uploaded_at": _now(),
            "reviewed_at": None,
        }
        self.client.table(self.t_docs).insert(record).execute()
        return record

    def list_documents(self, entry_id: str) -> list:
        res = (self.client.table(self.t_docs)
               .select("*").eq("entry_id", entry_id).execute())
        return res.data or []

    def update_document_status(self, doc_id: str, status: str) -> dict | None:
        patch = {"status": status,
                 "reviewed_at": _now() if status != "UPLOADED" else None}
        res = (self.client.table(self.t_docs)
               .update(patch).eq("id", doc_id).execute())
        return (res.data or [None])[0]

    # --- approvals ---
    def set_approval(self, entry_id: str, phase: int, team: str,
                     status: str, approver: str = "") -> dict:
        record = {
            "id": uuid.uuid4().hex,
            "entry_id": entry_id,
            "phase": phase,
            "team": team,
            "status": status,
            "approver": approver,
            "decided_at": _now() if status == "APPROVED" else None,
        }
        # upsert on the natural key (entry_id, phase, team)
        self.client.table(self.t_appr).upsert(
            record, on_conflict="entry_id,phase,team").execute()
        return record

    def list_approvals(self, entry_id: str) -> list:
        res = (self.client.table(self.t_appr)
               .select("*").eq("entry_id", entry_id).execute())
        return res.data or []


# ---------------------------------------------------------------------------
# Cosmos store (later Azure migration — stub mirroring the same interface)
# ---------------------------------------------------------------------------
class CosmosStore:  # pragma: no cover - documented for the later migration
    """Drop-in replacement for SupabaseStore when moving to Azure Cosmos DB.

    Containers (partition key `entryId`):
        registry_entries / documents / approvals
    Implement the same eight methods using azure.cosmos.CosmosClient, mirroring
    pacifican-bsp/cosmos_client.py. Files move to Azure Blob Storage.
    """
    def __init__(self, *_, **__):
        raise NotImplementedError("CosmosStore is a placeholder for the Azure migration.")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------
def get_store():
    url = os.environ.get("SUPABASE_URL", "").strip()
    key = os.environ.get("SUPABASE_KEY", "").strip()
    if url and key:
        try:
            logger.info("Storage backend: Supabase")
            return SupabaseStore(url, key)
        except Exception:
            logger.exception("Supabase init failed — falling back to LocalJSONStore")
    logger.info("Storage backend: LocalJSONStore (./data)")
    return LocalJSONStore(os.environ.get("DATA_DIR", "./data"))
