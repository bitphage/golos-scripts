#!/usr/bin/env python

import click

from golosscripts.decorators import common_options, helper


@click.command()
@common_options
@helper
@click.option('-C', '--count', default=19, help='number of witnesses to get')
@click.option('-o', '--oneline', default=False, is_flag=True, help='print witnesses in one line')
@click.option('-a', '--active', default=False, is_flag=True, help='print witnesses from current round')
@click.pass_context
def main(ctx, count, oneline, active):
    """Get list of witnesses."""

    if active:
        witnesses = ctx.helper.get_active_witnesses()
        witness_list = ['@{}'.format(i) for i in witnesses]
    else:
        witnesses = ctx.helper.get_witnesses_by_vote('', count)
        witness_list = ['@{}'.format(i['owner']) for i in witnesses]

    if oneline:
        print(' '.join(witness_list))
    else:
        print('\n'.join(witness_list))


if __name__ == '__main__':
    main()
