# from __future__ import annotations

from loguru import logger
import sqlmodel
import aiohttp

from .database import session_manager
from ..dtg import get_episodes_blind
from .scrapaw_config import scrapaw_settings
import pydantic as _p

if sqlmodel is None:
    raise ImportError("SQLModel not found")
MAYBE_ATTRS = ["title", "notes", "links", "date"]


async def get_add_to_session(ep_cls: type[_p.BaseModel]) -> None:
    sett = scrapaw_settings()
    with session_manager() as session:
        async with aiohttp.ClientSession() as http_session:
            async for ep in get_episodes_blind(
                    base_url=str(sett.podcast_url),
                    session_h=http_session,
                    limit=sett.scrape_limit,
            ):
                ep_val = ep_cls.model_validate(ep, from_attributes=True)
                session.add(ep_val)
                logger.info(f"added {ep.title}")
                session.commit()
