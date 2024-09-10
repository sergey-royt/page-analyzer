"""Custom types to annotate data from database"""

from datetime import date


Id = int
StatusCode = int
H1 = str
Title = str
Description = str
CreationDate = date
LastCheck = date
UrlName = str

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
