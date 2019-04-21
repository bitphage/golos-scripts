#!/usr/bin/env python

import sys
import json
import argparse
import logging
import yaml
import hashlib

from binascii import hexlify
from golos import Steem
from golosbase.account import PrivateKey, PublicKey

import functions

log = logging.getLogger('functions')


def main():

    parser = argparse.ArgumentParser(
        description='This script is for generating a keypair.',
        epilog='Report bugs to: https://github.com/bitfag/golos-scripts/issues',
    )
    parser.add_argument('-d', '--debug', action='store_true', help='enable debug output'),
    parser.add_argument('-c', '--config', default='./common.yml', help='specify custom path for config file')
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
        conf = yaml.safe_load(ymlfile)

    golos = Steem(nodes=conf['nodes_old'], no_broadcast=False, keys=conf['keys'])

    password = functions.generate_password()

    a = bytes(password, 'utf8')
    s = hashlib.sha256(a).digest()

    privkey = PrivateKey(hexlify(s).decode('ascii'))
    print('private: {}'.format(str(privkey)))  # we need explicit str() conversion!

    # pubkey with correct prefix
    key = format(privkey.pubkey, golos.chain_params["prefix"])
    print('public: {}'.format(key))


if __name__ == '__main__':
    main()
