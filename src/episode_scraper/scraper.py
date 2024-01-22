from __future__ import annotations

from abc import ABC
from asyncio import Queue
from typing import TYPE_CHECKING

from aiohttp import ClientSession
from bs4 import Tag
from pawsupport.async_ps import quiet_cancel_as

from .episode import EpisodeDC

if TYPE_CHECKING:
    from .selectors.captivate import CaptivateDetailPageSelector, CaptivatePageSelector, CaptivateListingSelectorABC


class ScraperGeneral(ABC):
    def __init__(
        self,
        url: str,
        http_session: ClientSession,
        queue: Queue,
        listpage_selector: type(CaptivatePageSelector),
        listing_selector: type(CaptivateListingSelectorABC),
        detail_page_selector: type(CaptivateDetailPageSelector),
    ):
        self.url = url
        self.http_session = http_session
        self.queue = queue
        self.listpage_selector = listpage_selector
        self.detailpage_selector = detail_page_selector
        self.listing_selector = listing_selector

    async def all_in_one(self, use_q=True):
        main_selector = await self.listpage_selector.from_url(self.url, self.http_session)
        urls = main_selector.listing_pages
        for listing_page in urls:
            page_selector = await self.listpage_selector.from_url(listing_page, self.http_session)
            for listing_tag in page_selector.listings:
                listing = self.listing_selector(listing_tag)
                detail = await self.detailpage_selector.from_url(listing.url, self.http_session)
                episode = EpisodeDC.from_selectors(listing, detail)
                if use_q:
                    await self.queue.put(episode)
                else:
                    yield episode

    @quiet_cancel_as
    async def run(self) -> None:
        main_selector = await self.listpage_selector.from_url(self.url, self.http_session)
        urls = main_selector.listing_pages
        for url in urls:
            ep = await self.get_and_q(url)
            await self.queue.put(ep)

    async def get_and_q(self, url: str) -> EpisodeDC:
        page_selector = await self.listpage_selector.from_url(url, self.http_session)
        for listing_tag in page_selector.listings:
            return await self.ep_from_list_tag(listing_tag)

    async def ep_from_list_tag(self, listing_tag: Tag):
        listing = self.listing_selector(listing_tag)
        detail = await self.detailpage_selector.from_url(listing.url, self.http_session)
        return EpisodeDC.from_selectors(listing, detail)

    async def get_some_eps(self, limit: int = 0):
        ep_i = 0
        async for ep in self.all_in_one(use_q=False):
            if limit and ep_i >= limit:
                break
            ep_i += 1
            yield ep
