#!/usr/bin/env python

import click

from golosscripts.decorators import common_options, helper


@click.command()
@common_options
@helper
@click.pass_context
def main(ctx):
    """Print Golos Power for each sea habitant level."""

    spmv = ctx.helper.converter.steem_per_mvests()

    print('fish: {:.0f}'.format(spmv * 1))
    print('dolphin: {:.0f}'.format(spmv * 10))
    print('orca: {:.0f}'.format(spmv * 100))
    print('whale: {:.0f}'.format(spmv * 1000))


if __name__ == '__main__':
    main()
