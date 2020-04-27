import re

import pytest

from golosscripts.bitshares_helper import BitSharesHelper

market = 'BTS/RUBLE'
nodes = [
    'wss://eu.nodes.bitshares.ws',
    'wss://api.bitshares.org',
    'wss://api.dex.trading',
    'wss://dex.iobanker.com:9090',
    'wss://api.bts.ai',
    'wss://api.bitshares.bhuz.info/ws',
    'wss://api.btsgo.net/ws',
]


@pytest.fixture(scope='session')
async def helper(event_loop):
    helper = BitSharesHelper(node=nodes, loop=event_loop)
    await helper.connect()
    return helper


@pytest.mark.asyncio
async def test_get_market_buy_price_pct_depth(helper):
    price, volume = await helper.get_market_buy_price_pct_depth(market, 5)
    assert price > 0
    assert volume > 0


@pytest.mark.asyncio
async def test_get_market_sell_price_pct_depth(helper):
    price, volume = await helper.get_market_sell_price_pct_depth(market, 5)
    assert price > 0
    assert volume > 0


@pytest.mark.asyncio
async def test_get_market_buy_price(helper):

    with pytest.raises(ValueError, match='quote_amount or base_amount must be given'):
        await helper.get_market_buy_price(market)

    price, volume = await helper.get_market_buy_price(market, quote_amount=1)
    assert price > 0
    assert volume > 0

    price, volume = await helper.get_market_buy_price(market, base_amount=1)
    assert price > 0
    assert volume > 0


@pytest.mark.asyncio
async def test_get_market_sell_price(helper):

    with pytest.raises(ValueError, match='quote_amount or base_amount must be given'):
        await helper.get_market_sell_price(market)

    price, volume = await helper.get_market_sell_price(market, quote_amount=1)
    assert price > 0
    assert volume > 0

    price, volume = await helper.get_market_sell_price(market, base_amount=1)
    assert price > 0
    assert volume > 0


@pytest.mark.asyncio
async def test_get_market_center_price(helper):

    with pytest.raises(ValueError, match='expected depth_pct or base_amount or quote_amount'):
        await helper.get_market_center_price(market)

    with pytest.raises(ValueError, match=re.escape('depth_pct and (base_amount, quote_amount) are mutually exclusive')):
        await helper.get_market_center_price(market, base_amount=1, depth_pct=1)

    price, volume = await helper.get_market_center_price(market, base_amount=1, quote_amount=1)
    assert price > 0
    assert volume > 0

    price, volume = await helper.get_market_center_price(market, depth_pct=5)
    assert price > 0
    assert volume > 0


@pytest.mark.asyncio
async def test_get_feed_price(helper):
    price = await helper.get_feed_price('HONEST.XAU')
    assert price > 0


@pytest.mark.asyncio
async def test_get_price_across_2_markets(helper):
    market = 'RUBLE/RUDEX.BTC'
    via = 'BTS'
    price, volume = await helper.get_price_across_2_markets(market, via)
    assert price > 0
    assert volume > 0
