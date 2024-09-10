from dataclasses import dataclass
from datetime import date


@dataclass
class Table:
    """Dataclass representing table cells types"""
    id: type = int
    status_code: type = int
    h1: type = str
    title: type = str
    description: type = str
    creation_date: type = date
    last_check: type = date
    url_name: type = str


CheckTableRow = tuple[
    Table.id,
    Table.status_code,
    Table.h1 | None,
    Table.title | None,
    Table.description | None,
    Table.creation_date
]

UrlTableRow = tuple[
    Table.id,
    Table.url_name,
    Table.creation_date
]

UrlLastCheckTableRow = tuple[
    Table.id,
    Table.url_name,
    Table.last_check | None,
    Table.status_code
]
