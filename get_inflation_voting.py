#!/usr/bin/env python

import statistics
from typing import Dict, List, Union

import click
from golos.witness import Witness

from golosscripts.decorators import common_options, helper

votings = List[Dict[str, Union[str, int]]]


def get_median_voting(voting: votings, sort_key: str) -> votings:
    """Calculate median in voting list by sort_key and return only items which has median value."""

    voting = sorted(voting, key=lambda k: k[sort_key])
    values = [i[sort_key] for i in voting]
    median = statistics.median(values)  # type: ignore

    for el in voting:
        print('{name:<16} {worker} {witness} {vesting} {author}'.format(**el))
    print(f'{sort_key}_reward_percent median: {median}')

    next_voting = [e for e in voting if e[sort_key] == median]

    return next_voting


@click.command()
@common_options
@helper
@click.pass_context
def main(ctx):
    """Get voting for inflation targets props."""

    witnesses_names = ctx.helper.get_active_witnesses()
    witnesses = [Witness(i) for i in witnesses_names]
    voting = []

    for i in witnesses:
        element = {
            'name': i['owner'],
            'worker': i['props']['worker_reward_percent'],
            'witness': i['props']['witness_reward_percent'],
            'vesting': i['props']['vesting_reward_percent'],
        }
        element['author'] = 10000 - element['worker'] - element['witness'] - element['vesting']
        voting.append(element)

    for key in ['worker', 'witness', 'vesting']:
        voting = get_median_voting(voting, key)


if __name__ == '__main__':
    main()
