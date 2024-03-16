from __future__ import annotations

from abc import ABC, abstractmethod

from aiohttp import ClientSession
from bs4 import ResultSet, Tag, BeautifulSoup
from loguru import logger
from pawsupport.async_ps import response_

from pawsupport.html_ps import PageSelectorABC, TagSelectorABC
from pawsupport.html_ps import PageSoup, TagSoup


class PodSoup(ABC):
    def __init__(
        self,
        list_soup: type(ListSoup),
        detail_soup: type(DetailSoup),
        list_tag: type(ListTag),
    ):
        self.list_soup = list_soup
        self.list_tag = list_tag
        self.detail_soup = detail_soup


class ListSoup(PageSoup):
    @abstractmethod
    def get_all_urls(self) -> list[str]:
        raise NotImplementedError

    @abstractmethod
    def get_subpage_tags(self) -> ResultSet[Tag]:
        raise NotImplementedError


class ListTag(TagSoup):
    @property
    def ep_number(self) -> str:
        raise NotImplementedError

    @property
    def ep_date(self) -> str:
        raise NotImplementedError

    @property
    def ep_url(self) -> str:
        raise NotImplementedError

    @property
    def ep_title(self) -> str:
        raise NotImplementedError


class DetailSoup(PageSoup):
    @property
    def ep_notes(self) -> list[str]:
        raise NotImplementedError

    @property
    def ep_links(self) -> dict[str, str]:
        raise NotImplementedError
