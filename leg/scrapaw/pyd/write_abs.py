from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Sequence



class EpisodeWriterABC(ABC):
    # def __init__(self, episodes: EP_PROT | Sequence[EP_PROT]):
    def __init__(self, episodes: EP_PROT | Sequence[EP_PROT]):
        if not isinstance(episodes, Sequence):
            episodes = (episodes,)
        self.episodes = episodes

    def write_many(self, eps=None) -> str:
        eps = eps or self.episodes
        text = self._post_head_text(eps)
        text += "".join([self.write_one(ep) for ep in eps])
        text += self._post_tail_text()
        return text

    def write_one(self, episode: EP_PROT = None) -> str:
        if len(self.episodes) != 1:
            raise ValueError(f"No episode provided and {len(self.episodes)} episodes in writer.")
        episode = episode or self.episodes[0]
        text = self._title_text(episode)
        text += self._date_text(episode.date.date().strftime("%A %B %d %Y"))
        text += self._notes_text(episode.notes) or ""
        text += self._links_text(episode.links) or ""
        text += self._ep_tail_text()
        return text

    @abstractmethod
    def _post_head_text(self, episode) -> str:
        raise NotImplementedError

    @abstractmethod
    def _title_text(self, episode) -> str:
        raise NotImplementedError

    @abstractmethod
    def _date_text(self, date_pub) -> str:
        raise NotImplementedError

    @abstractmethod
    def _notes_text(self, notes) -> str:
        raise NotImplementedError

    @abstractmethod
    def _links_text(self, links) -> str:
        raise NotImplementedError

    @abstractmethod
    def _ep_tail_text(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def _post_tail_text(self) -> str:
        raise NotImplementedError
