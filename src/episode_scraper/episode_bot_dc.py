from __future__ import annotations

import asyncio
import os
from dataclasses import dataclass
from typing import AsyncGenerator

from aiohttp import ClientSession
from loguru import logger

from .soups import PodcastSoup

SLEEP = int(os.environ.get("SCRAPER_SLEEP", 60 * 10))
MAX_DUPES = os.environ.get("MAX_DUPES", 3)


class EpisodeBotDC:
    def __init__(
        self,
        http_session: ClientSession,
        podcast_soup: PodcastSoup,
        queue: asyncio.Queue,
        sleep: int = SLEEP,
    ):
        self.http_session = http_session
        self.podcast_soup = podcast_soup
        self.sleep = sleep
        self.queue = queue

    @classmethod
    async def from_url(cls, url, queue, http_session: ClientSession) -> "EpisodeBotDC":
        main_soup = await PodcastSoup.from_url(url, http_session, queue)
        return cls(http_session, main_soup, queue)

    async def run_q_eps(self) -> None:
        """Schedule scraper and writer tasks."""
        logger.info(
            f"Initialised : {self.podcast_soup.podcast_url}",
        )
        while True:
            logger.debug("Waking")
            episode_stream = self.podcast_soup.episode_stream()
            async for new in episode_stream:
                await self.queue.put(new)
            logger.debug(f"Sleeping for {self.sleep} seconds")
            await asyncio.sleep(self.sleep)
