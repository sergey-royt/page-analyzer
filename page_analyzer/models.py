from dataclasses import dataclass
from datetime import date


@dataclass
class Check:
    """Dataclass representing check"""
    url_id: int | None = None
    status_code: int | None = None
    h1: str | None = None
    title: str | None = None
    description: str | None = None
    created_at: date | None = None
    id: int | None = None


@dataclass
class Url:
    """Dataclass representing url"""
    name: str
    id: int
    created_at: date | None = None
