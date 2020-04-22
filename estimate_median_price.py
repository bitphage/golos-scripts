#!/usr/bin/env python

import click

from golosscripts.decorators import common_options, helper


@click.command()
@common_options
@helper
@click.pass_context
def main(ctx):
    """Get witnesses price feed and estimate futher median price."""

    ctx.log.info('current conversion price: {:.3f}'.format(ctx.helper.converter.sbd_median_price()))
    ctx.log.info('estimated median price: {:.3f}'.format(ctx.helper.estimate_median_price()))

    if ctx.debug:
        feeds = ctx.helper.get_price_feeds()

        for feed in feeds:
            ctx.log.debug('{}: {:.3f}'.format(feed.owner, feed.price))


if __name__ == '__main__':
    main()
