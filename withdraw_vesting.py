#!/usr/bin/env python

import sys
import json
import argparse
import logging
import yaml
import traceback
from golos import Steem
from golos.account import Account
from golos.converter import Converter

log = logging.getLogger(__name__)

def main():

    parser = argparse.ArgumentParser(
            description='withdraw from vesting balance of one account to specified account',
            epilog='Report bugs to: https://github.com/bitfag/golos-scripts/issues')
    parser.add_argument('-d', '--debug', action='store_true',
        help='enable debug output'),
    parser.add_argument('--broadcast', action='store_true', default=False,
            help='broadcast transactions'),
    parser.add_argument('-c', '--config', default='./common.yml',
            help='specify custom path for config file')
    parser.add_argument('-m', '--min-balance', default=5, type=float,
            help='minimal Golos Power balance which will be left on withdrawing account')
    parser.add_argument('-t', '--to',
            help='destination account (optional)'),
    parser.add_argument('account',
            help='account to withdraw from')
    args = parser.parse_args()

    # CREATE logger
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

    # initialize steem instance
    log.debug('broadcast: %s', args.broadcast)
    # toggle args.broadcast
    b = not args.broadcast
    golos = Steem(nodes=conf['nodes_old'], no_broadcast=b, keys=conf['keys'])

    account = args.account

    cv = Converter(golos)
    min_balance = cv.sp_to_vests(args.min_balance)

    b = golos.get_balances(account=account)
    vests = b['available']['GESTS']
    withdraw_amount = vests - min_balance

    if args.to:
        golos.set_withdraw_vesting_route(args.to, percentage=100, account=account, auto_vest=False)
        to = args.to
    else:
        to = account


    log.info('withdrawing {:.4f} MGESTS ({:.3f} GOLOS): {} -> {}'.format(
        withdraw_amount.amount/1000000,
        cv.vests_to_sp(withdraw_amount.amount),
        account,
        to))
    golos.withdraw_vesting(withdraw_amount.amount, account=account)

if __name__ == '__main__':
    main()
