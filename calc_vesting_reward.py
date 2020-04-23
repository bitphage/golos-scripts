#!/usr/bin/env python

import click
from golos.account import Account
from golos.amount import Amount

from golosscripts.decorators import common_options, helper


@click.command()
@common_options
@helper
@click.argument('account')
@click.pass_context
def main(ctx, account):
    """Calculate profit from vesting holdings."""
    props = ctx.helper.get_dynamic_global_properties()
    acc = Account(account)
    balance = acc.get_balances()
    account_vesting = balance['total']['GESTS']
    vesting_fund = Amount(props['total_vesting_shares'])

    daily_emission = ctx.helper.calc_inflation()
    vesting_share = account_vesting / vesting_fund.amount
    ctx.log.info(f'{account} vesting share: {vesting_share:.4%}')

    daily_account_vesting = vesting_share * daily_emission.vesting
    ctx.log.info(f'{account} daily vesting: {daily_account_vesting:.0f}')


if __name__ == '__main__':
    main()
