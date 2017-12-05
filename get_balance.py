#!/usr/bin/env python

import argparse
import yaml

from steem import Steem
from steem.account import Account
from steem.converter import Converter
from pprint import pprint

def main():

    parser = argparse.ArgumentParser(
            description='show user balances',
            epilog='Report bugs to: https://github.com/bitfag/golos-scripts/issues')
    parser.add_argument('account',
            help='account name')
    parser.add_argument('-c', '--config', default='./common.yml',
            help='specify custom path for config file')
    args = parser.parse_args()

    # parse config
    with open(args.config, 'r') as ymlfile:
        conf = yaml.load(ymlfile)

    golos = Steem(nodes=conf['nodes_new'], no_broadcast=True)

    a = Account(args.account, steemd_instance=golos)
    b = a.get_balances()
    pprint(b)

    vests = b['total']['GESTS']
    cv = Converter(golos)
    pprint('GP: {}'.format(cv.vests_to_sp(vests)))


if __name__ == '__main__':
    main()
