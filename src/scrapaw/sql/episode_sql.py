# from __future__ import annotations

import typing as _t

from loguru import logger
import sqlmodel
import aiohttp
import pydantic as _p

from .database import session_manager
from .scrapaw_config import ScrapawConfig, scrapaw_settings
from .. import EpisodeBase

if sqlmodel is None:
    raise ImportError("SQLModel not found")
MAYBE_ATTRS = ["title", "notes", "links", "date"]


async def get_add_to_session(ep_cls: type[_p.BaseModel]) -> None:
    sett = scrapaw_settings()
    with session_manager() as session:
        async with aiohttp.ClientSession() as http_session:
            async for ep in episode_generator2(
                    base_url=str(sett.podcast_url),
                    session_h=http_session,
                    limit=sett.scrape_limit,
            ):
                ep_val = ep_cls.model_validate(ep, from_attributes=True)
                session.add(ep_val)
                logger.info(f"added {ep.title}")
                session.commit()


async def episode_generator2(
        settings: ScrapawConfig
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
                        raise pod_abs.MaxDupeError(f"Max Duplicate Episodes Reached: {max_dupe}")
                else:
                    raise pod_abs.DupeError(f"Duplicate episode found: {episode_url}")
            ep = await EpisodeBase.from_url(episode_url)
            yield ep
    except Exception:
        logger.exception("Error getting episodes")
        raise pod_abs.SrapeError("Error getting episodes")
