import typing as _t

import aiohttp
import bs4
from pydantic import HttpUrl
from scrapaw import get_soup


def get_listing_urls(url, num_pages) -> list[str]:
    """Construct list of listing page urls from main url and number of pages"""
    return [url + f'/episodes/{_ + 1}/#showEpisodes' for _ in range(num_pages)]


def num_pages(tag) -> int:
    page_nav_links = tag.select('.page-link')
    last_page = page_nav_links[-1]['href']
    num_pages_ = last_page.split('/')[-1].split('#')[0]
    return int(num_pages_)


def select_text(tag: bs4.Tag, *args, **kwargs) -> str:
    return tag.select_one(*args, **kwargs).text.strip()


def select_link(tag: bs4.Tag, *args, **kwargs) -> str:
    return tag.select_one(*args, **kwargs)['href']


def tag_url(tag: bs4.Tag) -> str:
    return select_link(tag, '.episode-title a')


async def episode_urls_from_url(url:str, h_session: aiohttp.ClientSession | None = None) -> \
        _t.AsyncGenerator[str, None]:
    listing_urls = await listing_urls_from_url(url)
    for listing_url in listing_urls:
        soup = await get_soup.soup_from_url(listing_url, session=h_session)
        for tag in soup.select('.episode'):
            yield tag_url(tag)


async def listing_urls_from_url(url:str) -> list[str]:
    soup = await get_soup.soup_from_url(url)
    num_pgs = num_pages(soup)
    return get_listing_urls(url, num_pgs)
