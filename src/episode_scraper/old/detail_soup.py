from __future__ import annotations

from aiohttp import ClientSession as ClientSession
from bs4 import BeautifulSoup
from loguru import logger
from pawsupport import response_


class EpisodeDetailsSoup(BeautifulSoup):
    """BeautifulSoup extended to parse episode details page"""

    def __init__(self, markup: str, url, parser: str = "html.parser"):
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
                soup = EpisodeDetailsSoup(html, url, "html.parser")
                return soup
        except Exception as e:
            logger.error(f"error in detailsoup: {e}")
