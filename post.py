#!/usr/bin/env python

import click

from golosscripts.decorators import common_options, helper


@click.command()
@common_options
@helper
@click.argument('account', type=str)
@click.argument('title', type=str)
@click.argument('tags', type=str)
@click.argument('permlink', type=str)
@click.argument('file_', type=click.File())
@click.pass_context
def main(ctx, account, title, tags, permlink, file_):
    """
    Publish post to the Blockchain.

    \b ACCOUNT account to post from TITLE post title TAGS comma-separated tag list PERMLINK post permlink FILE path to
    file containing post in markdown format or "-" for stdin
    """
    body = file_.read()
    tags = tags.split(',')

    ctx.helper.post(title, body, author=account, permlink=permlink, tags=tags)


if __name__ == '__main__':
    main()
