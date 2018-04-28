#!/usr/bin/env python

import sys
import json
import argparse
import logging
import yaml
from piston import Steem
from pistonbase.account import PasswordKey, PublicKey, PrivateKey

import functions

log = logging.getLogger('functions')

def main():

    parser = argparse.ArgumentParser(
            description='Create account',
            epilog='Report bugs to: https://github.com/bitfag/golos-scripts/issues')
    parser.add_argument('-d', '--debug', action='store_true',
                        help='enable debug output')
    parser.add_argument('-c', '--config', default='./common.yml',
                        help='specify custom path for config file')
    parser.add_argument('-p', '--password',
                        help='manually specify a password')
    parser.add_argument('creator',
                        help='parent account who will create child account')
    parser.add_argument('account',
                        help='new account name')
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

    # random password
    if args.password:
        password = args.password
    else:
        password = functions.generate_password()

    print('password: {}\n'.format(password))

    golos.create_account(args.account, creator=args.creator, password=password)

if __name__ == '__main__':
    main()
