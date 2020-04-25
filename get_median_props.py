#!/usr/bin/env python

import json

import click

from golosscripts.decorators import common_options, helper


@click.command()
@common_options
@helper
@click.pass_context
def main(ctx):
    """Get current votable params."""
    median_props = ctx.helper.get_chain_properties()
    print(json.dumps(median_props, indent=4))


if __name__ == '__main__':
    main()
