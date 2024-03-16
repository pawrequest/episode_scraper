from __future__ import annotations

from abc import ABC
from typing import Generator, TYPE_CHECKING

from aiohttp import ClientSession
import pawsupport.async_ps
from pawsupport.html_ps import TagSelectorABC

from .episode import EpisodeDC
from .selectors import DetailSoup, ListSoup, ListTag, PodSoup

if TYPE_CHECKING:
    pass


class ScraperABC(ABC):
    def __init__(
        self,
        url: str,
        http_session: ClientSession,
        selector_types: PodSoup,
    ):
        self.url = url
        self.http_session = http_session
        self.selectors = selector_types

    async def get_detail_page(self, url: str) -> DetailSoup:
        raise NotImplementedError

    async def get_list_page(self, url: str) -> ListSoup:
        raise NotImplementedError

    async def get_subpages(self, listpage: ListSoup) -> list[ListTag]:
        raise NotImplementedError

    def get_all_urls(self, main_selector: ListSoup) -> list[str]:
        raise NotImplementedError

    def episode_from_tags(self, selectors: tuple[TagSelectorABC, ...]) -> EpisodeDC:
        raise NotImplementedError

    async def go(self) -> Generator[EpisodeDC]:
        main_selector = await self.get_list_page(self.url)
        for url in self.get_all_urls(main_selector):
            list_page = await self.get_list_page(url)
            for ep_selectors in await self.get_episode_tags(list_page):
                episode = self.episode_from_tags(ep_selectors)
                yield episode

    async def get_episode_tags(self, listpage: ListSoup) -> list[tuple[TagSelectorABC, ...]]:
        raise NotImplementedError

    @quiet_cancel_as
    async def get_some_eps(self, limit: int = None) -> Generator[EpisodeDC]:
        ep_i = 0
        async for ep in self.go():
            if limit and ep_i >= limit:
                break
            ep_i += 1
            yield ep
