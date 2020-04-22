#!/usr/bin/env python

import sys
from datetime import datetime
from decimal import Decimal

import click
from golos.utils import parse_time

from golosscripts.decorators import common_options, helper


@click.command()
@common_options
@helper
@click.option('-n', '--notify', default=False, is_flag=True, help='send message to accounts who uses conversions')
@click.option('-a', '--account', type=str, help='get requests for this single account')
@click.pass_context
def main(ctx, notify, account):
    """Find all GBG conversion requests."""

    if account:
        accs = [account]
    else:
        ctx.log.debug('total accounts: %s', ctx.helper.get_account_count())
        accs = ctx.helper.get_all_usernames()

    # obtain conversion_price and market prices whether we're going to send a notification
    if notify:
        bid = ctx.helper.get_market_price(type_='bid')
        conversion_price = ctx.helper.converter.sbd_median_price()
        if not bid or not conversion_price:
            ctx.log.critical('failed to obtain price')
            sys.exit(1)

    start = datetime.utcnow()
    total_sum = Decimal('0.000')
    for acc in accs:
        requests = ctx.helper.get_conversion_requests(acc)
        total = Decimal('0.000')
        # Add datetime field
        for request in requests:
            request['date'] = parse_time(request['conversion_date'])

        # Sort by datetime
        requests = sorted(requests, key=lambda k: k['date'])
        for request in requests:
            amount = request['amount'].split()[0]
            total += Decimal(amount)
            print(
                '{:<16} {:<18} {:>7}'.format(
                    request['owner'], request['amount'], request['date'].strftime('%Y-%m-%d %H:%M')
                )
            )

        total_sum += total

        if len(requests) > 1:
            print('{:<16} {:<18} {:<7}'.format(request['owner'], total, 'Total'))

        if requests and notify:
            msg = ctx.config['notify_message'].format(conversion_price, bid)
            ctx.helper.transfer(acc, '0.001', 'GOLOS', memo=msg, account=ctx.config['notify_account'])

    print('Total on conversion: {}'.format(total_sum))
    ctx.log.debug('getting conversion requests took {:.2f} seconds'.format((datetime.utcnow() - start).total_seconds()))


if __name__ == '__main__':
    main()
