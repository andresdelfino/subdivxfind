import collections
import re
import urllib.parse

import bs4
import requests


Match = collections.namedtuple('Match', ['media_title', 'page_n', 'url',
                                         'description', 'found_in',
                                         'download_url'])

def find(title, tag, credentials):
    engine = 'html5lib'

    tag = tag.casefold()

    base = 'https://www.subdivx.com'
    search_url = f'{base}/index.php'

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

    comment_url_re = re.compile(r'popcoment\.php')
    download_url_re = re.compile(r'bajar\.php')

    no_results_message = 'No encontramos resultados con el buscador de subdivx'

    session = requests.Session()
    session.headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:63.0) Gecko/20100101 Firefox/63.0'}

    data = {
        'usuario': credentials[0],
        'clave': credentials[1],
        'Enviar': 'Entrar',
        'accion': '50',
        'enviau': '1',
        'refer': f'{base}/index.php?abandon=1',
    }

    session.get(f'{base}/index.php')
    print(session.cookies)
    session.get(f'{base}/X50')
    print(session.cookies)
    session.post(f'{base}/index.php', data)
    print(session.cookies)
    raise

    page_n = 1
    while True:
        params['pg'] = page_n
        page = session.get(search_url, params=params)

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
            found_in = ''

            media_title = title_section.find('a').string[13:]
            download_url = detail_section.find('a', href=download_url_re)['href']

            sub = detail_section.find('div', id='buscador_detalle_sub')
            if sub.string:
                description = sub.string
                if tag in description.casefold():
                    found_in = 'description'
            else:
                description = ''

            if not found_in:
                comment_url = detail_section.find('a', href=comment_url_re)
                if comment_url:
                    comment_page = session.get(f'{base}/{comment_url["href"]}')
                    comment_soup = bs4.BeautifulSoup(comment_page.content, engine, from_encoding='latin_1')
                    for comment in comment_soup.find_all('div', id='pop_upcoment'):
                        if tag in comment.contents[0].string.casefold():
                            found_in = 'comments'
                            break

            if found_in:
                query = urllib.parse.urlencode(params)

                yield Match(media_title, page_n, f'{search_url}?{query}',
                              description, found_in, download_url)

        if page_n == last_page_n:
            break

        page_n += 1

