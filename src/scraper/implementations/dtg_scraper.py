from __future__ import annotations

"""
some stiff
"""

from aiohttp import ClientSession
from dateutil.parser import parse

from ..episode import EpisodeDC
from ..scrape import ScraperABC
from ..selectors import PodSoup
from .dtg_selectors import DTGDetailPage, DTGListPage, DTGListTag


class DTGSelectors(PodSoup):
    """
    Decoding The Gurus Podcast selectors
    """

    def __init__(self):
        super().__init__(
            DTGListPage,
            DTGListTag,
            DTGDetailPage,
        )


class DTGScraper(ScraperABC):
    """
    Decoding The Gurus Podcast scraper
    """

    def __init__(self, url: str, http_session: ClientSession):
        super().__init__(
            url,
            http_session,
            DTGSelectors(),
        )

    async def get_detail_page(self, url: str) -> DTGDetailPage:
        return await DTGDetailPage.from_url(url, self.http_session)

    async def get_list_page(self, url: str) -> DTGListPage:
        try:
            return await DTGListPage.from_url(url, self.http_session)
        except Exception as e:
            print(f"Error getting {url}: {e}")
            raise e

    async def get_subpages(self, listpage: DTGListPage) -> list[DTGListTag]:
        return [DTGListTag.from_bs4(_) for _ in listpage.select(".episode")]
        # return listpage.subpage_selectors
        # return listpage.subpage_selectors

    def get_all_urls(self, listpage: DTGListPage) -> list[str]:
        return listpage.get_all_urls

    async def get_episode_tags(self, listpage: DTGListPage) -> list[tuple[DTGListTag, DTGDetailPage]]:
        return [(listing, await self.get_detail_page(listing.ep_url)) for listing in await self.get_subpages(listpage)]

    def episode_from_tags(self, selectors: tuple[DTGListTag, DTGDetailPage]) -> EpisodeDC:
        date = parse(selectors[0].ep_date)
        return EpisodeDC(
            title=selectors[0].ep_title,
            url=selectors[0].ep_url,
            episode_number=selectors[0].ep_number,
            date=date,
            notes=selectors[1].ep_notes,
            links=selectors[1].ep_links,
        )
