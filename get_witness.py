#!/usr/bin/env python


from pprint import pprint

import click
from golos.witness import Witness

from golosscripts.decorators import common_options, helper


@click.command()
@common_options
@helper
@click.argument('witness', type=str)
def main(witness):
    """Show WITNESS object."""
    wit = Witness(witness)
    pprint(wit)


if __name__ == '__main__':
    main()
