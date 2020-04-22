#!/usr/bin/env python

import logging
import sys

import click

from golosscripts.decorators import common_options, helper


@click.command()
@common_options
@helper
@click.option(
    '-t',
    '--type',
    'type_',
    default='market',
    type=click.Choice(['market', 'forum', 'custom']),
    help='bandwidth type to estimate. Market - transfers, forum - posting ops, custom - custom_json ops',
)
@click.option(
    '-w',
    '--warning',
    default=99,
    type=float,
    help='exit with 1 error code whether bandwidth exceeded specified percent',
)
@click.option(
    '-q',
    '--quiet',
    default=False,
    is_flag=True,
    help='do not show any output except errors, just return 0 if has_bandwidth or 1 if not',
)
@click.argument('account')
@click.pass_context
def main(ctx, type_, warning, quiet, account):
    """Estimate current bandwidth usage for an account."""
    if quiet:
        ctx.log.setLevel(logging.CRITICAL)

    bw = ctx.helper.get_bandwidth(account, type_=type_)
    ctx.log.info(f'used: {bw.used:.2f} KB, avail: {bw.avail:.2f} KB, usage ratio: {bw.ratio:.2%}')

    if bw.ratio * 100 > warning:
        ctx.log.warning('bandwidth usage ratio execeeded limit: {:.2%}'.format(bw.ratio))
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()
