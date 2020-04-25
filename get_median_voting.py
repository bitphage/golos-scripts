#!/usr/bin/env python

import click
from golos.witness import Witness

from golosscripts.decorators import common_options, helper


@click.command()
@common_options
@helper
@click.argument('param', type=str)
@click.pass_context
def main(ctx, param):
    """Get witness voting for a particular chain param."""

    witnesses_names = ctx.helper.get_active_witnesses()
    witnesses = [Witness(i) for i in witnesses_names]
    voting = []

    for i in witnesses:
        element = {'name': i['owner'], 'param': i['props'][param]}
        voting.append(element)

    voting = sorted(voting, key=lambda i: i['param'])
    median = voting[10]['param']

    for el in voting:
        print('{name:<16} {param}'.format(**el))

    print(f'{param} median: {median}')


if __name__ == '__main__':
    main()
