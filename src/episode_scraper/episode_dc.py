# from __future__ import annotations

import inspect
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Sequence

from loguru import logger

from episode_scraper.writer_dc import EP_PROT

MAYBE_ATTRS = ["title", "notes", "links", "date"]


@dataclass
class EpisodeDC:
    url: str
    title: str
    notes: List[str] = field(default_factory=list)
    links: Dict[str, str] = field(default_factory=dict)
    date: Optional[datetime] = None
    episode_number: Optional[str] = None

    def log_str(self) -> str:
        if self.title and self.date:
            return f"\t\t<green>{self.date.date()}</green> - <bold><cyan>{self.title}</cyan></bold>"
        else:
            return f"\t\t{self.url}"

    def __str__(self):
        return f"{self.__class__.__name__}: {self.title or self.url}"

    def __repr__(self):
        return f"<{self.__class__.__name__}({self.url})>"

    @classmethod
    def log_episodes(cls, eps: Sequence["EpisodeDC"], calling_func=None, msg: str = ""):
        """Logs the first 3 episodes and the last 2 episodes of a sequence episodes"""
        if not eps:
            return
        if calling_func:
            calling_f = calling_func.__name__
        else:
            calling_f = f"{inspect.stack()[1].function} INSPECTED, YOU SHOULD PROVIDE THE FUNC"

        new_msg = f"{msg} {len(eps)} Episodes in {calling_f}():\n"
        new_msg += episodes_log_msg(eps)
        logger.info(new_msg)


def episodes_log_msg(eps: Sequence[EpisodeDC]) -> str:
    msg = ""  # in case no eps
    msg += "\n".join([_.log_str() for _ in eps[:3]])

    if len(eps) == 4:
        fth = eps[3]
        msg += f"\n{fth.log_str()}"
    elif len(eps) > 4:
        to_log = min([2, abs(len(eps) - 4)])
        msg += " \n\t... more ...\n"
        msg += "\n".join([_.log_str() for _ in eps[-to_log:]])
    return msg
