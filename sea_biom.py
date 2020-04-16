#!/usr/bin/env python

import argparse
import logging
import yaml
from golos import Steem
from golos.converter import Converter


log = logging.getLogger('functions')


def main():

    parser = argparse.ArgumentParser(
        description='', epilog='Report bugs to: https://github.com/bitfag/golos-scripts/issues'
    )
    parser.add_argument('-d', '--debug', action='store_true', help='enable debug output'),
    parser.add_argument('-c', '--config', default='./common.yml', help='specify custom path for config file')
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
    cv = Converter(golos)
    spmv = cv.steem_per_mvests()

    print('fish: {:.0f}'.format(spmv * 1))
    print('dolphin: {:.0f}'.format(spmv * 10))
    print('orca: {:.0f}'.format(spmv * 100))
    print('whale: {:.0f}'.format(spmv * 1000))


if __name__ == '__main__':
    main()
