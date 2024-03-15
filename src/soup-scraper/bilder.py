from bs4 import ResultSet, Tag


# Utility


def tag_text(tag: Tag, *args, **kwargs) -> str:
    return tag.select_one(*args, **kwargs).text.strip()


def tag_link(tag: Tag, *args, **kwargs) -> str:
    return tag.select_one(*args, **kwargs)["href"]


# Detail Page


def notes(tag) -> list[str]:
    paragraphs = tag.select(".show-notes p")
    return [p.text for p in paragraphs if p.text != "Links"]


def links(tag) -> dict[str, str]:
    show_links_html = tag.select(".show-notes a")
    return {_.text: _["href"] for _ in show_links_html}


# List SubPage
def number(tag) -> str:
    """string because 'bonus' episodes are not numbered"""
    return tag_text(tag, ".episode-info").split()[1]


def date(tag) -> str:
    return tag_text(tag, ".publish-date")


def url(tag: Tag) -> str:
    return tag_link(tag, ".episode-title a")


def title(tag: Tag) -> str:
    return tag_text(tag, ".episode-title")


# List Page
def get_all_urls(url, num_pages) -> list[str]:
    """Construct list of listing page urls from main url and number of pages"""
    return [url + f"/episodes/{_ + 1}/#showEpisodes" for _ in range(num_pages)]


def get_subpage_tags(tag: Tag) -> ResultSet[Tag]:
    return tag.select(".episode")


def subpage_selectors(self) -> list[Tag]:
    # return [ListTag.from_bs4(_) for _ in self.get_subpage_tags]
    ...


def page_nav_links(tag: Tag) -> ResultSet[Tag]:
    return tag.select(".page-link")


def num_pages(page_nav_links) -> int:
    last_page = page_nav_links[-1]["href"]
    num_pages = last_page.split("/")[-1].split("#")[0]
    return int(num_pages)
