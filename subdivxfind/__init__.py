#!/usr/bin/env python

import argparse
import logging

from subdivxfind.finder import Finder


def main() -> None:
    logging.basicConfig()

    parser = argparse.ArgumentParser(description='Find subtitles in subdivx.')
    parser.add_argument('--strip-year', help='Strip year when searching title')
    parser.add_argument('title', help='Media title')
    parser.add_argument('tag', help='Release tag')

    args = parser.parse_args()

    matches_found = False

    finder = Finder(args.title, args.tag, args.strip_year)

    for match in finder.find():
        print('Title:      ', match.title)
        print('URL:        ', match.url)
        print('Description:', match.description)
        print('Found in:   ', match.found_in)
        print()


if __name__ == '__main__':
    main()
