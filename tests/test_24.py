from pprint import pprint

import pytest

from scrapaw.pyd import dtg_pyd, dtg_fnc

@pytest.mark.asyncio
async def test_24():
    ep = await dtg_pyd.DTGEpisode.from_url('https://decoding-the-gurus.captivate.fm/episode/hasan-piker-a-swashbuckling-bromance')
    ...

@pytest.mark.asyncio
async def test_25():
    async for res in dtg_fnc.episode_urls_from_url('https://decoding-the-gurus.captivate.fm/'):
        ...

@pytest.mark.asyncio
async def test_podcast():
    pod = dtg_pyd.DTGPodcast()
    await pod.get_episodes(limit=3)
    assert pod.episodes
    assert len(pod.episodes) == 3
    assert all(isinstance(_, dtg_pyd.DTGEpisode) for _ in pod.episodes)
    pprint(pod.episodes[0])
    ...