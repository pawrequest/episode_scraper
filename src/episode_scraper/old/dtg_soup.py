""" Scrape website for new episodes """

from __future__ import annotations

from aiohttp import ClientSession as ClientSession
from bs4 import BeautifulSoup
from loguru import logger
from pawsupport import response_

from episode_scraper.old.list_soup import ListingSoup
from episode_scraper.old.pod_soup import PodcastSoup
from episode_scraper.soups.selectors import TagSelector


class DTGSoup(PodcastSoup):
    ...


class DTGListing(ListingSoup):
    ...


class EpisodeDetailsSoup(BeautifulSoup):
    """BeautifulSoup extended to parse episode details page"""

    def __init__(self, markup: str, parser: str = "html.parser", url=None):
        super().__init__(markup, parser)
        self.episode_url = url

    @property
    def episode_notes(self):
        paragraphs = self.select(".show-notes p")
        show_notes = [p.text for p in paragraphs if p.text != "Links"]

        return show_notes or None

    @property
    def episode_links(self):
        show_links_html = self.select(".show-notes a")
        show_links_dict = {aref.text: aref["href"] for aref in show_links_html}
        return show_links_dict

    @classmethod
    async def from_url(cls, url: str, http_session: ClientSession = None) -> EpisodeDetailsSoup:
        try:
            http_session = http_session or ClientSession()
            async with http_session:
                html = await response_(url, http_session)
                soup = EpisodeDetailsSoup(html, "html.parser", url=url)
                return soup
        except Exception as e:
            logger.error(f"error in detailsoup: {e}")


# not async so we scrape in reverse chronological order and can abort on duplicates


class DTGTagSelector(TagSelector):
    @property
    def title(self):
        return self.select_(".episode-title")

    @property
    def episode_number(self):
        """string because 'bonus' episodes are not numbered"""
        res = self.select_(".episode-info").split()[1]
        return str(res)

    @property
    def date(self):
        return self.select_(".publish-date")

    @property
    def url(self):
        return self.select_link(".episode-title a")
