#!/usr/bin/env python

import asyncio

import click
from golos.amount import Amount

from golosscripts.bitshares_helper import BitSharesHelper
from golosscripts.decorators import common_options, helper
from golosscripts.functions import get_price_btc_usd_exchanges, get_price_gold_usd_cbr


async def calc_debt(ctx, usd):

    price_mg_gold, price_btc_usd = await asyncio.gather(get_price_gold_usd_cbr(), get_price_btc_usd_exchanges())
    # BTC/GOLD
    price_btc_gold = price_mg_gold / price_btc_usd

    # BTC/GOLOS
    bitshares = BitSharesHelper(node=ctx.config['node_bts'])
    price_btc_golos, _ = bitshares.get_market_center_price('RUDEX.GOLOS/RUDEX.BTC', depth_pct=5)

    props = ctx.helper.get_dynamic_global_properties()
    sbd_supply = Amount(props['current_sbd_supply'])
    current_supply = Amount(props['current_supply'])
    virtual_supply = Amount(props['virtual_supply'])
    total_reward_fund_steem = Amount(props['total_reward_fund_steem'])

    median = ctx.helper.converter.sbd_median_price()
    median_estimated = ctx.helper.estimate_median_price()

    # libraries/chain/database.cpp
    # this min_price caps system debt to 10% of GOLOS market capitalisation
    min_price = 9 * sbd_supply.amount / current_supply.amount
    print('Minimal possible median price GBG/GOLOS: {:.3f}'.format(min_price))

    # #define STEEMIT_100_PERCENT 10000
    # this is current GBG percent printed
    percent_sbd = sbd_supply.amount / median * 100 / virtual_supply.amount
    print('System GBG debt percent (by blockchain median): {:.2f}'.format(percent_sbd))
    percent_sbd = sbd_supply.amount / median_estimated * 100 / virtual_supply.amount
    print('System GBG debt percent (by feed price): {:.2f}'.format(percent_sbd))

    if percent_sbd > 10:
        # estimate supply when debt will return to 10% at current price
        target_supply = 9 * sbd_supply.amount / median_estimated
        print('GBG supply: {:,.0f} GBG'.format(sbd_supply.amount))
        print('Current supply: {:,.0f} GOLOS'.format(current_supply.amount))
        print('Expected supply for reaching 10% debt: {:,.0f} GOLOS'.format(target_supply))

        converted_supply = sbd_supply.amount / median
        print('New GOLOS amount on full convertation by blockchain price: {:,.0f} GOLOS'.format(converted_supply))

        converted_supply = sbd_supply.amount / median_estimated
        print('New GOLOS amount on full convertation by feed price: {:,.0f} GOLOS'.format(converted_supply))
        print(
            'Total supply after full convertation by feed price: {:,.0f} GOLOS'.format(
                current_supply.amount + converted_supply
            )
        )

        # model gradual conversion of all GBG supply
        step = 10000
        price = min_price
        gbg = sbd_supply.amount
        golos = current_supply.amount
        flag = False

        while gbg > step:
            gbg -= step
            golos += step / price
            price = max(9 * gbg / golos, median_estimated)
            virtual_supply = golos + gbg / price
            percent_sbd = gbg / median_estimated * 100 / virtual_supply
            if percent_sbd < 20 and not flag:
                print('GBG supply at 20% debt: {:,.0f}'.format(gbg))
                print('New GOLOS amount from conversion to 20% debt: {:,.0f}'.format(golos - current_supply.amount))
                flag = True
        new_supply = golos - current_supply.amount
        print(
            'New GOLOS amount after gradual convertation of all GBG with step {}: {:,.0f} GOLOS'.format(
                step, new_supply
            )
        )

    sbd_print_rate = props['sbd_print_rate'] / 100
    gbg_emission_week = (total_reward_fund_steem.amount / 2) * median * sbd_print_rate / 100
    gbg_emission_day = gbg_emission_week / 7
    print('GBG print rate: {:.2f}'.format(sbd_print_rate))
    print('Approximate GBG emission per day: {:.0f}'.format(gbg_emission_day))

    print('Conversion-derived price BTC/GBG: {:.8f}'.format(price_btc_golos / median))
    print('External price BTC/XAU: {:.8f}'.format(price_btc_gold))
    print('Current external price BTC/GOLOS: {:.8f}'.format(price_btc_golos))

    if usd:
        print('Approximate USD/GOLOS price at 2%-debt point: {:.3f}'.format(price_mg_gold * min_price * 5))
        print('Approximate USD/GOLOS price at 5%-debt point: {:.3f}'.format(price_mg_gold * min_price * 2))
        print('Approximate USD/GOLOS price at 10%-debt point: {:.3f}'.format(price_mg_gold * min_price))
    else:
        print('Approximate BTC/GOLOS price at 2%-debt point: {:.8f}'.format(price_btc_gold * min_price * 5))
        print('Approximate BTC/GOLOS price at 5%-debt point: {:.8f}'.format(price_btc_gold * min_price * 2))
        print('Approximate BTC/GOLOS price at 10%-debt point: {:.8f}'.format(price_btc_gold * min_price))


@click.command()
@common_options
@helper
@click.option('--usd', default=False, is_flag=True, help='display debt points in USD')
@click.pass_context
def main(ctx, usd):
    """Estimate GBG system debt and calc some analytics."""

    asyncio.run(calc_debt(ctx, usd))


if __name__ == '__main__':
    main()
