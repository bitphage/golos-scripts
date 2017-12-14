#!/usr/bin/env python

import argparse
import yaml
import logging

from steem import Steem
from steem.account import Account
from steem.converter import Converter
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

    golos = Steem(nodes=conf['nodes_new'], no_broadcast=True)

    if not args.no_header:
        print('Account GBG GOLOS GP')
        print('--------------------')

    sum_gbg = float()
    sum_golos = float()
    sum_gp = float()
    for acc in conf['accs']:
        a = Account(acc, steemd_instance=golos)
        b = a.get_balances()
        vests = b['total']['GESTS']
        cv = Converter(golos)
        gp = cv.vests_to_sp(vests)
        print('{}   {}  {}  {:.0f}'.format(acc, b['total']['GBG'], b['total']['GOLOS'], gp))
        sum_gbg += b['total']['GBG']
        sum_golos += b['total']['GOLOS']
        sum_gp += gp

    if not args.no_sum:
        print('--------------------')
        print('Totals:')
        print('{:.3f}  {:.3f}  {:.0f}'.format(sum_gbg, sum_golos, sum_gp))


if __name__ == '__main__':
    main()
