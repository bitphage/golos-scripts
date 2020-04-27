import pytest

from golosscripts.functions import (
    fetch_ticker,
    get_price_btc_usd_exchanges,
    get_price_gold_rub_cbr,
    get_price_usd_gold_cbr,
    get_price_usd_rub_cbr,
    price_troyounce_to_price_1mg,
)


def test_price_troyounce_to_price_1mg():
    price = price_troyounce_to_price_1mg(10000)
    assert price > 0


@pytest.mark.asyncio
async def test_get_price_gold_rub_cbr():
    price = await get_price_gold_rub_cbr()
    assert price > 0


@pytest.mark.asyncio
async def test_get_price_usd_rub_cbr():
    price = await get_price_usd_rub_cbr()
    assert price > 50


@pytest.mark.asyncio
async def test_get_price_usd_gold_cbr():
    price = await get_price_usd_gold_cbr()
    assert price > 0


@pytest.mark.asyncio
async def test_fetch_ticker():
    ticker = await fetch_ticker('binance', 'BTC/USDT')
    assert 'last' in ticker


@pytest.mark.asyncio
async def test_get_price_btc_usd_exchanges():
    price = await get_price_btc_usd_exchanges()
    assert price > 0
