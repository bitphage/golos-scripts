#!/usr/bin/env python

import sys
import json
import argparse
import logging
import yaml
from golos import Steem
from golos.amount import Amount
from pprint import pprint

import functions

log = logging.getLogger('functions')


def main():

    parser = argparse.ArgumentParser(
            description='Get witnesses price feed and estimate futher median price',
            epilog='Report bugs to: https://github.com/bitfag/golos-scripts/issues')
    parser.add_argument('-d', '--debug', action='store_true',
            help='enable debug output'),
    parser.add_argument('-c', '--config', default='./common.yml',
            help='specify custom path for config file')
    args = parser.parse_args()

    # create logger
    if args.debug == True:
        log.setLevel(logging.DEBUG)
    else:
        log.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(levelname)s: %(message)s")
    handler.setFormatter(formatter)
    log.addHandler(handler)

    # parse config
    with open(args.config, 'r') as ymlfile:
        conf = yaml.load(ymlfile)

    golos = Steem(nodes=conf['nodes_old'], keys=conf['keys'])

    if args.debug:
        verbose = True
    else:
        verbose = False

    log.info('current median price: {:.3f}'.format(functions.get_median_price(golos)))
    log.info('estimated median price: {:.3f}'.format(functions.estimate_median_price(golos, verbose=verbose)))
    log.info('estimated median price (from feed): {:.3f}'.format(functions.estimate_median_price_from_feed(golos)))

if __name__ == '__main__':
    main()
