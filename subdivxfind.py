import collections
import re
import urllib

import bs4
import requests


Match = collections.namedtuple('Match', ['title', 'url', 'description', 'found_in', 'download_url'])

engine = 'html5lib'
base = 'https://www.subdivx.com'
search_url = f'{base}/index.php'

comment_url_re = re.compile(r'popcoment\.php')
download_url_re = re.compile(r'bajar\.php')

no_results_message = 'No encontramos resultados con el buscador de subdivx'


def _in_comments(url, tag):
    comment_page = requests.get(url)
    comment_soup = bs4.BeautifulSoup(comment_page.content, engine, from_encoding='latin_1')

    for comment in comment_soup.find_all('div', id='pop_upcoment'):
        if tag in comment.contents[0].string.casefold():
            return True

    return False


def find(title, tag, strip_year=False):
    tag = tag.casefold()

    params = {
        'accion': 5,
        'buscar': title,
        'masdesc': '',
        'idusuario': '',
        'nick': '',
        'oxfecha': '',
        'oxcd': '',
        'oxdown': '',
    }

    page_n = 1
    while True:
        params['pg'] = page_n
        page = requests.get(search_url, params=params)

        if page_n == 1 and no_results_message in page.text:
            return

        soup = bs4.BeautifulSoup(page.content, engine, from_encoding='latin_1')

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

            if strip_year:
                # Remove year from title
                media_title = media_title.rsplit('(', maxsplit=1)[0]
                media_title = media_title.rstrip()

            if title not in media_title:
                continue

            download_url = ''  # detail_section.find('a', href=download_url_re)['href']

            sub = detail_section.find('div', id='buscador_detalle_sub')
            if sub.string:
                description = sub.string
            else:
                description = ''

            if tag in description.casefold():
                found_in = 'description'
            else:
                comments_url = detail_section.find('a', href=comment_url_re)
                if comments_url and _in_comments(f'{base}/{comments_url["href"]}', tag):
                    found_in = 'comments'

            if found_in:
                query = urllib.parse.urlencode(params)
                yield Match(media_title, url, description, found_in, download_url)

        if page_n == last_page_n:
            break

        page_n += 1
