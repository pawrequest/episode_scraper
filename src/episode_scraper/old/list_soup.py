""" Scrape website for new episodes """

from __future__ import annotations

from typing import AsyncGenerator

from aiohttp import ClientSession as ClientSession
from bs4 import BeautifulSoup
from pawsupport import response_

from episode_scraper.soups.funcs import ep_from_tag
from episode_scraper.episode_dc import EpisodeDC


class ListingSoup(BeautifulSoup):
    """BeautifulSoup extended to parse listing page"""

    def __init__(self, markup: str, url, parser: str = "html.parser"):
        super().__init__(markup, parser)
        self.listing_eps = list()
        self.listing_page_url = url

    async def episode_stream(self) -> AsyncGenerator[EpisodeDC, None]:
        """Yield EpisodeDC objects for each episode on this listing page"""
        for ep_tag in self.select(".episode"):
            yield await ep_from_tag(ep_tag)

    @classmethod
    async def from_url(cls, url: str, http_session: ClientSession):
        html = await response_(url, http_session)
        return cls(html, url)


def _listing_page_strs(main_url: str, num_pages: int) -> list[str]:
    """Construct list of listing page urls from main url and number of pages"""
    # not async so we scrape in reverse chronological order and can abort on duplicates
    return [main_url + f"/episodes/{_ + 1}/#showEpisodes" for _ in range(num_pages)]
