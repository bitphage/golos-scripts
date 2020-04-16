#!/usr/bin/env python

import argparse
import yaml
from golos import Steem
from golos.block import Block
from pprint import pprint


def main():

    parser = argparse.ArgumentParser(
        description='', epilog='Report bugs to: https://github.com/bitfag/golos-scripts/issues',
    )
    parser.add_argument('-c', '--config', default='./common.yml', help='specify custom path for config file')
    parser.add_argument('block', help='block')
    args = parser.parse_args()

    # parse config
    with open(args.config, 'r') as ymlfile:
        conf = yaml.safe_load(ymlfile)

    golos = Steem(nodes=conf['nodes_old'], keys=conf['keys'])

    block = Block(args.block, steemd_instance=golos)
    pprint(block)


if __name__ == '__main__':
    main()
