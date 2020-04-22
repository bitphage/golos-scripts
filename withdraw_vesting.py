#!/usr/bin/env python

import click
from golos.account import Account

from golosscripts.decorators import common_options, helper


@click.command()
@common_options
@helper
@click.option(
    '-m',
    '--min-balance',
    default=5,
    type=float,
    help='minimal Golos Power balance to keep on withdrawing account (default: 5)',
)
@click.option('-t', '--to', type=str, help='destination account (optional)')
@click.argument('account')
@click.pass_context
def main(ctx, min_balance, to, account):
    """Withdraw from vesting balance of one account to specified account."""

    cv = ctx.helper.converter
    min_balance = cv.sp_to_vests(min_balance)

    acc = Account(account)
    balance = acc.get_balances()

    vests = balance['available']['GESTS']
    withdraw_amount = vests - min_balance

    if to:
        ctx.helper.set_withdraw_vesting_route(to, percentage=100, account=account, auto_vest=False)
    else:
        to = account

    ctx.log.info(
        'withdrawing {:.4f} MGESTS ({:.3f} GOLOS): {} -> {}'.format(
            withdraw_amount / 1000000, cv.vests_to_sp(withdraw_amount), account, to
        )
    )
    ctx.helper.withdraw_vesting(withdraw_amount, account=account)


if __name__ == '__main__':
    main()
