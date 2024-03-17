from __future__ import annotations

from datetime import datetime
from typing import Protocol


# class ListingProtocol(Protocol):
#     ep_number: str
#     ep_date: str
#     ep_url: str
#     ep_title: str
#
#
# class DetailProtocol(Protocol):
#     ep_notes: list[str]
#     ep_links: dict[str, str]


class EP_PROT(Protocol):
    title: str
    date: datetime
    notes: list
    links: dict
    url: str
