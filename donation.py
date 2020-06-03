#!/usr/bin/env python

import click

from golosscripts.decorators import common_options, helper


@click.command()
@common_options
@helper
@click.option('--comment', help='add comment message to donation')
@click.argument('from_')
@click.argument('amount', type=float)
@click.argument('url')
@click.pass_context
def main(ctx, comment, from_, amount, url):
    """Make a donation from tip balance for specified post."""

    post = ctx.helper.parse_url(url)
    ctx.helper.golosid_donate_v1(amount, post.author, post.permlink, comment=comment, account=from_)


if __name__ == '__main__':
    main()
