#!/usr/bin/env python

from pprint import pformat

import click
from golos.account import Account
from golos.amount import Amount
from golos.utils import parse_time

from golosscripts.decorators import common_options, helper


@click.command()
@common_options
@helper
@click.option(
    '-a', '--amount', 'amount_limit', type=float, default=0, help='minimal transfer amount to look for (default: 0)'
)
@click.option('-l', '--limit', type=int, default=50, help='limit number of transactions to scan, default: 50')
@click.argument('account')
@click.pass_context
def main(ctx, amount_limit, limit, account):
    """Scan account history looking for transfers."""

    account = Account(account)
    history = account.rawhistory(only_ops=['transfer'], limit=limit)

    for item in history:
        ctx.log.debug(pformat(item))

        timestamp = parse_time(item[1]['timestamp'])
        from_ = item[1]['op'][1]['from']
        to = item[1]['op'][1]['to']
        amount = Amount(item[1]['op'][1]['amount'])
        memo = item[1]['op'][1]['memo']

        if amount.amount > amount_limit:
            print('{}: {:<16} -> {:<16}, {}, {}'.format(timestamp, from_, to, amount, memo))


if __name__ == '__main__':
    main()
