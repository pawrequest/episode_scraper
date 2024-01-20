from __future__ import annotations

import asyncio
import os
from asyncio import Queue
from typing import AsyncGenerator

from aiohttp import ClientSession
from loguru import logger

from .episode_model import EpisodeBase
from .soups import PodcastSoup

SLEEP = int(os.environ.get("SCRAPER_SLEEP", 60 * 10))
MAX_DUPES = os.environ.get("MAX_DUPES", 3)


class EpisodeBot:
    def __init__(
        self,
        http_session: ClientSession,
        podcast_soup: PodcastSoup,
        queue: asyncio.Queue = None,
        sleep: int = SLEEP,
    ):
        self.http_session = http_session
        self.podcast_soup = podcast_soup
        self.sleep = sleep
        self.queue = queue or asyncio.Queue()

    # @classmethod
    # async def from_config(cls, aio_session: ClientSession) -> "EpisodeBot":
    #     url = os.environ.get("MAIN_URL")
    #     main_soup = await PodcastSoup.from_url(url, aio_session)
    #     return cls(aio_session, main_soup)

    @classmethod
    async def from_url(cls, url, queue: Queue = None, http_session: ClientSession = None) -> "EpisodeBot":
        http_session = http_session or ClientSession()
        main_soup = await PodcastSoup.from_url(url, http_session, queue)
        return cls(http_session, main_soup)

    async def run_q(self) -> None:
        """Schedule scraper and writer tasks."""
        logger.info(
            f"Initialised : {self.podcast_soup.podcast_url}",
        )
        while True:
            logger.debug("Waking")
            episode_stream = self.podcast_soup.episode_stream()
            new_stream = self._filter_existing_eps(episode_stream)
            async for new in new_stream:
                await self.queue.put(new)
            logger.debug(f"Sleeping for {self.sleep} seconds")
            await asyncio.sleep(self.sleep)

    async def _filter_existing_eps(self, episodes: AsyncGenerator[EpisodeBase, None]) -> AsyncGenerator[dict, None]:
        """Yields episodes that do not exist in db."""
        dupes = 0
        async for episode in episodes:
            if self._episode_exists(episode):
                dupes += 1
                if dupes >= MAX_DUPES:
                    break
                continue
            yield episode
