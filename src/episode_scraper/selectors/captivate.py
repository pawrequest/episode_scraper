from __future__ import annotations

from abc import ABC

from bs4 import ResultSet
from pawsupport.bs4_ps import PageSelectorABC, TagSelectorABC
# from episode_scraper.selectors.abcs import PageSelectorABC, TagSelectorABC


class CaptivatePageSelector(PageSelectorABC):
    @property
    def listing_pages(self) -> list[str]:
        """Construct list of listing page urls from main url and number of pages"""
        return [self.url + f"/episodes/{_ + 1}/#showEpisodes" for _ in range(self.num_pages)]

    @property
    def listings(self) -> ResultSet:
        return self.tag.select(".episode")

    @property
    def page_nav_links(self) -> ResultSet:
        return self.tag.select(".page-link")

    @property
    def num_pages(self) -> int:
        last_page = self.page_nav_links[-1]["href"]
        num_pages = last_page.split("/")[-1].split("#")[0]
        return int(num_pages)


class CaptivateListingSelectorABC(TagSelectorABC, ABC):
    """Extract information from listing subsection of list page"""

    @property
    def number(self) -> str:
        raise NotImplementedError

    @property
    def date(self) -> str:
        raise NotImplementedError

    @property
    def url(self) -> str:
        raise NotImplementedError

    @property
    def title(self) -> str:
        raise NotImplementedError


class CaptivateDetailPageSelector(PageSelectorABC, ABC):
    @property
    def notes(self) -> list[str]:
        raise NotImplementedError

    @property
    def links(self) -> dict[str, str]:
        raise NotImplementedError
