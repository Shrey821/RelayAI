"""
UMS Local Vault - SQLite Persistence Engine
Allows storing personas, versioned snapshots, and migration audit logs locally.
"""

from __future__ import annotations
import sqlite3
import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from server.models import UMSPayload

DEFAULT_DB_PATH = os.path.join(os.path.dirname(__file__), "..", "ums_vault.db")

class UMSVault:
    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self.db_path = os.path.abspath(db_path)
        self._init_db()

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._get_conn() as conn:
            cursor = conn.cursor()
            # Profiles table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS profiles (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    source_provider TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    payload_json TEXT NOT NULL
                )
            """)
            # Snapshots table (for version history & rollbacks)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    profile_id TEXT NOT NULL,
                    version_num INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    description TEXT,
                    payload_json TEXT NOT NULL,
                    FOREIGN KEY (profile_id) REFERENCES profiles(id) ON DELETE CASCADE
                )
            """)
            # Migration audit log
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS migration_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    profile_id TEXT NOT NULL,
                    source_provider TEXT NOT NULL,
                    target_provider TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    retention_score REAL NOT NULL,
                    items_total INTEGER NOT NULL,
                    items_learned INTEGER NOT NULL,
                    items_adapted INTEGER NOT NULL,
                    items_filtered INTEGER NOT NULL,
                    diff_json TEXT NOT NULL
                )
            """)
            conn.commit()

    def save_profile(self, payload: UMSPayload, description: str = "Update") -> str:
        data = payload.to_dict()
        profile_id = payload.metadata.id
        name = payload.metadata.name or "Untitled Persona"
        source = payload.metadata.source_provider or "generic"
        now = datetime.now(timezone.utc).isoformat()
        payload.metadata.updated_at = now

        payload_json = json.dumps(payload.to_dict(), indent=2)

        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO profiles (id, name, source_provider, created_at, updated_at, payload_json)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    name=excluded.name,
                    source_provider=excluded.source_provider,
                    updated_at=excluded.updated_at,
                    payload_json=excluded.payload_json
            """, (profile_id, name, source, payload.metadata.created_at, now, payload_json))

            # Calculate next version number for snapshot
            cursor.execute("SELECT COALESCE(MAX(version_num), 0) + 1 FROM snapshots WHERE profile_id = ?", (profile_id,))
            next_ver = cursor.fetchone()[0]

            cursor.execute("""
                INSERT INTO snapshots (profile_id, version_num, created_at, description, payload_json)
                VALUES (?, ?, ?, ?, ?)
            """, (profile_id, next_ver, now, description, payload_json))

            conn.commit()
        return profile_id

    def get_profile(self, profile_id: str) -> Optional[UMSPayload]:
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT payload_json FROM profiles WHERE id = ?", (profile_id,))
            row = cursor.fetchone()
            if not row:
                return None
            data = json.loads(row["payload_json"])
            return UMSPayload.from_dict(data)

    def list_profiles(self) -> List[Dict[str, Any]]:
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, source_provider, created_at, updated_at
                FROM profiles ORDER BY updated_at DESC
            """)
            return [dict(row) for row in cursor.fetchall()]

    def delete_profile(self, profile_id: str) -> bool:
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM profiles WHERE id = ?", (profile_id,))
            conn.commit()
            return cursor.rowcount > 0

    def log_migration(self, profile_id: str, source: str, target: str, diff_result: Dict[str, Any]) -> int:
        now = datetime.now(timezone.utc).isoformat()
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO migration_logs (
                    profile_id, source_provider, target_provider, timestamp,
                    retention_score, items_total, items_learned, items_adapted, items_filtered, diff_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                profile_id,
                source,
                target,
                now,
                diff_result.get("retention_score", 0.0),
                diff_result.get("items_total", 0),
                diff_result.get("items_learned", 0),
                diff_result.get("items_adapted", 0),
                diff_result.get("items_filtered", 0),
                json.dumps(diff_result)
            ))
            conn.commit()
            return cursor.lastrowid

    def get_migration_logs(self, profile_id: Optional[str] = None) -> List[Dict[str, Any]]:
        with self._get_conn() as conn:
            cursor = conn.cursor()
            if profile_id:
                cursor.execute("""
                    SELECT * FROM migration_logs WHERE profile_id = ? ORDER BY timestamp DESC LIMIT 50
                """, (profile_id,))
            else:
                cursor.execute("SELECT * FROM migration_logs ORDER BY timestamp DESC LIMIT 50")
            rows = cursor.fetchall()
            results = []
            for r in rows:
                item = dict(r)
                item["diff"] = json.loads(item["diff_json"])
                del item["diff_json"]
                results.append(item)
            return results
