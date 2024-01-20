from __future__ import annotations

from typing import Protocol, TYPE_CHECKING

from bs4 import Tag
from dateutil.parser import parse
from loguru import logger

from episode_scraper import EpisodeDC

if TYPE_CHECKING:
    from episode_scraper.old.my_soup import DetailPage, ListingSoup
    from episode_scraper.soups.selectors import ListingSelector, DetailPageSelector


def num_pages_(soup: Tag) -> int:
    page_links = soup.select(".page-link")
    last_page = page_links[-1]["href"]
    num_pages = last_page.split("/")[-1].split("#")[0]
    return int(num_pages)


def list_page_strs_(main_url: str, num_pages: int) -> list[str]:
    return [main_url + f"/episodes/{_ + 1}/#showEpisodes" for _ in range(num_pages)]


async def ep_from_selectors(l_select: ListingSelector, d_select: DetailPageSelector) -> EpisodeDC:
    return EpisodeDC(
        title=l_select.ep_title,
        url=l_select.ep_url,
        episode_number=l_select.ep_number,
        date=l_select.ep_date,
        notes=d_select.ep_notes,
        links=d_select.ep_links,
    )


class ListingProtocol(Protocol):
    @property
    def ep_number(self) -> str:
        """string because 'bonus' episodes are not numbered"""
        ...

    @property
    def ep_date(self) -> str:
        ...

    @property
    def ep_url(self) -> str:
        ...

    @property
    def ep_title(self) -> str:
        ...


class DetailProtocol(Protocol):
    @property
    def ep_notes(self) -> list:
        ...

    @property
    def ep_links(self) -> dict[str, str]:
        ...


async def ep_from_proto(listing: ListingProtocol, detail: DetailProtocol) -> EpisodeDC:
    date = parse(listing.ep_date)
    return EpisodeDC(
        title=listing.ep_title,
        url=listing.ep_url,
        episode_number=listing.ep_number,
        date=date,
        notes=detail.ep_notes,
        links=detail.ep_links,
    )


async def ep_from_soups(list_soup: ListingSoup, detail_soup: DetailPage) -> EpisodeDC:
    return EpisodeDC(
        title=list_soup.ep_title,
        url=list_soup.ep_url,
        episode_number=list_soup.ep_number,
        date=list_soup.ep_date,
        notes=detail_soup.ep_notes,
        links=detail_soup.ep_links,
    )


async def ep_from_tag(ep_tag: Tag) -> EpisodeDC:
    try:
        l_selector = ListingSelector(ep_tag)
        d_selector = DetailPageSelector(ep_tag)
        return await ep_from_selectors(l_selector, d_selector)
    except Exception as e:
        logger.error(f"Error in episodes: {e}")
        raise e
