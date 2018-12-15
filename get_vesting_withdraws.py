#!/usr/bin/env python

import sys
import json
import argparse
import logging
import yaml
from golos import Steem
from golos.account import Account
from golos.amount import Amount
from golos.converter import Converter
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
    parser.add_argument('-a', '--account',
            help='get info for single account')
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

    c = golos.get_account_count()
    log.debug('total accounts: {}'.format(c))

    if args.account:
        accs = [args.account]
    else:
        accs = golos.get_all_usernames()

    start = datetime.utcnow()

    # get all accounts in one batch
    all_accounts = golos.get_accounts(accs)

    # we well get summary info about total withdrawal rate and number of accounts
    sum_rate = float()
    count = int()

    cv = Converter(golos)
    steem_per_mvests = cv.steem_per_mvests()

    for a in all_accounts:
        vshares = Amount(a['vesting_shares'])
        mgests = vshares.amount / 1000000
        rate = Amount(a['vesting_withdraw_rate'])
        d = datetime.strptime(a['next_vesting_withdrawal'], '%Y-%m-%dT%H:%M:%S')

        if mgests > args.min_mgests and rate.amount > 1000:
            # We use own calculation instead of cv.vests_to_sp() to speed up execution
            # avoiding API call on each interation
            rate_gp = rate.amount / 1e6 * steem_per_mvests
            gp = vshares.amount / 1e6 * steem_per_mvests
            sum_rate += rate_gp
            count += 1

            print('{:<16} {:<18} {:>6.0f} {:>8.0f}'.format(
                                       a['name'],
                                       d.strftime('%Y-%m-%d %H:%M'),
                                       rate_gp, gp))

# non-pretty format
#            log.info('{} {} {:.0f} / {:.0f}'.format(
#                                       a['name'],
#                                       d.strftime('%Y-%m-%d %H:%M'),
#                                       rate_gp, gp))

    log.debug('accounts iteration took {:.2f} seconds'.format(
        (datetime.utcnow() - start).total_seconds()))

    log.info('numbers of matching accounts on vesting withdrawal: {}'.format(count))
    log.info('sum rate: {:.0f}'.format(sum_rate))


if __name__ == '__main__':
    main()
