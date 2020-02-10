#!/usr/bin/env python

import argparse
import logging
import yaml

from golos import Steem
from golos.converter import Converter
from golos.amount import Amount


log = logging.getLogger('functions')


def main():

    parser = argparse.ArgumentParser(
        description='', epilog='Report bugs to: https://github.com/bitfag/golos-scripts/issues'
    )
    parser.add_argument('-d', '--debug', action='store_true', help='enable debug output'),
    parser.add_argument('-c', '--config', default='./common.yml', help='specify custom path for config file')
    parser.add_argument('-g', '--gests', action='store_true', help='amount in GESTS (default: amount in Golos Power)')
    parser.add_argument('f', help='account name to delegate from'),
    parser.add_argument('to', help='account name to delegate to'),
    parser.add_argument('amount', type=float, help='amount (default: amount in Golos Power)'),
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

    if args.gests:
        gests = args.amount
    else:
        cv = Converter(golos)
        gests = cv.sp_to_vests(args.amount)

    gests = Amount('{} GESTS'.format(gests))
    golos.delegate_vesting_shares(args.to, gests, account=args.f)


if __name__ == '__main__':
    main()
