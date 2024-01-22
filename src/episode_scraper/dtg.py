from __future__ import annotations

from asyncio import Queue

from aiohttp import ClientSession

from episode_scraper import ScraperGeneral
from episode_scraper.selectors import DTGListingSelector
from episode_scraper.selectors.captivate import CaptivatePageSelector
from episode_scraper.selectors.dtg import DTGDetailPageSelector


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
