#!/usr/bin/env python

import argparse
import yaml

from piston import Steem
from piston.account import Account
from piston.converter import Converter
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

    golos = Steem(node=conf['nodes_old'], nobroadcast=True)

    a = Account(args.account, steem_instance=golos)
    b = a.get_balances()
    cv = Converter(golos)
    gp = cv.vests_to_sp(b['VESTS'].amount)

    print('{:<15}{:>18.3f}'.format('SAVINGS_{}:'.format(b['SAVINGS_SBD'].asset), b['SAVINGS_SBD'].amount))
    print('{:<15}{:>18.3f}'.format('SAVINGS_{}:'.format(b['SAVINGS_STEEM'].asset), b['SAVINGS_STEEM'].amount))
    print('{:<15}{:>18.3f}'.format('{}:'.format(b['SBD'].asset), b['SBD'].amount))
    print('{:<15}{:>18.3f}'.format('{}:'.format(b['STEEM'].asset), b['STEEM'].amount))
    print('{:<15}{:>18.3f}'.format('GP:', gp, b['STEEM'].asset))
    print('{:<15}{:>18.3f}'.format('M{}:'.format(b['VESTS'].asset), b['VESTS'].amount/1000000))

if __name__ == '__main__':
    main()
