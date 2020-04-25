#!/usr/bin/env python

import click
from golos.witness import Witness

from golosscripts.decorators import common_options, helper


@click.command()
@common_options
@helper
@click.option('--shutdown', default=False, is_flag=True, help='shutdown witness')
@click.pass_context
def main(ctx, shutdown):
    """Update witness data or votable params."""
    # set pubkey to special value whether we need to shutdown witness
    if shutdown:
        pubkey = 'GLS1111111111111111111111111111111114T1Anm'
    else:
        pubkey = ctx.config['witness_pubkey']

    witness = Witness(ctx.config['witness'])

    if witness['url'] != ctx.config['url'] or witness['signing_key'] != pubkey:
        ctx.helper.witness_update(pubkey, ctx.config['url'], ctx.config['props'], account=ctx.config['witness'])

    ctx.helper.chain_properties_update(ctx.config['props'], account=ctx.config['witness'])


if __name__ == '__main__':
    main()
