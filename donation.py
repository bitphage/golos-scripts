#!/usr/bin/env python

import json

import click

from golosscripts.decorators import common_options, helper


@click.command()
@common_options
@helper
@click.argument('from_')
@click.argument('amount', type=float)
@click.argument('asset')
@click.argument('url')
@click.pass_context
def main(ctx, from_, amount, asset, url):
    """Make a donation in liquid asset for specific post."""

    post = ctx.helper.parse_url(url)
    memo = {'donate': {'post': '/@{}/{}'.format(post.author, post.permlink)}}
    ctx.log.info('transfer {} -> {}: {} {}'.format(from_, post.author, amount, asset))
    ctx.helper.transfer(post.author, amount, asset, memo=json.dumps(memo), account=from_)


if __name__ == '__main__':
    main()
