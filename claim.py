#!/usr/bin/env python

import click
from golos.account import Account

from golosscripts.decorators import common_options, helper


@click.command()
@common_options
@helper
@click.option('--to', help='claim to another account')
@click.option('--amount', type=float, help='claim only specified amount, otherwise claim all')
@click.option('--to-vesting', is_flag=True, default=False, help='claim to vesting')
@click.argument('account')
@click.pass_context
def main(ctx, to, amount, to_vesting, account):
    """Claim funds from accumulative balance to tip balance or to vesting."""

    if not amount:
        account = Account(account)
        balance = account.get_balances()
        amount = balance['accumulative']['GOLOS']

    if not to:
        to = account

    ctx.helper.claim(to, amount, to_vesting=to_vesting, account=account)


if __name__ == '__main__':
    main()
