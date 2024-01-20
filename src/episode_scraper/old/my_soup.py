from __future__ import annotations

from aiohttp import ClientSession
from bs4 import BeautifulSoup
from pawsupport import response_

from episode_scraper.soups.funcs import list_page_strs_, num_pages_


class MySoup(BeautifulSoup):
    def __init__(self, url, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.url = url

    @classmethod
    async def from_url(cls, url: str, http_session: ClientSession):
        html = await response_(url, http_session)
        return cls(url, html, "html.parser")

    def select_(self, *args, **kwargs):
        return self.tag.select_one(*args, **kwargs).text.strip()

    def select_link(self, *args, **kwargs):
        return self.tag.select_one(*args, **kwargs)["href"]


class ListPage(MySoup):
    @property
    def num_pages(self) -> int:
        return num_pages_(self)

    @property
    def listing_pages(self) -> list[str]:
        """Construct list of listing page urls from main url and number of pages"""
        return list_page_strs_(self.url, self.num_pages)

    @property
    def listings(self):
        return self.select(".episode")


class ListingSoup(MySoup):
    @property
    def ep_number(self):
        """string because 'bonus' episodes are not numbered"""
        res = self.select_one(".episode-info").text.strip().split()[1]
        return str(res)

    @property
    def ep_date(self):
        return self.select_one(".publish-date").text.strip()

    @property
    def ep_url(self):
        return self.select_link(".episode-title a")

    @property
    def ep_title(self):
        return self.select(".episode-title")


class DetailPage(MySoup):
    @property
    def ep_notes(self):
        paragraphs = self.tag.select(".show-notes p")
        show_notes = [p.text for p in paragraphs if p.text != "Links"]

        return show_notes or None

    @property
    def ep_links(self):
        show_links_html = self.tag.select(".show-notes a")
        show_links_dict = {aref.text: aref["href"] for aref in show_links_html}
        return show_links_dict
