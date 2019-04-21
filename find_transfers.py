#!/usr/bin/env python

import sys
import json
import argparse
import logging
import yaml

from datetime import datetime
from pprint import pprint
from golos import Steem
from golos.account import Account
from golos.amount import Amount
from golos.converter import Converter

import functions

log = logging.getLogger('functions')


def main():

    parser = argparse.ArgumentParser(
        description='Scan account history looking for transfers',
        epilog='Report bugs to: https://github.com/bitfag/golos-scripts/issues',
    )
    parser.add_argument('-d', '--debug', action='store_true', help='enable debug output'),
    parser.add_argument('-c', '--config', default='./common.yml', help='specify custom path for config file')
    parser.add_argument(
        '-a', '--amount', type=float, default=0, help='minimal transfer amount to look for (default: 0)'
    )
    parser.add_argument('-l', '--limit', type=int, default=50, help='limit number of transactions to scan, default: 50')
    parser.add_argument('account', help='account to scan')
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
        conf = yaml.load(ymlfile)

    golos = Steem(nodes=conf['nodes_old'], keys=conf['keys'])

    account = Account(args.account, steemd_instance=golos)
    history = account.rawhistory(only_ops=['transfer'], limit=args.limit)

    for item in history:
        # pprint(item)

        timestamp = datetime.strptime(item[1]['timestamp'], '%Y-%m-%dT%H:%M:%S')
        t_from = item[1]['op'][1]['from']
        to = item[1]['op'][1]['to']
        amount = Amount(item[1]['op'][1]['amount'])

        if amount.amount > args.amount:
            print('{}: {:<16} -> {:<16}, {}'.format(timestamp, t_from, to, amount))


if __name__ == '__main__':
    main()
