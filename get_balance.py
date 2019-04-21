#!/usr/bin/env python

import argparse
import yaml

from golos import Steem
from golos.account import Account
from golos.converter import Converter
from pprint import pprint


def main():

    parser = argparse.ArgumentParser(
        description='show user balances', epilog='Report bugs to: https://github.com/bitfag/golos-scripts/issues'
    )
    parser.add_argument('account', help='account name')
    parser.add_argument('-c', '--config', default='./common.yml', help='specify custom path for config file')
    args = parser.parse_args()

    # parse config
    with open(args.config, 'r') as ymlfile:
        conf = yaml.load(ymlfile)

    golos = Steem(nodes=conf['nodes_old'], no_broadcast=True)

    a = Account(args.account, steemd_instance=golos)
    b = a.get_balances()
    cv = Converter(golos)
    gp = cv.vests_to_sp(b['total']['GESTS'])

    for asset in b['savings']:
        print('{:<15}{:>18.3f}'.format('SAVINGS_{}'.format(asset), b['savings'][asset]))
    for asset in b['total']:
        print('{:<15}{:>18.3f}'.format('{}:'.format(asset), b['available'][asset]))

    print('{:<15}{:>18.3f}'.format('GP:', gp))
    print('{:<15}{:>18.3f}'.format('MGESTS:', b['total']['GESTS'] / 1000000))


if __name__ == '__main__':
    main()
