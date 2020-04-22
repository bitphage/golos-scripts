#!/usr/bin/env python

import json

import click
from golos.account import Account

from golosscripts.decorators import common_options, helper


@click.command()
@common_options
@helper
@click.argument('account')
@click.pass_context
def main(ctx, account):
    """Show account object."""

    acc = Account(account)
    js = json.dumps(acc, indent=4)
    print(js)


if __name__ == '__main__':
    main()
