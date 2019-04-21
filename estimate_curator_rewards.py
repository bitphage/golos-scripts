#!/usr/bin/env python

import sys
import json
import argparse
import logging
import yaml
import re

from datetime import datetime
from datetime import timedelta
from golos import Steem
from golos.amount import Amount

import functions

log = logging.getLogger('functions')


def main():

    parser = argparse.ArgumentParser(
        description='', epilog='Report bugs to: https://github.com/bitfag/golos-scripts/issues'
    )
    parser.add_argument('-d', '--debug', action='store_true', help='enable debug output'),
    parser.add_argument('-c', '--config', default='./common.yml', help='specify custom path for config file')
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

    golos = Steem(nodes=conf['nodes_old'], keys=conf['keys'])

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

    post = functions.get_post_content(golos, author, post_permlink)
    total_pending_payout_value = post['total_pending_payout_value'].amount
    from pprint import pprint

    # pprint(post)
    # pprint(post.export())
    if not post:
        log.critical('could not find post in blockchain')
        sys.exit(1)

    if post['mode'] != 'first_payout':
        log.critical('post already got a payout')
        sys.exit(1)

    total_vote_weight = int(post['total_vote_weight'])
    if total_vote_weight == 0:
        log.critical('curation rewards disabled')
        sys.exit(1)

    pending_payout = functions.convert_gbg_to_golos(golos, total_pending_payout_value)
    active_votes = sorted(post['active_votes'], key=lambda k: datetime.strptime(k['time'], '%Y-%m-%dT%H:%M:%S'))
    sum_weight = int()

    for vote in active_votes:
        sum_weight += int(vote['weight'])
        weight_pct = int(vote['weight']) / total_vote_weight
        reward = pending_payout * 0.25 * weight_pct
        time_passed = datetime.strptime(vote['time'], '%Y-%m-%dT%H:%M:%S') - post['created']
        print(
            'weight percent: {:.2%}, reward: {:.3f} GP, voter: {:<16}, time: {}, weight: {:.2f}'.format(
                weight_pct, reward, vote['voter'], time_passed, float(vote['weight']) / 100000000000000
            )
        )

    curators_pct = sum_weight / int(post['total_vote_weight']) * 0.25
    print('curation real percent: {:.4%}'.format(curators_pct))


if __name__ == '__main__':
    main()
