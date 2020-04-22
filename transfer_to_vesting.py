#!/usr/bin/env python

import click

from golosscripts.decorators import common_options, helper


@click.command()
@common_options
@helper
@click.argument('from_')
@click.argument('to')
@click.argument('amount', type=float)
@click.pass_context
def main(ctx, from_, to, amount):
    """Transfer GOLOS to GOLOS POWER."""

    ctx.helper.transfer_to_vesting(amount, to=to, account=from_)


if __name__ == '__main__':
    main()
