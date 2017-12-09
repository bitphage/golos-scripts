#!/usr/bin/env python

import sys
import json
import argparse
import logging
import yaml
from piston import Steem

import functions

log = logging.getLogger('functions')


def main():

    parser = argparse.ArgumentParser(
            description='Calculate actual voting power',
            epilog='Report bugs to: https://github.com/bitfag/golos-scripts/issues')
    parser.add_argument('-d', '--debug', action='store_true',
            help='enable debug output'),
    parser.add_argument('-c', '--config', default='./common.yml',
            help='specify custom path for config file')
    parser.add_argument('account',
            help='specify account which VP should be estimated')

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

    golos = Steem(node=conf['nodes_old'], keys=conf['keys'])
    vp = functions.get_voting_power(golos, args.account)
    log.info('VP of {}: {:.2f}'.format(args.account, vp))


if __name__ == '__main__':
    main()
