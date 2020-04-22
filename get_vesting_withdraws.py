#!/usr/bin/env python

from datetime import datetime

import click
from golos.amount import Amount
from golos.utils import parse_time

from golosscripts.decorators import common_options, helper


@click.command()
@common_options
@helper
@click.option(
    '-m',
    '--min-mgests',
    default=0,
    type=float,
    help='look for account with vesting shares not less than X MGESTS, default is 0',
)
@click.option('-a', '--account', type=str, help='get info for this single account')
@click.pass_context
def main(ctx, min_mgests, account):
    """Find all vesting withdrawals with rates and dates."""

    ctx.log.debug('total accounts: %s', ctx.helper.get_account_count())

    if account:
        accs = [account]
    else:
        accs = ctx.helper.get_all_usernames()

    start = datetime.utcnow()

    # get all accounts in one batch
    all_accounts = ctx.helper.get_accounts(accs)

    # we well get summary info about total withdrawal rate and number of accounts
    sum_rate = float()
    count = int()

    cv = ctx.helper.converter
    steem_per_mvests = cv.steem_per_mvests()

    for acc in all_accounts:
        vshares = Amount(acc['vesting_shares'])
        mgests = vshares.amount / 1000000
        rate = Amount(acc['vesting_withdraw_rate'])
        date = parse_time(acc['next_vesting_withdrawal'])

        if mgests > min_mgests and rate.amount > 1000:
            # We use own calculation instead of cv.vests_to_sp() to speed up execution
            # avoiding API call on each interation
            rate_gp = rate.amount / 1e6 * steem_per_mvests
            gp = vshares.amount / 1e6 * steem_per_mvests
            sum_rate += rate_gp
            count += 1

            print('{:<16} {:<18} {:>6.0f} {:>8.0f}'.format(acc['name'], date.strftime('%Y-%m-%d %H:%M'), rate_gp, gp))

    ctx.log.debug('accounts iteration took {:.2f} seconds'.format((datetime.utcnow() - start).total_seconds()))

    ctx.log.info('numbers of matching accounts on vesting withdrawal: {}'.format(count))
    ctx.log.info('sum rate: {:.0f}'.format(sum_rate))


if __name__ == '__main__':
    main()
