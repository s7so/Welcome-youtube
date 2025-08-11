from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, Dict, Any, Optional, List, Set

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
    def __init__(
        self,
        db_url: Optional[str],
        query: Optional[str],
        table: Optional[str] = None,
        col_emp: Optional[str] = None,
        col_time: Optional[str] = None,
        col_type: Optional[str] = None,
        in_values: Optional[Set[str]] = None,
        out_values: Optional[Set[str]] = None,
    ) -> None:
        self.db_url = db_url
        self.query = query
        self.table = table
        self.col_emp = col_emp
        self.col_time = col_time
        self.col_type = col_type
        self._engine: Optional[Engine] = None
        self.in_values = {v.strip().upper() for v in (in_values or set())}
        self.out_values = {v.strip().upper() for v in (out_values or set())}

    def connect(self) -> None:
        if not self.db_url:
            raise ConnectionError("FingerTec DB URL not configured")
        if create_engine is None:
            raise ConnectionError("SQLAlchemy not available. Install requirements.")
        self._engine = create_engine(self.db_url)
        # test connection
        with self._engine.connect() as conn:
            conn.execute(text("SELECT 1"))

    def _build_query_if_needed(self) -> Optional[str]:
        if self.query:
            return self.query
        if self.table and self.col_emp and self.col_time:
            # type column may be None
            projections = [
                f"{self.col_emp} as employee_id",
                f"{self.col_time} as timestamp",
            ]
            if self.col_type:
                projections.append(f"{self.col_type} as type")
            proj = ", ".join(projections)
            return (
                f"SELECT {proj} FROM {self.table} "
                f"WHERE {self.col_time} > :since ORDER BY {self.col_time} ASC"
            )
        return None

    def _map_type(self, raw_type: Any) -> str:
        if raw_type is None:
            return "IN"
        val = str(raw_type).strip().upper()
        if self.in_values and val in self.in_values:
            return "IN"
        if self.out_values and val in self.out_values:
            return "OUT"
        # Fallbacks
        if val in {"IN", "I", "0"}:
            return "IN"
        if val in {"OUT", "O", "1"}:
            return "OUT"
        return "IN"

    def fetch_logs_since(self, since: datetime) -> Iterable[Dict[str, Any]]:
        if not self._engine:
            raise ConnectionError("DBAdapter not connected")
        sql = self._build_query_if_needed()
        if not sql:
            # No query and insufficient metadata: return empty
            return []
        rows: List[Dict[str, Any]] = []
        with self._engine.connect() as conn:
            result = conn.execute(text(sql), {"since": since})
            for row in result.mappings():
                employee_id = str(row.get("employee_id"))
                ts = row.get("timestamp")
                if isinstance(ts, datetime):
                    timestamp = ts
                else:
                    try:
                        timestamp = datetime.fromisoformat(str(ts))
                    except Exception:
                        continue
                raw_type = row.get("type")
                log_type = self._map_type(raw_type)
                rows.append(
                    {
                        "employee_id": employee_id,
                        "timestamp": timestamp,
                        "type": log_type,
                    }
                )
        return rows


def create_adapter_from_settings(django_settings) -> FingerTecAdapter:
    mode = str(getattr(django_settings, "FINGERTEC_MODE", "db")).lower()
    if mode == "sdk":
        return SDKAdapter(
            ip=getattr(django_settings, "FINGERTEC_IP", None),
            port=int(getattr(django_settings, "FINGERTEC_PORT", 0) or 0) or None,
        )
    # default: db
    in_values = set(
        (getattr(django_settings, "FINGERTEC_DB_TYPE_IN_VALUES", "IN,I,0")).split(",")
    )
    out_values = set(
        (getattr(django_settings, "FINGERTEC_DB_TYPE_OUT_VALUES", "OUT,O,1")).split(",")
    )
    return DBAdapter(
        db_url=getattr(django_settings, "FINGERTEC_DB_URL", None),
        query=getattr(django_settings, "FINGERTEC_DB_QUERY", None),
        table=getattr(django_settings, "FINGERTEC_DB_TABLE", None),
        col_emp=getattr(django_settings, "FINGERTEC_DB_COL_EMP", None),
        col_time=getattr(django_settings, "FINGERTEC_DB_COL_TIME", None),
        col_type=getattr(django_settings, "FINGERTEC_DB_COL_TYPE", None),
        in_values=in_values,
        out_values=out_values,
    )