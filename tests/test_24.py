import pytest

from scrapaw.pyd import dtg_fnc, dtg_pyd

import scrapaw.captivate_fncs


@pytest.mark.asyncio
async def test_24():
    ep = await dtg_pyd.EpisodeBase.from_url(
        'https://decoding-the-gurus.captivate.fm/episode/hasan-piker-a-swashbuckling-bromance'
    )
    ...


@pytest.mark.asyncio
async def test_25():
    async for res in scrapaw.captivate_fncs.episode_urls_from_url('https://decoding-the-gurus.captivate.fm/'):
        ...


@pytest.mark.asyncio
async def test_podcast():
    pod = dtg_pyd.DTGPodcast()
    async for ep in pod.get_episodes(limit=3):
        assert isinstance(ep, dtg_pyd.EpisodeBase)
    assert pod.episodes
    assert all(isinstance(_, dtg_pyd.EpisodeBase) for _ in pod.episodes)
    assert len(pod.episodes) == 3
    async for ep2 in pod.get_episodes(limit=3):
        assert isinstance(ep2, dtg_pyd.EpisodeBase)
    assert len(pod.episodes) == 6
    async for ep3 in pod.get_episodes(limit=3, max_dupes=3):
        assert isinstance(ep3, dtg_pyd.EpisodeBase)
    assert len(pod.episodes) == 6

