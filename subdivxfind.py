import re
import sys
import urllib.parse
import urllib.request

import bs4
import html5lib

title, release = sys.argv[1:3]

engine = 'html5lib'

title = urllib.parse.quote_plus(title)
release = release.casefold()

description_length = 75

base = 'https://www.subdivx.com'
search_url = f'{base}/index.php?accion=5&buscar={title}&masdesc=&idusuario=&nick=&oxfecha=&oxcd=&oxdown=&pg='

page_n = 1

comment_url_re = re.compile(r'popcoment\.php')
download_url_re = re.compile(r'bajar\.php')

while True:
    with urllib.request.urlopen(f'{search_url}{page_n}') as page:
        page_content = page.read()

    if page_n == 1 and 'No encontramos resultados con el buscador de subdivx' in page_content.decode('latin_1'):
        print('No results.')
        break

    soup = bs4.BeautifulSoup(page_content, engine, from_encoding='latin_1')

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
            if release in description.casefold():
                found_in = 'description'
        else:
            description = ''

        if not found_in:
            comment_url = detail_section.find('a', href=comment_url_re)
            if comment_url:
                with urllib.request.urlopen(f'{base}/{comment_url["href"]}') as comment_page:
                    comment_page_content = comment_page.read()
                comment_soup = bs4.BeautifulSoup(comment_page_content, engine, from_encoding='latin_1')
                for comment in comment_soup.find_all('div', id='pop_upcoment'):
                    if release in comment.contents[0].string.casefold():
                        found_in = 'comments'
                        break

        if found_in:
            if len(description) > description_length:
                description = f'{description[:description_length - 3]}...'
            print('Title:      ', media_title)
            print('Page:       ', page_n)
            print('URL:        ', f'{search_url}{page_n}')
            print('Description:', description)
            print('Found in:   ', found_in)
            print('Download:   ', download_url)
            print()

    if page_n == last_page_n:
        break

    page_n += 1
