import itertools
import logging
import os
import re

from typing import (
    Iterator,
    NamedTuple,
)

import bs4
import requests


BASE = 'https://www.subdivx.com'
CHARACTER_ENCODING = 'utf-8'
ENGINE = 'html5lib'

SEARCH_URL = f'{BASE}/index.php'

logger = logging.getLogger(__name__)


class Match(NamedTuple):
    title: str
    url: str
    description: str
    found_in: str


comment_url_re = re.compile(r'popcoment\.php')


class Finder:
    def __init__(self, title: str, tag: str, strip_year: bool = False) -> None:
        self.title = title.casefold()
        self.title = re.sub(' +', ' ', self.title).strip()
        self.tag = tag.casefold()
        self.strip_year = strip_year

    def find(self) -> Iterator[Match]:
        self.session = requests.Session()

        self.session.headers['User-Agent'] = 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0'
        self.session.get('https://www.subdivx.com/')
        self.session.get('https://www.subdivx.com/X50', headers={'Referer': 'https://www.subdivx.com/index.php?abandon=1'})
        response = self.session.post(
            'https://www.subdivx.com/index.php',
            data={
                'usuario': os.environ['SUBDIVX_USERNAME'],
                'clave': os.environ['SUBDIVX_PASSWORD'],
                'Enviar': 'Entrar',
                'accion': '50',
                'enviau': '1',
                'refer': 'https://subdivx.com/',
            },
            headers={'Referer': 'https://www.subdivx.com/X50'},
        )
        assert b'Login' not in response.content

        common = {
            'accion': 5,
            'buscar2': self.title,
            'masdesc': '',
        }

        for page_n in itertools.count(1):
            kwargs = {}
            if page_n == 1:
                http_method = self.session.post
                kwargs['data'] = common | {
                    'realiza_b': 1,
                    'subtitulos': 1,
                }
            else:
                http_method = self.session.get
                kwargs['params'] = common | {
                    'idusuario': '',
                    'nick': '',
                    'oxcd': '',
                    'oxdown': '',
                    'oxfecha': '',
                    'pg': page_n,
                }

            page = http_method(SEARCH_URL, **kwargs)

            if 'menu_detalle_buscador' not in page.text:
                return

            soup = bs4.BeautifulSoup(page.content, ENGINE, from_encoding=CHARACTER_ENCODING)

            title_sections = soup.find_all('div', id='menu_detalle_buscador')
            detail_sections = soup.find_all('div', id='buscador_detalle')

            for title_section, detail_section in zip(title_sections, detail_sections):
                found_in = None

                title_anchor = title_section.find('a')

                url = title_anchor['href']

                media_title = title_anchor.string
                media_title = media_title.removeprefix('Subtitulos de ')
                media_title = media_title.casefold()
                media_title = re.sub(' +', ' ', media_title)

                if self.strip_year:
                    media_title = media_title.rsplit('(', maxsplit=1)[0]

                if self.title not in media_title:
                    continue

                sub = detail_section.find('div', id='buscador_detalle_sub')
                if sub.string:
                    description = str(sub.string)
                else:
                    description = None

                if description and self.tag in description.casefold():
                    found_in = 'Description'
                elif detail_section.find('a', href=comment_url_re) and self._in_comments(url):
                    found_in = 'Comment'

                if found_in:
                    yield Match(str(title_anchor.string).removeprefix('Subtitulos de '), url, description, found_in)

    def _in_comments(self, url: str) -> bool:
        page = self.session.get(url)
        soup = bs4.BeautifulSoup(page.content, ENGINE, from_encoding=CHARACTER_ENCODING)

        for comment in soup.find_all('div', id='detalle_reng_coment1'):
            comment_string = comment.contents[0].string

            if comment_string is None:
                logger.error('Could not parse %s', url)
                continue

            if self.tag in comment_string.casefold():
                return True

        return False
