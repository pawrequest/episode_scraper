from __future__ import annotations

from bs4 import ResultSet, Tag

from ..selectors import DetailSoup, ListSoup, ListTag


class CDetailPage(DetailSoup):
    pass


class CListTag(ListTag):
    pass


class CListPage(ListSoup):
    """Extract information from list page"""

    @property
    def get_all_urls(self) -> list[str]:
        """Construct list of listing page urls from main url and number of pages"""
        return [self.url + f"/episodes/{_ + 1}/#showEpisodes" for _ in range(self.num_pages)]

    @property
    def get_subpage_tags(self) -> ResultSet[Tag]:
        return self.select(".episode")

    @property
    def subpage_selectors(self) -> list[ListTag]:
        return [ListTag.from_bs4(_) for _ in self.get_subpage_tags]

    @property
    def page_nav_links(self) -> ResultSet[Tag]:
        return self.select(".page-link")

    @property
    def num_pages(self) -> int:
        last_page = self.page_nav_links[-1]["href"]
        num_pages = last_page.split("/")[-1].split("#")[0]
        return int(num_pages)
