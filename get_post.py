#!/usr/bin/env python

import argparse
import yaml
import re
import logging
import sys

from golos import Steem
from pprint import pprint

import functions

log = logging.getLogger(__name__)


def main():

    parser = argparse.ArgumentParser(description='get post with metadata', epilog='Report bugs to: ')
    parser.add_argument('--tags-only', action='store_true', help='show only post tags')
    parser.add_argument('--body', action='store_true', help='show only body')
    parser.add_argument('-c', '--config', default='./common.yml', help='specify custom path for config file')
    parser.add_argument('-d', '--debug', action='store_true', help='enable debug output'),
    parser.add_argument('url', help='post id in format @author/article or full url')
    args = parser.parse_args()

    # create logger
    if args.debug == True:
        log.setLevel(logging.DEBUG)
    else:
        log.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s")
    handler.setFormatter(formatter)
    log.addHandler(handler)

    # parse config
    with open(args.config, 'r') as ymlfile:
        conf = yaml.safe_load(ymlfile)

    # extract author and post permlink from args.url
    p = re.search('@(.*?)/([^/]+)', args.url)
    if p == None:
        log.critical('Wrong post id specified')
        sys.exit(1)
    else:
        author = p.group(1)
        log.debug('author: {}'.format(author))

        post_permlink = p.group(2)
        log.debug('permlink: {}'.format(post_permlink))

    golos = Steem(nodes=conf['nodes_old'])
    post = functions.get_post_content(golos, author, post_permlink)

    if not post:
        sys.exit(1)

    if args.tags_only:
        pprint(post['tags'])
    elif args.body:
        print(post['body'])
    else:
        pprint(dict(post))


if __name__ == '__main__':
    main()
