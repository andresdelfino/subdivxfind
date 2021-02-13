import itertools
import re

from typing import Iterator, NamedTuple

import bs4
import requests

from subdivxfind.constants import (
    BASE,
    ENGINE,
    SEARCH_URL,
)


class Match(NamedTuple):
    title: str
    url: str
    description: str
    found_in: str


comment_url_re = re.compile(r'popcoment\.php')


class Finder:
    def __init__(self, title: str, tag: str, strip_year: bool = False) -> None:
        self.title = title.casefold()
        self.title = re.sub(' +', ' ', self.title)
        self.tag = tag.casefold()
        self.strip_year = strip_year

    def find(self) -> Iterator[Match]:
        self.session = requests.Session()

        for page_n in itertools.count(1):
            if page_n == 1:
                params = {
                    'buscar': self.title,
                    'accion': 5,
                    'masdesc': '',
                    'subtitulos': 1,
                    'realiza_b': 1,
                }
            else:
                params = {
                    'accion': 5,
                    'buscar': self.title,
                    'masdesc': '',
                    'idusuario': '',
                    'nick': '',
                    'oxfecha': '',
                    'oxcd': '',
                    'oxdown': '',
                    'pg': page_n,
                }

            page = self.session.get(SEARCH_URL, params=params)

            if 'Downloads:' not in page.text:
                return

            soup = bs4.BeautifulSoup(page.content, ENGINE, from_encoding='latin_1')

            title_list = soup.find_all('div', id='menu_detalle_buscador')
            detail_list = soup.find_all('div', id='buscador_detalle')

            for title_section, detail_section in zip(title_list, detail_list):
                found_in = None

                title_anchor = title_section.find('a')

                url = title_anchor['href']

                media_title = title_anchor.string
                media_title = media_title.replace('Subtitulos de ', '')
                media_title = media_title.casefold()
                media_title = re.sub(' +', ' ', media_title)

                if self.strip_year:
                    # Remove year from title
                    media_title = media_title.rsplit('(', maxsplit=1)[0]
                    media_title = media_title.rstrip()

                if self.title not in media_title:
                    continue

                sub = detail_section.find('div', id='buscador_detalle_sub')
                if sub.string:
                    description = sub.string
                else:
                    description = ''

                if self.tag in description.casefold():
                    found_in = 'description'
                elif detail_section.find('a', href=comment_url_re) and self._in_comments(url):
                    found_in = 'comments'

                if found_in:
                    yield Match(media_title, url, description, found_in)

    def _in_comments(self, url: str) -> bool:
        comment_page = self.session.get(url)
        comment_soup = bs4.BeautifulSoup(comment_page.content, ENGINE, from_encoding='latin_1')

        for comment in comment_soup.find_all('div', id='detalle_reng_coment1'):
            comment_string = comment.contents[0].string
            if comment_string is None:
                print('error:', url)
                continue
            if self.tag in comment_string.casefold():
                return True

        return False
