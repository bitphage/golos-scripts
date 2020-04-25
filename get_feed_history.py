#!/usr/bin/env python

from datetime import datetime, timedelta

import click
from golos.amount import Amount

from golosscripts.decorators import common_options, helper


@click.command()
@common_options
@helper
@click.pass_context
def main(ctx):
    """Show pricefeed history."""

    hist = ctx.helper.get_feed_history()['price_history']
    hist_size = len(hist)

    # median history contains values for STEEMIT_FEED_HISTORY_WINDOW
    # median price update performed once per hour
    for i in hist:
        timestamp = datetime.now() - timedelta(hours=hist_size)
        base = Amount(i['base'])
        quote = Amount(i['quote'])
        price = base.amount / quote.amount
        print('{}: {:.3f}'.format(timestamp.strftime('%d.%m.%Y %H'), price))
        # use hist_size as iterator
        hist_size -= 1


if __name__ == '__main__':
    main()
