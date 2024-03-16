import typing as _t

import aiohttp
import bs4
from bs4 import Tag

from scrapaw import get_soup


# Utility
def select_text(tag: Tag, *args, **kwargs) -> str:
    return tag.select_one(*args, **kwargs).text.strip()


def select_link(tag: Tag, *args, **kwargs) -> str:
    return tag.select_one(*args, **kwargs)["href"]


#####
# Detail Page
def tag_notes(tag: bs4.Tag) -> list[str]:
    paragraphs = tag.select(".show-notes p")
    return [p.text for p in paragraphs if p.text != "Links"]


def tag_links(tag: bs4.Tag) -> dict[str, str]:
    show_links_html = tag.select(".show-notes a")
    return {_.text: _["href"] for _ in show_links_html}


def tag_ep_num(tag: bs4.Tag) -> str:
    """string because 'bonus' episodes are not numbered"""
    return select_text(tag, ".episode-info").split()[1]


def tag_ep_date(tag: bs4.Tag) -> str:
    return select_text(tag, ".publish-date")


def tag_url(tag: Tag) -> str:
    return select_link(tag, ".episode-title a")


def tag_title(tag: Tag) -> str:
    return select_text(tag, ".episode-title")


# List Page
async def episode_urls_from_url(url, session: aiohttp.ClientSession | None = None) -> \
        _t.AsyncGenerator[str, None]:
    listing_urls = await listing_urls_from_url(url)
    for listing_url in listing_urls:
        soup = await get_soup.soup_from_url(listing_url, session=session)
        for tag in soup.select(".episode"):
            yield tag_url(tag)


async def listing_urls_from_url(url) -> list[str]:
    soup = await get_soup.soup_from_url(url)
    num_pgs = num_pages(soup)
    return get_listing_urls(url, num_pgs)


def get_listing_urls(url, num_pages) -> list[str]:
    """Construct list of listing page urls from main url and number of pages"""
    return [url + f"/episodes/{_ + 1}/#showEpisodes" for _ in range(num_pages)]


def num_pages(tag) -> int:
    page_nav_links = tag.select(".page-link")
    last_page = page_nav_links[-1]["href"]
    num_pages_ = last_page.split("/")[-1].split("#")[0]
    return int(num_pages_)
