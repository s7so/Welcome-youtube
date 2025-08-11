from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterable, List, Dict, Any


class ConnectionError(Exception):
    pass


@dataclass
class FingerTecLog:
    employee_id: str
    timestamp: datetime
    type: str  # 'IN' or 'OUT'


class FingerTecClient:
    def __init__(self, ip: str, port: int, timeout: float = 5.0) -> None:
        self.ip = ip
        self.port = port
        self.timeout = timeout
        self.connected = False

    def connect(self) -> None:
        # TODO: Replace with actual SDK connection logic
        if not self.ip or not self.port:
            raise ConnectionError("Invalid device configuration")
        self.connected = True

    def get_new_logs(self, since: datetime) -> Iterable[Dict[str, Any]]:
        # TODO: Replace with actual SDK fetch logic
        # For now, return an empty list to avoid side effects
        return []

    @staticmethod
    def parse(raw: Dict[str, Any]) -> FingerTecLog:
        return FingerTecLog(
            employee_id=str(raw.get("employee_id")),
            timestamp=raw.get("timestamp"),
            type=str(raw.get("type", "IN")),
        )