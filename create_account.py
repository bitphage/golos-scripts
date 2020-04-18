#!/usr/bin/env python

import sys

import click
from bitsharesscripts.functions import generate_password, get_keys_from_password

from golosscripts.decorators import common_options, helper
from golosscripts.helper import key_types


@click.command()
@common_options
@helper
@click.option('-p', '--password', help='manually specify a password (if not, a random will be generated)')
@click.option('--broadcast', default=False, is_flag=True, help='broadcast transaction')
@click.argument('creator')
@click.argument('account')
@click.pass_context
def main(ctx, broadcast, password, creator, account):
    """
    Create new account.

    CREATOR is parent account who will create child account

    ACCOUNT is new account name
    """

    if not password:
        password = generate_password()

    print('password: {}\n'.format(password))
    # prints keys to stdout
    prefix = ctx.helper.steemd.chain_params["prefix"]
    get_keys_from_password(account, password, prefix, key_types=key_types)

    if not broadcast:
        ctx.log.info('Not broadcasting!')
        sys.exit(0)

    ctx.helper.create_account(account, creator=creator, password=password)


if __name__ == '__main__':
    main()
