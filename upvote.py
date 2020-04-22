#!/usr/bin/env python

import click

from golosscripts.decorators import common_options, helper


@click.command()
@common_options
@helper
@click.option('-w', '--weight', type=float, default=100, help='voting weight')
@click.argument('account', type=str)
@click.argument('url', type=str)
@click.pass_context
def main(ctx, weight, account, url):
    """Upvote post."""

    post = ctx.helper.parse_url(url)
    ctx.helper.vote(post.id, weight, account=account)


if __name__ == '__main__':
    main()
