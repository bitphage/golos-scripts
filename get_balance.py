#!/usr/bin/env python

import click
from golos.account import Account

from golosscripts.decorators import common_options, helper


@click.command()
@common_options
@helper
@click.argument('account')
@click.pass_context
def main(ctx, account):
    """Show account balances."""

    account = Account(account)
    balance = account.get_balances()
    gp = ctx.helper.converter.vests_to_sp(balance['total']['GESTS'])

    for asset in balance['savings']:
        print('{:<15}{:>18.3f}'.format('SAVINGS_{}'.format(asset), balance['savings'][asset]))
    for asset in balance['total']:
        print('{:<15}{:>18.3f}'.format('{}:'.format(asset), balance['available'][asset]))

    print('{:<15}{:>18.3f}'.format('GP:', gp))
    print('{:<15}{:>18.3f}'.format('MGESTS:', balance['total']['GESTS'] / 1000000))


if __name__ == '__main__':
    main()
