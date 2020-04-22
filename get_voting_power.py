#!/usr/bin/env python

import click

from golosscripts.decorators import common_options, helper


@click.command()
@common_options
@helper
@click.argument('account')
@click.pass_context
def main(ctx, account):
    """Calculate actual voting power of an account."""

    vp = ctx.helper.get_voting_power(account)
    ctx.log.info('VP of {}: {:.2f}'.format(account, vp))


if __name__ == '__main__':
    main()
