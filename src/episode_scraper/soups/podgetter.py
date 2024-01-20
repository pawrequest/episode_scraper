from __future__ import annotations

from asyncio import Queue

from aiohttp import ClientSession
from pawsupport import quiet_cancel_as

from ..episode_dc import EpisodeDC
from .funcs import ep_from_proto
from .selectors import DetailPageSelector, ListPageSelector, ListingSelector


class PodGetter:
    def __init__(self, url: str, http_session: ClientSession, queue: Queue):
        self.url = url
        self.http_session = http_session
        self.queue = queue

    @quiet_cancel_as
    async def run(self) -> None:
        main_selector = await ListPageSelector.from_url(self.url, self.http_session)
        urls = main_selector.listing_pages
        for url in urls:
            await self._get_queue_listings(url)

    async def _get_queue_listings(self, url: str) -> None:
        page_selector = await ListPageSelector.from_url(url, self.http_session)
        for listing_tag in page_selector.listings:
            await self._queue_listing(listing_tag)

    async def _queue_listing(self, listing_tag) -> None:
        listing = ListingSelector(listing_tag)
        detail = await DetailPageSelector.from_url(listing.ep_url, self.http_session)
        episode: EpisodeDC = await ep_from_proto(listing, detail)
        await self.queue.put(episode)
