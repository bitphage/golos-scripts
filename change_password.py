#!/usr/bin/env python

import sys
from pprint import pformat
from typing import List, Tuple

import click
from bitsharesscripts.functions import generate_password, get_keys_from_password
from golosbase.operations import AccountUpdate

from golosscripts.decorators import common_options, helper
from golosscripts.helper import key_types


@click.command()
@common_options
@helper
@click.option('-p', '--password', help='manually specify a password (if not, a random will be generated)')
@click.option('--broadcast', default=False, is_flag=True, help='broadcast transaction')
@click.argument('account_name')
@click.pass_context
def main(ctx, broadcast, password, account_name):
    """
    Change account keys derived from password.

    By default, random password is geneeated
    """

    if not password:
        password = generate_password()

    print('password: {}\n'.format(password))

    prefix = ctx.helper.steemd.chain_params["prefix"]
    keys = get_keys_from_password(account_name, password, prefix, key_types=key_types)

    # prepare for json format
    owner_key_authority = [(keys['owner'], 1)]
    active_key_authority = [(keys['active'], 1)]
    posting_key_authority = [(keys['posting'], 1)]
    owner_accounts_authority: List[Tuple[str, int]] = []
    active_accounts_authority: List[Tuple[str, int]] = []
    posting_accounts_authority: List[Tuple[str, int]] = []

    pre_op = {
        'account': account_name,
        'memo_key': keys['memo'],
        'owner': {'account_auths': owner_accounts_authority, 'key_auths': owner_key_authority, 'weight_threshold': 1},
        'active': {
            'account_auths': active_accounts_authority,
            'key_auths': active_key_authority,
            'weight_threshold': 1,
        },
        'posting': {
            'account_auths': posting_accounts_authority,
            'key_auths': posting_key_authority,
            'weight_threshold': 1,
        },
        'prefix': prefix,
    }

    op = AccountUpdate(**pre_op)
    ctx.log.debug(pformat(op.json()))

    if not broadcast:
        ctx.log.info('Not broadcasting!')
        sys.exit(0)

    ctx.helper.finalizeOp(op, account_name, "owner")


if __name__ == '__main__':
    main()
