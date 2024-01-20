from __future__ import annotations

from aiohttp import ClientSession
from bs4 import BeautifulSoup, Tag
from pawsupport import response_

from episode_scraper.soups.funcs import list_page_strs_, num_pages_


class TagSelector:
    def __init__(self, tag: Tag):
        self.tag = tag

    @classmethod
    async def from_url(cls, url: str, http_session: ClientSession):
        try:
            html = await response_(url, http_session)
            soup = BeautifulSoup(html, "html.parser")
            return cls(soup)
        except Exception as e:
            logger.error(f"Error getting {url}: {e}", bot_name="Scraper")

    def select_(self, *args, **kwargs):
        return self.tag.select_one(*args, **kwargs).text.strip()

    def select_link(self, *args, **kwargs):
        return self.tag.select_one(*args, **kwargs)["href"]


class PageSelector(TagSelector):
    def __init__(self, tag: Tag, url):
        try:
            super().__init__(tag)
            self.url = url
        except Exception as e:
            logger.error(f"Error getting {url}: {e}", bot_name="Scraper")

    @classmethod
    async def from_url(cls, url: str, http_session: ClientSession):
        try:
            html = await response_(url, http_session)
            soup = BeautifulSoup(html, "html.parser")
            return cls(soup, url)
        except Exception as e:
            logger.error(f"Error getting {url}: {e}", bot_name="Scraper")


class ListPageSelector(PageSelector):
    @property
    def num_pages(self) -> int:
        return num_pages_(self.tag)

    @property
    def listing_pages(self) -> list[str]:
        """Construct list of listing page urls from main url and number of pages"""
        return list_page_strs_(self.url, self.num_pages)

    @property
    def listings(self):
        return self.tag.select(".episode")


class ListingSelector(TagSelector):
    @property
    def ep_number(self):
        """string because 'bonus' episodes are not numbered"""
        res = self.select_(".episode-info").split()[1]
        return str(res)

    @property
    def ep_date(self):
        return self.select_(".publish-date")

    @property
    def ep_url(self):
        return self.select_link(".episode-title a")

    @property
    def ep_title(self):
        return self.select_(".episode-title")


class DetailPageSelector(PageSelector):
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
