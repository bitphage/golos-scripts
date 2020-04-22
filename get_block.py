#!/usr/bin/env python

from pprint import pprint

import click
from golos.block import Block

from golosscripts.decorators import common_options, helper


@click.command()
@common_options
@helper
@click.argument('block_num')
@click.pass_context
def main(ctx, block_num):
    """Get block."""

    block = Block(block_num)
    pprint(block)


if __name__ == '__main__':
    main()
