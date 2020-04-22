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
    ctx.log.info('%s vesting share: %s', account, account_vesting / vesting_fund.amount)


if __name__ == '__main__':
    main()
