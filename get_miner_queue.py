#!/usr/bin/env python

from pprint import pprint

import click

from golosscripts.decorators import common_options, helper


@click.command()
@common_options
@helper
@click.pass_context
def main(ctx):
    """Show miner queue."""
    queue = ctx.helper.get_miner_queue()
    pprint(queue)


if __name__ == '__main__':
    main()
