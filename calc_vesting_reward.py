#!/usr/bin/env python

import argparse
import logging
import yaml

from golos import Steem
from golos.account import Account
from golos.amount import Amount


log = logging.getLogger('functions')


def main():

    parser = argparse.ArgumentParser(
        description='', epilog='Report bugs to: https://github.com/bitfag/golos-scripts/issues'
    )
    parser.add_argument('-d', '--debug', action='store_true', help='enable debug output'),
    parser.add_argument('-c', '--config', default='./common.yml', help='specify custom path for config file')
    parser.add_argument('account')
    args = parser.parse_args()

    # create logger
    if args.debug is True:
        log.setLevel(logging.DEBUG)
    else:
        log.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s")
    handler.setFormatter(formatter)
    log.addHandler(handler)

    # parse config
    with open(args.config, 'r') as ymlfile:
        conf = yaml.safe_load(ymlfile)

    golos = Steem(nodes=conf['nodes_old'], keys=conf['keys'])
    props = golos.get_dynamic_global_properties()
    a = Account(args.account, steemd_instance=golos)
    b = a.get_balances()
    account_vesting = b['total']['GESTS']
    vesting_fund = Amount(props['total_vesting_shares'])
    log.info('%s vesting share: %s', args.account, account_vesting / vesting_fund.amount)


if __name__ == '__main__':
    main()
