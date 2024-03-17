import abc
import datetime as dt
import typing as _t

import aiohttp
import pydantic as _p
from dateutil import parser

from . import dtg_fnc as fnc
from .. import get_soup


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
        return cls.model_validate(
            dict(
                url=url,
                title=fnc.tag_title(tag=tag),
                date=fnc.tag_ep_date(tag=tag),
                notes=fnc.tag_notes(tag=tag),
                links=fnc.tag_links(tag=tag),
                number=fnc.tag_ep_num(tag=tag),
            )
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
            max_dupes: int = None
    ) -> _t.AsyncGenerator[DTGEpisode, None]:
        session = session or aiohttp.ClientSession()
        dupes = 0
        ep_count = 0
        async for episode_url in fnc.episode_urls_from_url(self.base_url, session=session):
            if limit and ep_count >= limit:
                break
            if episode_url in [ep.url for ep in self.episodes]:
                print(f'Duplicate episode found: {episode_url}')
                dupes += 1
                if max_dupes and dupes >= max_dupes:
                    print(f'Exiting due to {max_dupes} duplicates')
                    break
                continue
            ep = await DTGEpisode.from_url(episode_url)
            self.episodes.append(ep)
            ep_count += 1
            yield ep
