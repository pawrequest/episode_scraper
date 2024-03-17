from __future__ import annotations, annotations

from .captivate_selectors import DetailPage, ListPage, ListTag


class DTGListPage(ListPage):
    @property
    def subpage_selectors(self) -> list[DTGListTag]:
        return [DTGListTag.from_bs4(_) for _ in self.tag.select(".episode")]


class DTGDetailPage(DetailPage):
    """Extract information from detail page"""

    @property
    def ep_notes(self) -> list[str]:
        paragraphs = self.tag.select(".show-notes p")
        return [p.text for p in paragraphs if p.text != "Links"]

    @property
    def ep_links(self) -> dict[str, str]:
        show_links_html = self.tag.select(".show-notes a")
        return {_.text: _["href"] for _ in show_links_html}


class DTGListTag(ListTag):
    @property
    def ep_number(self) -> str:
        """string because 'bonus' episodes are not numbered"""
        res = self.select_text(".episode-info").split()[1]
        return str(res)

    @property
    def ep_date(self) -> str:
        return self.select_text(".publish-date")

    @property
    def ep_url(self) -> str:
        # return self.select_link(".episode-title")
        return self.select_link(".episode-title a")

    @property
    def ep_title(self) -> str:
        return self.select_text(".episode-title")
