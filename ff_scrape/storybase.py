from datetime import datetime
from typing import List

class Chapter(object):
    __word_count: int
    __body: str
    __raw_body: str
    __processed_body: str
    __name: str

    def __init__(self):
        self.__word_count = 0
        self.__raw_body = ""
        self.__processed_body = ""
        self.__name = ""

    @property
    def word_count(self) -> int:
        return self.__word_count

    @word_count.setter
    def word_count(self, count)-> None:
        self.__word_count = count

    @property
    def processed_body(self) -> str:
        return self.__processed_body

    @processed_body.setter
    def processed_body(self, val) -> None:
        self.__processed_body = val

    @property
    def raw_body(self) -> str:
        return self.__raw_body

    @raw_body.setter
    def raw_body(self, val) -> None:
        self.__raw_body = val

    @property
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, name) -> None:
        self.__name = name


class Story(object):

    _author: str
    _title: str
    _url: str
    _author_url: str
    _chapters: List[Chapter]
    _domain: str
    _status: str
    _universe: List[str]
    _categories: List[str]
    _genres: List[str]
    _published: datetime
    _updated: datetime
    _summary: str
    _rating: str
    _pairings: List[str]
    _warnings: List[str]
    _characters: List[str]
    _raw_index_page: str

    def __init__(self, url, **kwargs):
        self._url = url

        self._author = None
        self._title = None
        self._author_url = None
        self._domain = None
        self._status = None
        self._published = None
        self._updated = None
        self._summary = None
        self._rating = None
        self._raw_index_page = None

        self._chapters = []
        self._categories = []
        self._genres = []
        self._pairings = []
        self._universe = []
        self._warnings = []
        self._characters = []

    def __repr__(self):
        return '%s(url:%s)' % (self.__class__.__name__,
                               self._url or "''")

    @property
    def url(self) -> str: return self._url

    @property
    def domain(self) -> str: return self._domain

    @domain.setter
    def domain(self, domain) -> None: self._domain = domain

    @property
    def author(self) -> str: return self._author

    @author.setter
    def author(self, author) -> None: self._author = author

    @property
    def title(self) -> str: return self._title

    @title.setter
    def title(self, title): self._title = title

    @property
    def author_url(self) -> str: return self._author_url

    @author_url.setter
    def author_url(self, author_url): self._author_url = author_url

    @property
    def published(self) -> datetime: return self._published

    @published.setter
    def published(self, published): self._published = published

    @property
    def updated(self) -> datetime: return self._updated

    @updated.setter
    def updated(self, updated): self._updated = updated

    @property
    def status(self) -> str: return self._status

    @status.setter
    def status(self, status): self._status = status

    @property
    def universe(self) -> List[str]: return self._universe

    def add_universe(self, universe) -> None: self._universe.append(universe)

    @property
    def summary(self) -> str: return self._summary

    @summary.setter
    def summary(self, summary): self._summary = summary

    @property
    def rating(self) -> str: return self._rating

    @rating.setter
    def rating(self, rating): self._rating = rating

    @property
    def categories(self) -> List[str]: return self._categories

    def add_category(self, category) -> None: self._categories.append(category)

    @property
    def characters(self) -> List[str]: return self._characters

    def add_character(self, character) -> None: self._characters.append(character)

    @property
    def warnings(self) -> List[str]: return self._warnings

    def add_warning(self, warning) -> None: self._warnings.append(warning)

    @property
    def genres(self) -> List[str]: return self._genres

    def add_genre(self, genre) -> None: self._genres.append(genre)

    @property
    def pairings(self) -> List[str]: return self._pairings

    def add_pairing(self, pairing) -> None: self._pairings.append(pairing)

    @property
    def word_count(self) -> int:
        count = 0
        for chapter in self._chapters:
            count += chapter.word_count
        return count

    @property
    def chapters(self) -> List[str]: return self._chapters

    def add_chapter(self, chapter) -> None: self._chapters.append(chapter)

    @property
    def chapter_count(self) -> int: return len(self._chapters)

    @property
    def raw_index_page(self) -> str: return self._raw_index_page

    @raw_index_page.setter
    def raw_index_page(self, value) -> None: self._raw_index_page = value

