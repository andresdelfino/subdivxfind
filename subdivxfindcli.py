import argparse

import subdivxfind


def main():
    parser = argparse.ArgumentParser(description='Find subtitles in subdivx.')
    parser.add_argument('title', help='Media title')
    parser.add_argument('tag', help='Release tag.')

    args = parser.parse_args()

    description_length = 75

    matches_found = False

    for match in subdivxfind.find(args.title, args.tag):
        matches_found = True

        if len(match.description) > description_length:
            description = f'{match.description[:description_length - 3]}...'

        print('Title:      ', match.media_title)
        print('Page:       ', match.page_n)
        print('URL:        ', match.url)
        print('Description:', match.description)
        print('Found in:   ', match.found_in)
        print('Download:   ', match.download_url)
        print()

    if not matches_found:
        print('No results found.')


if __name__ == '__main__':
    main()

