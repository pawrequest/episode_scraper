import datetime as dt
import inspect
import typing as _t

import pydantic as _p

from scrapaw.consts import MAX_DUPES


@_t.runtime_checkable
class Episode(_t.Protocol):
    title: str
    url: str
    date: dt.date
    notes: list[str]
    links: dict[str, str]
    number: str


def log_episodes(eps: _t.Sequence[Episode], calling_func=None, msg: str = ''):
    """Logs the first 3 episodes and the last 2 episodes of a sequence episodes"""
    if not eps:
        return
    if calling_func:
        calling_f = calling_func.__name__
    else:
        calling_f = f'{inspect.stack()[1].function} INSPECTED, YOU SHOULD PROVIDE THE FUNC'

    new_msg = f'{msg} {len(eps)} Episodes in {calling_f}():\n'
    new_msg += episodes_log_msg(eps)
    print(new_msg)


def ep_log_str(episode) -> str:
    if episode.title and episode.date:
        return f'\t\t<green>{episode.date}</green> - <bold><cyan>{episode.title}</cyan></bold>'
    else:
        return f'\t\t{episode.url}'


def episodes_log_msg(eps: _t.Sequence[Episode]) -> str:
    msg = ''  # in case no eps
    msg += '\n'.join([ep_log_str(_) for _ in eps[:3]])

    if len(eps) == 4:
        fth = eps[3]
        msg += f'\n{ep_log_str(fth)}'
    elif len(eps) > 4:
        to_log = min([2, abs(len(eps) - 4)])
        msg += ' \n\t... more ...\n'
        msg += '\n'.join([ep_log_str(_) for _ in eps[-to_log:]])
    return msg


class Podcast(_t.Protocol):
    name: _t.ClassVar[str]
    base_url: _t.ClassVar[str]
    episodes: list[Episode] = _p.Field(default_factory=list)

    # async def all_urls(self) -> list[str]:
    #     raise NotImplementedError
    #
    # @abc.abstractmethod
    # async def get_episodes(
    #         self,
    #         limit: int | None = None,
    #         session: aiohttp.ClientSession | None = None,
    #         max_dupes: int = 3
    # ):
    #     raise NotImplementedError


class DupeError(Exception):
    ...


class MaxDupe(Exception):
    ...


type EndOfStream = object


async def dupes_not_exceeded(dupes):
    if dupes > MAX_DUPES:
        raise MaxDupe(f'Found {dupes} duplicates, stopping')


class SrapeError(Exception):
    pass
