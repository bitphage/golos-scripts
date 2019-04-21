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
        description='Scan account history looking for author or curator payouts',
        epilog='Report bugs to: https://github.com/bitfag/golos-scripts/issues',
    )
    parser.add_argument('-d', '--debug', action='store_true', help='enable debug output'),
    parser.add_argument('-c', '--config', default='./common.yml', help='specify custom path for config file')
    parser.add_argument(
        '-t',
        '--type',
        default='author',
        choices=['author', 'curator'],
        help='reward type, "author" or "curator", default: author',
    )
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

    if args.type == 'author':
        ops = ['author_reward']
    elif args.type == 'curator':
        ops = ['curation_reward']

    golos = Steem(nodes=conf['nodes_old'], keys=conf['keys'])
    cv = Converter(golos)

    account = Account(args.account, steemd_instance=golos)
    history = account.rawhistory(only_ops=ops)

    for item in history:
        # pprint(item)

        permlink = item[1]['op'][1]['permlink']
        payout_timestamp = datetime.strptime(item[1]['timestamp'], '%Y-%m-%dT%H:%M:%S')

        sbd_payout = Amount(item[1]['op'][1]['sbd_payout'])
        steem_payout = Amount(item[1]['op'][1]['steem_payout'])
        vesting_payout = Amount(item[1]['op'][1]['vesting_payout'])
        gp = cv.vests_to_sp(vesting_payout.amount)

        golos_payout = steem_payout.amount + gp
        gpg_repr = sbd_payout.amount + functions.convert_golos_to_gbg(golos, golos_payout, price_source='market')

        print(
            '{} {}: {} {} {:.3f} GP, GBG repr: {:.3f}'.format(
                payout_timestamp, permlink, sbd_payout, steem_payout, gp, gpg_repr
            )
        )


if __name__ == '__main__':
    main()
