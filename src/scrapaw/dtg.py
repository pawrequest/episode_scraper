import functools
import hashlib
import typing as _t
import datetime as dt

import aiohttp
import bs4
import pydantic as _p
from anyio import EndOfStream
from dateutil import parser
from loguru import logger

from . import captivate, get_soup, pod_abs
from .scrapaw_config import ScrapawConfig


class EpisodeBase(_p.BaseModel):
    title: str
    url: str
    date: dt.date
    notes: list[str]
    links: dict[str, str]
    number: str

    @_p.computed_field
    @property
    def get_hash(self) -> str:
        return hashlib.md5(
            ','.join([self.title, self.date.isoformat()]).encode('utf-8')
        ).hexdigest()

    @classmethod
    async def from_url(cls, url, session: aiohttp.ClientSession | None = None) -> _t.Self:
        tag = await get_soup.soup_from_url(url=url, session=session)
        return cls.model_validate(
            dict(
                url=url,
                title=ep_soup_title(tag=tag),
                date=ep_soup_date(tag=tag),
                notes=ep_soup_notes(tag=tag),
                links=ep_soup_links(tag=tag),
                number=ep_soup_num(tag=tag),
            )
        )


def ep_soup_notes(tag: bs4.Tag) -> list[str]:
    paragraphs = tag.select(".show-notes p")
    return [p.text for p in paragraphs if p.text != "Links"]


def ep_soup_links(tag: bs4.Tag) -> dict[str, str]:
    show_links_html = tag.select(".show-notes a")
    return {_.text: _["href"] for _ in show_links_html}


def ep_soup_num(tag: bs4.Tag) -> str:
    """string because 'bonus' episodes are not numbered"""
    return captivate.select_text(tag, ".episode-info").split()[1]


def ep_soup_date(tag: bs4.Tag) -> dt.date:
    datestr = captivate.select_text(tag, ".publish-date")
    return parser.parse(datestr).date()


def ep_soup_title(tag: bs4.Tag) -> str:
    return captivate.select_text(tag, ".episode-title")


async def episode_generator1(
        base_url: str,
        existing_eps: list[EpisodeBase] = None,
        limit: int | None = None,
        session_h: aiohttp.ClientSession | None = None,
        dupe_mode: _t.Literal["allow", "forbid", "ignore", "limited"] = "limited",
        max_dupe: int = 3,
) -> _t.AsyncGenerator[EpisodeBase, None]:
    try:
        existing_eps = existing_eps or []
        session_h = session_h or aiohttp.ClientSession()
        ep_count = 0
        dupes = 0
        async for episode_url in captivate.episode_urls_from_url(base_url, h_session=session_h):
            ep_count += 1
            if limit is not None and ep_count >= limit:
                break
            if episode_url in [ep.url for ep in existing_eps]:
                dupes += 1
                if dupe_mode == "allow":
                    pass
                elif dupe_mode == "ignore":
                    continue
                elif dupe_mode == "limited":
                    if dupes > max_dupe:
                        raise EndOfStream(f"Max Duplicate Episodes Reached: {max_dupe}")
                else:
                    raise ValueError(
                        f"Duplicate episode found with mode {dupe_mode}: {episode_url}"
                    )
            ep = await EpisodeBase.from_url(episode_url)
            yield ep
    except Exception:
        logger.exception("Error getting episodes")
        raise pod_abs.SrapeError("Error getting episodes")


async def episode_generator(config: ScrapawConfig, http_session) -> _t.AsyncGenerator[EpisodeBase, None]:
    try:
        http_session = http_session
        ep_count = 0
        async for episode_url in captivate.episode_urls_from_url(
                str(config.db_loc),
                h_session=http_session
        ):
            ep_count += 1
            if config.scrape_limit is not None and ep_count >= config.scrape_limit:
                break
            ep = await EpisodeBase.from_url(episode_url)
            yield ep
    except Exception as e:
        logger.exception(f"Error getting episodes {str(e.args)}")
        raise e


