#!/usr/bin/env python

import sys
import json
import argparse
import logging
import yaml
import re

from piston import Steem
from piston.amount import Amount

import functions

log = logging.getLogger('functions')


def main():

    parser = argparse.ArgumentParser(
            description='Use this script to estimate potential upvote profit',
            epilog='Report bugs to: https://github.com/bitfag/golos-scripts/issues')
    parser.add_argument('-d', '--debug', action='store_true',
            help='enable debug output'),
    parser.add_argument('-c', '--config', default='./common.yml',
            help='specify custom path for config file')
    parser.add_argument('account',
            help='specify account which upvote should be estimated')
    parser.add_argument('-p', '--percent', default=100, type=float,
            help='specify upvote percent')
    parser.add_argument('--curve', default='linear', choices=['quadratic', 'linear'],
            help='select curve type')
    parser.add_argument('-u', '--url',
            help='post id in format @author/article or full url')
    args = parser.parse_args()

    # create logger
    if args.debug == True:
        log.setLevel(logging.DEBUG)
    else:
        log.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(levelname)s: %(message)s")
    handler.setFormatter(formatter)
    log.addHandler(handler)

    # parse config
    with open(args.config, 'r') as ymlfile:
        conf = yaml.load(ymlfile)

    golos = Steem(node=conf['nodes_old'], keys=conf['keys'])

    if args.curve == 'quadratic':
        if not args.url:
            log.critical('you need to provide --url when using quadratic curve')
            sys.exit(1)
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
        if not post:
            log.critical('could not find post in blockchain')
            sys.exit(1)

        # current post rshares
        net_rshares = int(post['net_rshares'])

        # current pending_payout_value, GBG
        current_pending_payout_value = post['pending_payout_value']
        log.info('current pending_payout_value: {}'.format(current_pending_payout_value))

        # estimate current expected author reward
        author_payout_gp, author_payout_gbg, author_payout_golos = functions.estimate_author_payout(golos, current_pending_payout_value)
        log.info('estimated author payout: {:.3f} GBG, {:.3f} GOLOS, {:.3f} GP'.format(
            author_payout_gbg, author_payout_golos, author_payout_gp))

        rshares = functions.calc_rshares(golos, args.account, args.percent)
        new_rshares = net_rshares + rshares

        new_payout = functions.calc_payout(golos, new_rshares)
        new_payout_gbg = functions.convert_golos_to_gbg(golos, new_payout, price_source='median')
        new_payout_gbg = Amount('{} GBG'.format(new_payout_gbg))
        log.info('new pending_payout_value: {}'.format(new_payout_gbg))

        payout_diff = new_payout_gbg.amount - current_pending_payout_value.amount
        log.info('pending_payout diff: {:.3f}'.format(payout_diff))

        # estimate new author reward
        author_payout_gp, author_payout_gbg, author_payout_golos = functions.estimate_author_payout(golos, new_payout_gbg)
        log.info('new estimated author payout: {:.3f} GBG, {:.3f} GOLOS, {:.3f} GP'.format(
            author_payout_gbg, author_payout_golos, author_payout_gp))

    elif args.curve == 'linear':

        rshares = functions.calc_rshares(golos, args.account, args.percent)
        payout = functions.calc_payout(golos, rshares)
        payout_gbg = functions.convert_golos_to_gbg(golos, payout, price_source='median')
        payout_gbg = Amount('{} GBG'.format(payout_gbg))
        author_payout_gp, author_payout_gbg, author_payout_golos = functions.estimate_author_payout(golos, payout_gbg)
        log.info('estimated author payout: {:.3f} GBG, {:.3f} GOLOS, {:.3f} GP'.format(
            author_payout_gbg, author_payout_golos, author_payout_gp))

        author_payout_gbg_repr = author_payout_gbg
        author_payout_gbg_repr += functions.convert_golos_to_gbg(golos, author_payout_golos, price_source='market')
        author_payout_gbg_repr += functions.convert_golos_to_gbg(golos, author_payout_gp, price_source='market')
        log.info('estimated author payout in GBG representation: {:.3f} GBG'.format(author_payout_gbg_repr))


if __name__ == '__main__':
    main()
