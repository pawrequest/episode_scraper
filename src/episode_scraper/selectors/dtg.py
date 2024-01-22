from __future__ import annotations, annotations

from asyncio import Queue
from typing import TYPE_CHECKING

from aiohttp import ClientSession

from .captivate import CaptivateDetailPageSelector, CaptivateListingSelectorABC
from .captivate import CaptivatePageSelector
from ..scraper import ScraperGeneral


class DTGScraper(ScraperGeneral):
    def __init__(self, url: str, http_session: ClientSession, queue: Queue):
        super().__init__(
            url,
            http_session,
            queue,
            CaptivatePageSelector,
            DTGListingSelector,
            DTGDetailPageSelector,
        )


class DTGDetailPageSelector(CaptivateDetailPageSelector):
    @property
    def notes(self) -> list[str]:
        paragraphs = self.tag.select(".show-notes p")
        return [p.text for p in paragraphs if p.text != "Links"]

    @property
    def links(self) -> dict[str, str]:
        show_links_html = self.tag.select(".show-notes a")
        return {_.text: _["href"] for _ in show_links_html}


class DTGListingSelector(CaptivateListingSelectorABC):
    """Extract information from listing subsection of list page"""

    @property
    def number(self) -> str:
        """string because 'bonus' episodes are not numbered"""
        res = self.select_text(".episode-info").split()[1]
        return str(res)

    @property
    def date(self) -> str:
        return self.select_text(".publish-date")

    @property
    def url(self) -> str:
        return self.select_link(".episode-title a")

    @property
    def title(self) -> str:
        return self.select_text(".episode-title")
