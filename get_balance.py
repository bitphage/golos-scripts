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

    print('{:<15}{:>18.3f}'.format('To claim GOLOS:', balance['accumulative']['GOLOS']))
    print('{:<15}{:>18.3f}'.format('Tip GOLOS:', balance['tip']['GOLOS']))

    for asset in balance['savings']:
        print('{:<15}{:>18.3f}'.format('SAVINGS_{}'.format(asset), balance['savings'][asset]))

    for asset in balance['available']:
        print('{:<15}{:>18.3f}'.format('{}:'.format(asset), balance['available'][asset]))

    gp = ctx.helper.converter.vests_to_sp(balance['total']['GESTS'])
    print('{:<15}{:>18.3f}'.format('GP:', gp))
    print('{:<15}{:>18.3f}'.format('MGESTS:', balance['total']['GESTS'] / 1000000))


if __name__ == '__main__':
    main()
