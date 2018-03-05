#!/usr/bin/env python

import sys
import json
import argparse
import logging
import yaml
import traceback
from piston import Steem
from piston.account import Account
from piston.converter import Converter

log = logging.getLogger(__name__)

def main():

    parser = argparse.ArgumentParser(
            description='withdraw from vesting balance of multiple accounts to specified account',
            epilog='Report bugs to: https://github.com/bitfag/golos-scripts/issues')
    parser.add_argument('-d', '--debug', action='store_true',
        help='enable debug output'),
    parser.add_argument('--broadcast', action='store_true', default=False,
            help='broadcast transactions'),
    parser.add_argument('-c', '--config', default='./common.yml',
            help='specify custom path for config file')
    parser.add_argument('-m', '--min-balance', default=5, type=float,
            help='minimal Golos Power balance which will be left on withdrawing account')
    parser.add_argument('to',
            help='to'),
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
    golos = Steem(node=conf['nodes_old'], nobroadcast=b, keys=conf['keys'])

    cv = Converter(golos)
    min_balance = cv.sp_to_vests(args.min_balance)

    for account in conf['accs']:

        b = golos.get_balances(account=account)
        vests = b['vesting_shares']
        withdraw_amount = vests - min_balance

        log.info('withdrawing {:.4f} MGESTS ({:.3f} GOLOS): {} -> {}'.format(
                                                              withdraw_amount.amount/1000000,
                                                              cv.vests_to_sp(withdraw_amount.amount),
                                                              account,
                                                              args.to
                                                              ))
        golos.set_withdraw_vesting_route(args.to, percentage=100, account=account, auto_vest=False)
        golos.withdraw_vesting(withdraw_amount.amount, account=account)

if __name__ == '__main__':
    main()
