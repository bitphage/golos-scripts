#!/usr/bin/env python

import argparse
import yaml
import logging

from piston import Steem
from piston.account import Account
from piston.converter import Converter
from pprint import pprint

log = logging.getLogger(__name__)

def main():

    parser = argparse.ArgumentParser(
            description='show multiple users balances',
            epilog='Report bugs to: https://github.com/bitfag/golos-scripts/issues')
    parser.add_argument('-c', '--config', default='./common.yml',
            help='specify custom path for config file')
    parser.add_argument('--no-header', action='store_true',
            help='supress header')
    parser.add_argument('--no-sum', action='store_true',
            help='supress summary output')
    parser.add_argument('-d', '--debug', action='store_true',
        help='enable debug output'),

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

    golos = Steem(node=conf['nodes_old'], nobroadcast=True)

    if not args.no_header:
        print('{:<20} {:>10} {:>11} {:>11}'.format('Account', 'GBG', 'GOLOS', 'GP'))
        print('--------------------')

    sum_gbg = float()
    sum_golos = float()
    sum_gp = float()
    for acc in conf['accs']:
        a = Account(acc, steem_instance=golos)
        b = a.get_balances()
        cv = Converter(golos)
        gp = cv.vests_to_sp(b['VESTS'].amount)

        total_sbd = b['SAVINGS_SBD'].amount + b['SBD'].amount
        total_steem = b['SAVINGS_STEEM'].amount + b['STEEM'].amount
        print('{:<20} {:>10}  {:>10}  {:>10.0f}'.format(acc, total_sbd, total_steem, gp))

        sum_gbg += total_sbd
        sum_golos += total_steem
        sum_gp += gp

    if not args.no_sum:
        print('--------------------')
        print('{:<20} {:>10.3f}  {:>10.3f}  {:>10.0f}'.format('Totals:', sum_gbg, sum_golos, sum_gp))


if __name__ == '__main__':
    main()
