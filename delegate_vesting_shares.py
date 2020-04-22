#!/usr/bin/env python

import click
from golos.amount import Amount

from golosscripts.decorators import common_options, helper


@click.command()
@common_options
@helper
@click.option('-g', '--gests', default=False, is_flag=True, help='amount in GESTS (default: amount in Golos Power)')
@click.argument('from_')
@click.argument('to')
@click.argument('amount', type=float)
@click.pass_context
def main(ctx, gests, from_, to, amount):

    if gests:
        gests = amount
    else:
        cv = ctx.helper.converter
        gests = cv.sp_to_vests(amount)

    gests = Amount('{} GESTS'.format(gests))
    ctx.helper.delegate_vesting_shares(to, gests, account=from_)


if __name__ == '__main__':
    main()
