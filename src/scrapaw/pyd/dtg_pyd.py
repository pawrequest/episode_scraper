import abc
import datetime as dt
import typing as _t

import aiohttp
import pydantic as _p
from dateutil import parser

from . import dtg_fnc as fnc
from .. import get_soup


# def tag_text(tag: bs4.Tag, *args, **kwargs) -> str:
#     return tag.select_one(*args, **kwargs).text.strip()
#
#
# def tag_link(tag: bs4.Tag, *args, **kwargs) -> str:
#     return tag.select_one(*args, **kwargs)["href"]

#
# class DetailPage(_p.BaseModel):
#     detail_url: str
#     episode_notes: list = _p.Field(default_factory=list)
#     episode_links: dict[str, str] = _p.Field(default_factory=dict)
#
#
# class ListingSubPage(_p.BaseModel):
#     episode_number: str = ''
#     episode_date: dt.date
#     episode_url: str
#     episode_title: str
#
#
# class ListingPage(_p.BaseModel):
#     listing_url: str
#     listing_subpages: list[ListingSubPage] | None = None


class Episode(_p.BaseModel):
    title: str
    url: str
    date: dt.date
    notes: list[str]
    links: dict[str, str]
    number: str

    @classmethod
    @abc.abstractmethod
    async def from_url(cls, url, session: aiohttp.ClientSession | None = None) -> _t.Self:
        raise NotImplementedError

    @_p.field_validator('date', mode='before')
    def date_is_str(cls, v):
        if isinstance(v, str):
            res = parser.parse(v).date()
            print(f'Parsed date: {v} - to - {res}')
            return res
        return v


class DTGEpisode(Episode):
    @classmethod
    async def from_url(cls, url, session: aiohttp.ClientSession | None = None) -> _t.Self:
        tag = await get_soup.soup_from_url(url=url, session=session)
        return cls(
            url=url,
            title=fnc.tag_title(tag=tag),
            date=fnc.tag_ep_date(tag=tag),
            notes=fnc.tag_notes(tag=tag),
            links=fnc.tag_links(tag=tag),
            number=fnc.tag_ep_num(tag=tag),
        )


class Podcast(_p.BaseModel, abc.ABC):
    name: _t.ClassVar[str]
    base_url: _t.ClassVar[str]
    episodes: list[Episode] = _p.Field(default_factory=list)

    async def all_urls(self) -> list[str]:
        return await fnc.listing_urls_from_url(self.base_url)

    @abc.abstractmethod
    async def get_episodes(
            self,
            limit: int | None = None,
            session: aiohttp.ClientSession | None = None,
            max_dupes: int = 3
    ):
        raise NotImplementedError


class DTGPodcast(Podcast):
    name: _t.ClassVar[str] = 'Decoding The Gurus'
    base_url: _t.ClassVar[str] = 'https://decoding-the-gurus.captivate.fm/'
    episodes: list[DTGEpisode] = _p.Field(default_factory=list)

    async def get_episodes(
            self,
            limit: int | None = None,
            session: aiohttp.ClientSession | None = None,
            max_dupes: int = 3
    ):
        session = session or aiohttp.ClientSession()
        dupes = 0
        async for episode_url in fnc.episode_urls_from_url(self.base_url, session=session):
            if limit and len(self.episodes) >= limit:
                break
            if episode_url in [ep.url for ep in self.episodes]:
                dupes += 1
                if dupes >= max_dupes:
                    break
                continue
            self.episodes.append(await DTGEpisode.from_url(episode_url))
        ...
