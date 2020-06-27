import collections
import re
import urllib

import bs4
import requests

from constants import (
    BASE,
    ENGINE,
    NO_RESULTS_MESSAGE,
    SEARCH_URL,
)


Match = collections.namedtuple('Match', ['title', 'url', 'description', 'found_in', 'download_url'])

comment_url_re = re.compile(r'popcoment\.php')
download_url_re = re.compile(r'bajar\.php')


class Finder:
    def __init__(self, title, tag, strip_year=False):
        self.title = title.casefold()
        self.tag = tag.casefold()
        self.strip_year = strip_year

    def find(self):
        params = {
            'accion': 5,
            'buscar': self.title,
            'masdesc': '',
            'subtitulos': 1,
            'realiza_b': 1,
        }

        self.session = requests.Session()

        page_n = 1
        while True:
            params['pg'] = page_n
            page = self.session.get(SEARCH_URL, params=params)

            if page_n == 1 and NO_RESULTS_MESSAGE in page.text:
                return

            soup = bs4.BeautifulSoup(page.content, ENGINE, from_encoding='latin_1')

            if page_n == 1:
                pagination = soup.find('div', class_='pagination')
                if pagination.contents:
                    last_page_n = int(pagination.find_all('a')[-2].string)
                else:
                    last_page_n = 1

            title_list = soup.find_all('div', id='menu_detalle_buscador')
            detail_list = soup.find_all('div', id='buscador_detalle')

            for title_section, detail_section in zip(title_list, detail_list):
                found_in = None

                title_anchor = title_section.find('a')

                url = title_anchor['href']

                media_title = title_anchor.string
                media_title = media_title.replace('Subtitulos de ', '')
                media_title = media_title.casefold()

                if self.strip_year:
                    # Remove year from title
                    media_title = media_title.rsplit('(', maxsplit=1)[0]
                    media_title = media_title.rstrip()

                if self.title not in media_title:
                    continue

                # detail_section.find('a', href=download_url_re)['href']
                download_url = ''

                sub = detail_section.find('div', id='buscador_detalle_sub')
                if sub.string:
                    description = sub.string
                else:
                    description = ''

                if self.tag in description.casefold():
                    found_in = 'description'
                else:
                    comments_url = detail_section.find('a', href=comment_url_re)
                    if comments_url and self._in_comments(f'{BASE}/{comments_url["href"]}'):
                        found_in = 'comments'

                if found_in:
                    query = urllib.parse.urlencode(params)
                    yield Match(media_title, url, description, found_in, download_url)

            if page_n == last_page_n:
                break

            page_n += 1

    def _in_comments(self, url):
        comment_page = self.session.get(url)
        comment_soup = bs4.BeautifulSoup(comment_page.content, ENGINE, from_encoding='latin_1')

        for comment in comment_soup.find_all('div', id='pop_upcoment'):
            if self.tag in comment.contents[0].string.casefold():
                return True

        return False
