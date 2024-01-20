from __future__ import annotations

from asyncio import Queue

from aiohttp import ClientSession as ClientSession
from bs4 import BeautifulSoup
from pawsupport import response_

from episode_scraper.soups.selectors import ListPageSelector


class Podcast:
    def __init__(self, url: str, http_session: ClientSession, queue: Queue, page_sel=ListPageSelector):
        self.url = url
        self.http_session = http_session
        self.queue = queue
        self.page_selector = page_sel

    async def go(self):
        main_soup = await ListPageSoup.from_url(self.url, self.http_session)
        pages = main_soup.listing_pages
        for page in pages:
            list_page_soup = ListPageSoup.from_url(page, self.http_session)
            async for listing in list_page_soup.listings:
                await self.queue.put(listing)

    async def episode_stream_q(self) -> None:
        async for listing_soup in self.listing_page_selectors():
            async for ep in listing_soup.episode_stream():
                await self.queue.put(ep)

    async def listing_page_selectors(self):
        for listing_page in self.page_selector.listing_pages:
            page_markup = await response_(listing_page, self.http_session)
            listing_page_soup = BeautifulSoup(page_markup, "html.parser")
            selector = ListPageSelector(listing_page_soup, listing_page)
            yield selector


class ListPageSoup(BeautifulSoup, ListPageSelector):
    @classmethod
    async def from_url(cls, url: str, http_session) -> ListPageSoup:
        html = await response_(url, http_session)
        return cls(html, "html.parser")
