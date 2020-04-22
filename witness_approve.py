#!/usr/bin/env python

import click

from golosscripts.decorators import common_options, helper


@click.command()
@common_options
@helper
@click.argument('account')
@click.argument('witness')
@click.pass_context
def main(ctx, account, witness):
    """
    Vote for witness.

    \b
    ACCOUNT - account name to use for voting
    WITNESS - witness name to approve
    """
    ctx.helper.approve_witness(witness, account=account)


if __name__ == '__main__':
    main()
