#!/usr/bin/env python

import click
from golosbase.account import PrivateKey

from golosscripts.decorators import common_options, helper


@click.command()
@common_options
@helper
@click.pass_context
def main(ctx):
    """Generate random keypair."""

    wif = PrivateKey()
    prefix = ctx.helper.steemd.chain_params["prefix"]
    pubkey = format(wif.pubkey, prefix)

    print(f'private key: {str(wif)}')
    print(f'public key: {pubkey}')


if __name__ == '__main__':
    main()
