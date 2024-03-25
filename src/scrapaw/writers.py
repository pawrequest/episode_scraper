from __future__ import annotations

from typing import Sequence

from loguru import logger

from . import _write_abs, pod_abs, consts


class HtmlWriter(_write_abs.EpisodeWriterABC):
    def _contents(self, eps: Sequence[pod_abs.Episode] = None) -> str:
        eps = eps or self.episodes
        toc = "<h2>Table of Contents</h2>\n"
        for i, ep in enumerate(eps):
            toc += f"<a href='#ep-{i}'>{ep.title}</a><br>\n"
        return toc

    def _post_head_text(self, episode: pod_abs.Episode) -> str:
        text = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>{consts.HTML_TITLE}</title>
            </head>
            <body>
            """
        text += self._contents(self.episodes)
        return text

    def _title_text(self, episode: pod_abs.Episode, ep_id="") -> str:
        return f"<h1 id='ep-{str(ep_id)}'>{episode.title}</h1>\n<a href='{episode.url}'>Play on Captivate.fm</a>\n"

    def _date_text(self, date_pub) -> str:
        return f"<p>Date Published: {date_pub}</p>\n"

    def _notes_text(self, notes) -> str:
        notes = "<h3>Show Notes:</h3>\n" + "\n".join(
            [f"<p>{_}</p>" for _ in notes]
        ) + "\n" if notes else ""
        return notes

    def _links_text(self, links) -> str:
        if not links:
            return ""
        links_html = "\n".join([f'<a href="{link}">{text}</a><br>' for text, link in links.items()])
        return f"<h3>Show Links:</h3>\n{links_html}"

    def _ep_tail_text(self) -> str:
        return "<br> <br>"

    def _post_tail_text(self) -> str:
        return "\n</body>\n</html>"


class RPostWriter(_write_abs.EpisodeWriterABC):
    def _post_head_text(self, episode: pod_abs.Episode) -> str:
        return ""

    def _title_text(self, episode: pod_abs.Episode) -> str:
        return f"## [{episode.title}]({episode.url})\n \n"

    def _date_text(self, date_pub) -> str:
        return f"***{date_pub}***\n \n"

    def _notes_text(self, notes: list[str]) -> str:
        notes = "***Show Notes:***\n \n" + "\n \n".join(notes) + "\n \n" if notes else ""
        return notes

    def _links_text(self, links: dict[str, str]) -> str:
        if not links:
            return ""
        links_str = "***Show Links:***\n \n" + "\n \n".join(
            [f"[{text}]({link})\n" for text, link in links.items()]
        )
        return links_str

    def _ep_tail_text(self) -> str:
        return "\n \n"

    def _post_tail_text(self) -> str:
        return "\n \n"


class RWikiWriter(_write_abs.EpisodeWriterABC):
    def _post_head_text(self, episode: pod_abs.Episode) -> str:
        return ""

    def _title_text(self, episode: pod_abs.Episode) -> str:
        return f"### [{episode.title}]({episode.url})\n \n"

    def _date_text(self, date_pub) -> str:
        return f"***{date_pub}***\n \n"

    def _notes_text(self, notes: list[str]) -> str:
        notes = "***Notes:***\n \n" + "\n \n".join(notes) + "\n \n" if notes else ""
        return notes

    def _links_text(self, links: dict[str, str]) -> str:
        if not links:
            return ""
        links = "***Links:***\n \n" + "\n \n".join(
            [f"[{text}]({link})" for text, link in links.items()]
        ) + "\n \n"
        return links

    def _ep_tail_text(self) -> str:
        return "\n\n---------------------\n\n"

    def _post_tail_text(self) -> str:
        return "\n \n --- \n \n"


async def episode_subreddit_post_text(episode: pod_abs.Episode) -> tuple[str, str]:
    try:
        title = f"NEW EPISODE: {episode.title}"
        writer = RPostWriter(episode)
        text = writer.write_many()
        return title, text
    except Exception as e:
        logger.error(f"Error submitting episode: {e}")
