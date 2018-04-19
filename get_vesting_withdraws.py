#!/usr/bin/env python

import sys
import json
import argparse
import logging
import yaml
from piston import Steem
from piston.account import Account
from piston.amount import Amount
from piston.converter import Converter
from pprint import pprint

from datetime import timedelta
from datetime import datetime

import functions

log = logging.getLogger('functions')

def main():

    parser = argparse.ArgumentParser(
            description='Find all vesting withdrawals with rates and dates',
            epilog='Report bugs to: https://github.com/bitfag/golos-scripts/issues')
    parser.add_argument('-d', '--debug', action='store_true',
            help='enable debug output'),
    parser.add_argument('-c', '--config', default='./common.yml',
            help='specify custom path for config file')
    parser.add_argument('-m', '--min-mgests', default=100, type=float,
            help='look for account with vesting shares not less than X MGESTS, default is 100')
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

    golos = Steem(node=conf['nodes_old'], keys=conf['keys'])

    c = golos.rpc.get_account_count(api='database_api')
    log.debug('total accounts: {}'.format(c))

    accs = golos.get_all_usernames()

    # we well get summary info about total withdrawal rate and number of accounts
    sum_rate = float()
    count = int()

    start = datetime.utcnow()
    for account in accs:
        a = Account(account, steem_instance=golos)
        cv = Converter(golos)
        vshares = Amount(a['vesting_shares'])
        mgests = vshares.amount / 1000000
        rate = Amount(a['vesting_withdraw_rate'])
        d = datetime.strptime(a['next_vesting_withdrawal'], '%Y-%m-%dT%H:%M:%S')

        if mgests > args.min_mgests and rate.amount > 1000:
            rate_gp = cv.vests_to_sp(rate.amount)
            gp = cv.vests_to_sp(vshares.amount)
            sum_rate += rate_gp
            count += 1

            print('{:<16} {:<18} {:>6.0f} {:>8.0f}'.format(
                                       account,
                                       d.strftime('%Y-%m-%d %H:%M'),
                                       rate_gp, gp))

# non-pretty format
#            log.info('{} {} {:.0f} / {:.0f}'.format(
#                                       account,
#                                       d.strftime('%Y-%m-%d %H:%M'),
#                                       rate_gp, gp))

    log.debug('accounts iteration took {:.2f} seconds'.format(
        (datetime.utcnow() - start).total_seconds()))

    log.info('numbers of matching accounts on vesting withdrawal: {}'.format(count))
    log.info('sum rate: {:.0f}'.format(sum_rate))


if __name__ == '__main__':
    main()
