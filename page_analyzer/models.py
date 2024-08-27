from dataclasses import dataclass
from datetime import date


@dataclass
class Url:
    name: str
    created_at: date | None
    id: int | None


@dataclass
class Check:
    url_id: int
    status_code: int | None
    h1: str | None
    title: str | None
    description: str | None
    created_at: date
    id: int | None = None
