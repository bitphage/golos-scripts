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
@click.argument('to')
@click.pass_context
def main(ctx, min_balance, to):
    """Withdraw from vesting balance of multiple accounts to specified account."""

    cv = ctx.helper.converter
    min_balance = cv.sp_to_vests(min_balance)

    for account in ctx.config['accs']:

        acc = Account(account)
        balance = acc.get_balances()
        vests = balance['available']['GESTS']
        withdraw_amount = vests - min_balance

        ctx.log.info(
            'withdrawing {:.4f} MGESTS ({:.3f} GOLOS): {} -> {}'.format(
                withdraw_amount / 1000000, cv.vests_to_sp(withdraw_amount), account, to
            )
        )
        ctx.helper.set_withdraw_vesting_route(to, percentage=100, account=account, auto_vest=False)
        ctx.helper.withdraw_vesting(withdraw_amount, account=account)


if __name__ == '__main__':
    main()
