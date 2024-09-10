from datetime import date
from typing import NewType


Id = NewType('Id', int)
StatusCode = NewType('StatusCode', int)
H1 = NewType('H1', str)
Title = NewType('Title', str)
Description = NewType('Description', str)
CreationDate = NewType('CreationDate', date)
LastCheck = NewType('LastCheck', date)
UrlName = NewType('UrlName', str)

CheckTableRow = tuple[
    Id,
    StatusCode,
    H1 | None,
    Title | None,
    Description | None,
    CreationDate
]

UrlTableRow = tuple[
    Id,
    UrlName,
    CreationDate
]

UrlLastCheckTableRow = tuple[
    Id,
    UrlName,
    LastCheck | None,
    StatusCode
]
