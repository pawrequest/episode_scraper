import typing as _t

import aiohttp
import bs4
import pydantic as _p

from DecodeTheBot.core import consts
from . import abs, captivate, get_soup


class DTGEpisode(abs.Episode):
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


class DTGPodcast(abs.Podcast):
    name: _t.ClassVar[str] = 'Decoding The Gurus'
    base_url: _t.ClassVar[str] = consts.PODCAST_URL,
    episodes: list[DTGEpisode] = _p.Field(default_factory=list)

    async def all_urls(self) -> list[str]:
        return await captivate.listing_urls_from_url(self.base_url)

    async def get_episodes(
            self,
            limit: int | None = None,
            session_h: aiohttp.ClientSession | None = None,
            max_dupes: int = None,
            dupe_mode: _t.Literal['allow', 'forbid', 'ignore'] = 'forbid',
    ) -> _t.AsyncGenerator[DTGEpisode, None]:
        session_h = session_h or aiohttp.ClientSession()
        ep_count = 0
        async for episode_url in captivate.episode_urls_from_url(
                self.base_url,
                h_session=session_h
        ):
            if limit and ep_count >= limit:
                break
            if episode_url in [ep.url for ep in self.episodes]:
                if dupe_mode == 'allow':
                    pass
                elif dupe_mode == 'ignore':
                    continue
                else:
                    raise abs.DupeError(f'Duplicate episode found: {episode_url}')
            ep = await DTGEpisode.from_url(episode_url)
            ep_count += 1
            yield ep


def ep_soup_notes(tag: bs4.Tag) -> list[str]:
    paragraphs = tag.select(".show-notes p")
    return [p.text for p in paragraphs if p.text != "Links"]


def ep_soup_links(tag: bs4.Tag) -> dict[str, str]:
    show_links_html = tag.select(".show-notes a")
    return {_.text: _["href"] for _ in show_links_html}


def ep_soup_num(tag: bs4.Tag) -> str:
    """string because 'bonus' episodes are not numbered"""
    return captivate.select_text(tag, ".episode-info").split()[1]


def ep_soup_date(tag: bs4.Tag) -> str:
    return captivate.select_text(tag, ".publish-date")


def ep_soup_title(tag: bs4.Tag) -> str:
    return captivate.select_text(tag, ".episode-title")


async def get_episodes_fnc(
        base_url: str,
        existing_eps: list[DTGEpisode],
        limit: int | None = None,
        session_h: aiohttp.ClientSession | None = None,
        dupe_mode: _t.Literal['allow', 'forbid', 'ignore'] = 'forbid',
) -> _t.AsyncGenerator[DTGEpisode, None]:
    session_h = session_h or aiohttp.ClientSession()
    ep_count = 0
    async for episode_url in captivate.episode_urls_from_url(
            base_url,
            h_session=session_h
    ):
        if limit and ep_count >= limit:
            break
        if episode_url in [ep.url for ep in existing_eps]:
            if dupe_mode == 'allow':
                pass
            elif dupe_mode == 'ignore':
                continue
            else:
                raise abs.DupeError(f'Duplicate episode found: {episode_url}')
        ep = await DTGEpisode.from_url(episode_url)
        ep_count += 1
        yield ep


async def get_episodes_blind(
        base_url: str,
        limit: int | None = None,
        session_h: aiohttp.ClientSession | None = None,
) -> _t.AsyncGenerator[DTGEpisode, None]:
    session_h = session_h or aiohttp.ClientSession()
    ep_count = 0
    async for episode_url in captivate.episode_urls_from_url(
            base_url,
            h_session=session_h
    ):
        if limit and ep_count >= limit:
            break
        ep = await DTGEpisode.from_url(episode_url)
        ep_count += 1
        yield ep
