#!/usr/bin/env python

from pprint import pprint

import click

from golosscripts.decorators import common_options, helper


@click.command()
@common_options
@helper
@click.pass_context
def main(ctx):
    """Show global properties and "steem per mvests"."""

    pprint(ctx.helper.get_dynamic_global_properties())
    print('steem_per_mvests: {}'.format(ctx.helper.converter.steem_per_mvests()))


if __name__ == '__main__':
    main()
