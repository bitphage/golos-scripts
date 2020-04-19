#!/usr/bin/env python

import sys

import click

from golosscripts.decorators import common_options, helper


@click.command()
@common_options
@helper
@click.option('--broadcast', default=False, is_flag=True, help='broadcast transaction')
@click.argument('from_')
@click.argument('to')
@click.argument('amount', type=float)
@click.argument('asset')
@click.argument('memo')
@click.pass_context
def main(ctx, broadcast, from_, to, amount, asset, memo):
    """Transfer asset FROM account to another account TO."""

    ctx.log.info('transfer {} -> {}: {} {} "{}"'.format(from_, to, amount, asset, memo))

    if not broadcast:
        ctx.log.info('Not broadcasting!')
        sys.exit(0)

    ctx.helper.transfer(to, amount, asset, memo=memo, account=from_)


if __name__ == '__main__':
    main()
