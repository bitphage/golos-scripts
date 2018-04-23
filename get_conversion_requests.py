#!/usr/bin/env python

import sys
import json
import argparse
import logging
import yaml
from piston import Steem
from piston.account import Account
from pprint import pprint

from datetime import timedelta
from datetime import datetime

import functions

log = logging.getLogger('functions')


def main():

    parser = argparse.ArgumentParser(
            description='Find all GBG conversion requests',
            epilog='Report bugs to: https://github.com/bitfag/golos-scripts/issues')
    parser.add_argument('-d', '--debug', action='store_true',
            help='enable debug output'),
    parser.add_argument('-c', '--config', default='./common.yml',
            help='specify custom path for config file')
    parser.add_argument('-n', '--notify', action='store_true',
            help='send message to accounts who uses conversions')
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

    golos = Steem(node=conf['nodes_old'], keys=conf['keys'])

    c = golos.rpc.get_account_count(api='database_api')
    log.debug('total accounts: {}'.format(c))

    accs = golos.get_all_usernames()

    # obtain median and market prices whether we're going to send a notification
    if args.notify:
        bid = functions.get_market_price(golos)
        median = functions.get_median_price(golos)
        if not bid or not median:
            log.critical('failed to obtain price')
            sys.exit(1)

    start = datetime.utcnow()
    for acc in accs:
        r = golos.rpc.get_conversion_requests(acc, api='database_api')
        if r:
            d = datetime.strptime(r[0]['conversion_date'], '%Y-%m-%dT%H:%M:%S')
            print('{:<16} {:<18} {:>7}'.format(
                                    r[0]['owner'],
                                    r[0]['amount'],
                                    d.strftime('%Y-%m-%d %H:%M')
                                    ))

            if args.notify:
                msg = conf['notify_message'].format(median, bid)
                functions.transfer(golos, conf['notify_account'], acc, '0.001', 'GBG', msg)

    log.debug('getting conversion requests took {:.2f} seconds'.format(
        (datetime.utcnow() - start).total_seconds()))

if __name__ == '__main__':
    main()
