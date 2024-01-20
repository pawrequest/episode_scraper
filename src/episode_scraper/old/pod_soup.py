from __future__ import annotations

from asyncio import Queue
from typing import AsyncGenerator

from aiohttp import ClientSession as ClientSession
from bs4 import BeautifulSoup
from loguru import logger
from pawsupport import response_

from episode_scraper.old.list_soup import ListingSoup, _listing_page_strs


class PodcastSoup(BeautifulSoup):
    def __init__(
        self,
        markup: str,
        podcast_url,
        queue: Queue,
        http_session: ClientSession = None,
        parser: str = "html.parser",
    ):
        super().__init__(markup, parser)
        self.podcast_url = podcast_url
        self.listing_pages = list()
        self.http_session = http_session or ClientSession()
        self.queue = queue

    @classmethod
    async def from_url(cls, url: str, http_session: ClientSession, queue: Queue):
        html = await response_(url, http_session)
        pod_soup = cls(html, url, queue, http_session)
        num_pgs = pod_soup._num_pages
        pod_soup.listing_pages = _listing_page_strs(url, num_pgs)
        return pod_soup

    async def episode_stream_q(self) -> None:
        async for listing_soup in self.listing_soups():
            async for ep in listing_soup.episode_stream():
                await self.queue.put(ep)

    async def listing_soups(self) -> AsyncGenerator[ListingSoup, None]:
        """Yield ListingSoup object for each listing page"""
        for listing_page in self.listing_pages:
            logger.debug(f"listing page {listing_page}", bot_name="Scraper")
            listing_page_soup = await ListingSoup.from_url(listing_page, self.http_session)
            yield listing_page_soup

    @property
    def _num_pages(self) -> int:
        """Get number of pages of listings from pagination controls on mainpage"""
        page_links = self.select(".page-link")
        lastpage = page_links[-1]["href"]
        num_pages = lastpage.split("/")[-1].split("#")[0]
        return int(num_pages)
