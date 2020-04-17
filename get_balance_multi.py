#!/usr/bin/env python

import click
from golos.account import Account

from golosscripts.decorators import common_options, helper


@click.command()
@common_options
@helper
@click.option('--no-header', default=False, is_flag=True, help='supress header')
@click.option('--no-sum', default=False, is_flag=True, help='supress summary output')
@click.pass_context
def main(ctx, no_header, no_sum):
    """Show multiple users balances."""

    if not no_header:
        print('{:<20} {:>10} {:>11} {:>11}'.format('Account', 'GBG', 'GOLOS', 'GP'))
        print('--------------------')

    sum_gbg = float()
    sum_golos = float()
    sum_gp = float()
    for acc in ctx.config['accs']:
        account = Account(acc)
        balance = account.get_balances()
        cv = ctx.helper.converter
        gp = cv.vests_to_sp(balance['total']['GESTS'])

        print('{:<20} {:>10}  {:>10}  {:>10.0f}'.format(acc, balance['total']['GBG'], balance['total']['GOLOS'], gp))

        sum_gbg += balance['total']['GBG']
        sum_golos += balance['total']['GOLOS']
        sum_gp += gp

    if not no_sum:
        print('--------------------')
        print('{:<20} {:>10.3f}  {:>10.3f}  {:>10.0f}'.format('Totals:', sum_gbg, sum_golos, sum_gp))


if __name__ == '__main__':
    main()
