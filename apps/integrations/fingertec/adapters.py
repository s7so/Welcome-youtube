from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, Dict, Any, Optional, List

from django.conf import settings

try:
    from sqlalchemy import create_engine, text
    from sqlalchemy.engine import Engine
except Exception:  # pragma: no cover
    create_engine = None  # type: ignore
    Engine = object  # type: ignore


class ConnectionError(Exception):
    pass


@dataclass
class LogRecord:
    employee_id: str
    timestamp: datetime
    type: str  # 'IN' or 'OUT'


class FingerTecAdapter:
    def connect(self) -> None:  # pragma: no cover - interface
        raise NotImplementedError

    def fetch_logs_since(self, since: datetime) -> Iterable[Dict[str, Any]]:  # pragma: no cover - interface
        raise NotImplementedError


class SDKAdapter(FingerTecAdapter):
    def __init__(self, ip: Optional[str], port: Optional[int]) -> None:
        self.ip = ip
        self.port = port
        self.connected = False

    def connect(self) -> None:
        if not self.ip or not self.port:
            raise ConnectionError("FingerTec SDK connection not configured")
        # TODO: Implement actual SDK connection
        self.connected = True

    def fetch_logs_since(self, since: datetime) -> Iterable[Dict[str, Any]]:
        # TODO: Implement actual SDK fetching
        return []


class DBAdapter(FingerTecAdapter):
    def __init__(self, db_url: Optional[str], query: Optional[str]) -> None:
        self.db_url = db_url
        self.query = query
        self._engine: Optional[Engine] = None

    def connect(self) -> None:
        if not self.db_url:
            raise ConnectionError("FingerTec DB URL not configured")
        if create_engine is None:
            raise ConnectionError("SQLAlchemy not available. Install requirements.")
        self._engine = create_engine(self.db_url)
        # test connection
        with self._engine.connect() as conn:
            conn.execute(text("SELECT 1"))

    def fetch_logs_since(self, since: datetime) -> Iterable[Dict[str, Any]]:
        if not self._engine:
            raise ConnectionError("DBAdapter not connected")
        if not self.query:
            # As a safe default, return empty without a configured query
            return []
        rows: List[Dict[str, Any]] = []
        with self._engine.connect() as conn:
            result = conn.execute(text(self.query), {"since": since})
            for row in result.mappings():
                # Expect columns: employee_id, timestamp, type (optional)
                employee_id = str(row.get("employee_id"))
                ts = row.get("timestamp")
                if isinstance(ts, datetime):
                    timestamp = ts
                else:
                    # attempt to parse if string; else skip
                    try:
                        timestamp = datetime.fromisoformat(str(ts))
                    except Exception:
                        continue
                log_type = str(row.get("type") or "IN").upper()
                if log_type not in ("IN", "OUT"):
                    log_type = "IN"
                rows.append({
                    "employee_id": employee_id,
                    "timestamp": timestamp,
                    "type": log_type,
                })
        return rows


def create_adapter_from_settings(django_settings) -> FingerTecAdapter:
    mode = str(getattr(django_settings, "FINGERTEC_MODE", "db")).lower()
    if mode == "sdk":
        return SDKAdapter(
            ip=getattr(django_settings, "FINGERTEC_IP", None),
            port=int(getattr(django_settings, "FINGERTEC_PORT", 0) or 0) or None,
        )
    # default: db
    return DBAdapter(
        db_url=getattr(django_settings, "FINGERTEC_DB_URL", None),
        query=getattr(django_settings, "FINGERTEC_DB_QUERY", None),
    )