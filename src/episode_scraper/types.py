from __future__ import annotations

from typing import Protocol


class ListingProtocol(Protocol):
    ep_number: str
    ep_date: str
    ep_url: str
    ep_title: str


class DetailProtocol(Protocol):
    ep_notes: list[str]
    ep_links: dict[str, str]
