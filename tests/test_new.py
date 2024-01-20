import asyncio
from asyncio import Queue

import aiohttp
import pytest
import pytest_asyncio

from episode_scraper.soups.podgetter import PodGetter
from episode_scraper.episode_dc import EpisodeDC


@pytest_asyncio.fixture
async def pod_getter():
    async with aiohttp.ClientSession() as http_session:
        process_qu = Queue()
        podgetter = PodGetter("https://decoding-the-gurus.captivate.fm/", http_session, process_qu)
        yield podgetter


@pytest.mark.asyncio
async def test_pod_getter(pod_getter):
    assert isinstance(pod_getter, PodGetter)
    task = asyncio.create_task(pod_getter.run())
    ep = await pod_getter.queue.get()
    assert isinstance(ep, EpisodeDC)
    task.cancel()
    await asyncio.gather(task)
