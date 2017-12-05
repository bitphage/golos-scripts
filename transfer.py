#!/usr/bin/env python

import sys
import json
import argparse
import logging
import yaml
from piston import Steem

log = logging.getLogger(__name__)

def transfer(steem_instance, account, to, amount, asset, memo):
    """ transfer ASSET to someone """

    try:
        log.info('transferring to {}: {} "{}"'.format(to, amount, asset, memo))
        steem_instance.transfer(to, amount, asset, memo=memo, account=account)
    except Exception as e:
        log.error(e)

def main():

    parser = argparse.ArgumentParser(
            description='transfer',
            epilog='Report bugs to: https://github.com/bitfag/golos-scripts/issues')
    parser.add_argument('-d', '--debug', action='store_true',
        help='enable debug output'),
    parser.add_argument('--broadcast', action='store_true', default=False,
            help='broadcast transactions'),
    parser.add_argument('-c', '--config', default='./common.yml',
            help='specify custom path for config file')
    parser.add_argument('f',
            help='from'),
    parser.add_argument('to',
            help='to'),
    parser.add_argument('amount',
            help='amount'),
    parser.add_argument('asset',
            help='asset'),
    parser.add_argument('memo',
            help='memo'),

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


    # initialize steem instance
    log.debug('broadcast: %s', args.broadcast)
    # toggle args.broadcast
    b = not args.broadcast
    golos = Steem(node=conf['nodes'], nobroadcast=b, keys=conf['keys'])

    transfer(golos, args.f, args.to, args.amount, args.asset, args.memo)


if __name__ == '__main__':
    main()
