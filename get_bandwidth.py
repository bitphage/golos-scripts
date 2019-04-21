#!/usr/bin/env python

import sys
import json
import argparse
import logging
import yaml
from golos import Steem
from golos.account import Account
from golos.amount import Amount

from datetime import datetime
from datetime import timedelta

import functions

log = logging.getLogger('functions')


def main():

    parser = argparse.ArgumentParser(
        description='Estimate current bandwidth usage for an account',
        epilog='Report bugs to: https://github.com/bitfag/golos-scripts/issues',
    )
    parser.add_argument('-c', '--config', default='./common.yml', help='specify custom path for config file')
    parser.add_argument(
        '-t',
        '--type',
        default='market',
        choices=['market', 'forum'],
        help='bandwidth type to estimate. Market - transfers, forum - posting ops',
    )
    parser.add_argument(
        '-w',
        '--warning',
        default=99,
        type=float,
        help='exit with 1 error code whether bandwidth exceeded specified percent',
    )
    parser.add_argument('account', help='specify account which bandwidth should be estimated')

    verbosity_args = parser.add_mutually_exclusive_group()
    verbosity_args.add_argument(
        '-q',
        '--quiet',
        action='store_true',
        help='do not show any output except errors, just return 0 if has_bandwidth or 1 if not',
    )
    verbosity_args.add_argument('-d', '--debug', action='store_true', help='enable debug output')
    args = parser.parse_args()

    # create logger
    if args.debug == True:
        log.setLevel(logging.DEBUG)
    else:
        log.setLevel(logging.INFO)
    if args.quiet == True:
        log.setLevel(logging.CRITICAL)

    handler = logging.StreamHandler()
    # formatter = logging.Formatter("%(levelname)s: %(message)s")
    # handler.setFormatter(formatter)
    log.addHandler(handler)

    # parse config
    with open(args.config, 'r') as ymlfile:
        conf = yaml.load(ymlfile)

    golos = Steem(nodes=conf['nodes_old'], keys=conf['keys'])

    ratio = functions.get_bandwidth(golos, args.account, args.type)

    if ratio > args.warning:
        log.warning('bandwidth usage ratio execeeded limit: {:.2f}'.format(ratio))
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()
