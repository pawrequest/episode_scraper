import typing as _t
import datetime as dt

import aiohttp
import bs4
import pydantic as _p
from dateutil import parser
from loguru import logger

from . import captivate, get_soup
from .scrapaw_config import ScrapawConfig

# TODO: TIMESTAMP TYPE: css class = 'cp-timestamp'
# TODO: SHOWNOTES work properly!

class EpisodeBase(_p.BaseModel):
    title: str
    url: str
    date: dt.date
    notes: list[str]
    links: dict[str, str]
    number: str
    # show_notes_html: str | None = None

    def __hash__(self):
        return hash((self.title, self.date.isoformat()))

    def __eq__(self, other):
        return self.title == other.title and self.date == other.date

    @classmethod
    async def from_url(cls, url, http_session: aiohttp.ClientSession) -> _t.Self:
        tag = await get_soup.soup_from_url(url=url, http_session=http_session)
        return cls.model_validate(
            dict(
                url=url,
                title=ep_soup_title(tag=tag),
                date=ep_soup_date(tag=tag),
                notes=ep_soup_notes(tag=tag),
                links=ep_soup_links(tag=tag),
                number=ep_soup_num(tag=tag),
                # show_notes_html=str(tag.select_one('.show-notes')),
            )
        )


def ep_soup_notes(tag: bs4.Tag) -> list[str]:
    paragraphs = tag.select('.show-notes p')
    return [p.text for p in paragraphs if p.text != 'Links' and not p.find('a', class_='cp-timestamp')]


def ep_soup_links(tag: bs4.Tag) -> dict[str, str]:
    show_links_html = tag.select('.show-notes a')
    show_links_html = [_ for _ in show_links_html if 'cp-timestamp' not in _.get('class', [])]
    return {_.text: _['href'] for _ in show_links_html}


def ep_soup_num(tag: bs4.Tag) -> str:
    """string because 'bonus' episodes are not numbered"""
    return captivate.select_text(tag, '.episode-info').split()[1]


def ep_soup_date(tag: bs4.Tag) -> dt.date:
    datestr = captivate.select_text(tag, '.publish-date')
    return parser.parse(datestr).date()


def ep_soup_title(tag: bs4.Tag) -> str:
    return captivate.select_text(tag, '.episode-title')


async def episode_generator(
    config: ScrapawConfig, http_session: aiohttp.ClientSession
) -> _t.AsyncGenerator[EpisodeBase, None]:
    try:
        ep_count = 0
        async for episode_url in captivate.episode_urls_from_url(str(config.podcast_url), http_session=http_session):
            ep_count += 1
            if config.scrape_limit is not None and ep_count >= config.scrape_limit:
                break
            ep = await EpisodeBase.from_url(episode_url, http_session=http_session)
            yield ep
    except Exception as e:
        logger.exception(f'Error getting episodes {str(e.args)}')
        raise e
