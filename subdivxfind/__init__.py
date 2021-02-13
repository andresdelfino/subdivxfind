#!/usr/bin/env python

import argparse
import logging

from subdivxfind.finder import Finder


def main() -> None:
    logging.basicConfig()

    parser = argparse.ArgumentParser(description='Find subtitles in subdivx.')
    parser.add_argument('title', help='Media title')
    parser.add_argument('tag', help='Release tag')
    parser.add_argument('--strip-year', help='Strip year when searching title')

    args = parser.parse_args()

    matches_found = False

    finder = Finder(args.title, args.tag, args.strip_year)

    for match in finder.find():
        matches_found = True

        print('Title:      ', match.title)
        print('URL:        ', match.url)
        print('Description:', match.description)
        print('Found in:   ', match.found_in)
        print()

    if not matches_found:
        print('No results found.')


if __name__ == '__main__':
    main()
