import asyncio
import logging
from datetime import date, timedelta
from typing import Any, Dict, Optional, Union

import aiohttp
import ccxt.async_support as ccxt
from defusedxml.minidom import parseString

log = logging.getLogger('golosscripts')


def price_troyounce_to_price_1mg(price_troyounce: float) -> float:
    """Convert price per troy ounce to price per milligramm."""
    gram_in_troyounce = 31.1034768
    price = price_troyounce / gram_in_troyounce / 1000

    return price


async def get_price_rub_gold_cbr(
    timeout: Union[int, float] = 12, session: Optional[aiohttp.ClientSession] = None
) -> float:
    """Get price of 1 mg Gold from Russian Central Bank; return value is RUB."""

    if not session:
        session = aiohttp.ClientSession(raise_for_status=True)

    # cbr metall codes: (1 - gold, 2 - silver, 3 - platinum, 4 - palladium)
    # cbr may return an empty value on Monday, so request 2 days history
    today = date.today()
    date1 = (today - timedelta(days=7)).strftime('%d/%m/%Y')
    date2 = today.strftime('%d/%m/%Y')
    # date_req1 — date_req2 = Date range
    payload = {'date_req1': date1, 'date_req2': date2}

    async with session.get('http://www.cbr.ru/scripts/xml_metall.asp', params=payload, timeout=timeout) as result:

        dom = parseString(await result.text())
        price = []

        for element in dom.getElementsByTagName('Record'):
            if element.getAttribute('Code') == '1':
                price.append(element.getElementsByTagName('Buy')[0].childNodes[0].data.split(',')[0])

        # return value is grams, so divide to 1000
        return float(price[0]) / 1000


async def get_price_usd_rub_cbr(
    timeout: Union[int, float] = 12, session: Optional[aiohttp.ClientSession] = None
) -> float:
    """Get USD/RUB price from Russian Central Bank API mirror."""

    if not session:
        session = aiohttp.ClientSession(raise_for_status=True)

    async with session.get('https://www.cbr-xml-daily.ru/daily_json.js', timeout=timeout) as result:
        js = await result.json(content_type='application/javascript')

        return js['Valute']['USD']['Value']


async def get_price_usd_gold_cbr() -> float:
    """Calculate price of 1 mg GOLD in USD based on cbr.ru rates."""

    session = aiohttp.ClientSession(raise_for_status=True)
    try:
        rub_gold_price, rub_usd_price = await asyncio.gather(
            get_price_rub_gold_cbr(session=session), get_price_usd_rub_cbr(session=session)
        )
    except Exception:
        raise
    finally:
        await session.close()

    usd_gold_price = rub_gold_price / rub_usd_price

    return usd_gold_price


async def fetch_ticker(exchange: str, market: str) -> Dict[str, Any]:
    """
    Fetch ticker data from exchange.

    :param exchange: exchnage name, see `Supported exchanges
        <https://ccxt.readthedocs.io/en/latest/exchanges.html>`_
    :param market: market like 'BTC/USD'
    :return: ticker
    :rtype: dict
    """
    _exchange = getattr(ccxt, exchange)()
    try:
        ticker = await _exchange.fetch_ticker(market)
        log.debug('got ticker from %s', exchange)
    except Exception:
        raise
    finally:
        await _exchange.close()

    return ticker


async def get_price_btc_usd_exchanges() -> float:
    """Returns average BTC/USD price across several pre-defined exchanges."""

    exchanges = {'binance': 'usdt', 'bittrex': 'usdt', 'coinbase': 'usd', 'gemini': 'usd'}
    tasks = [
        asyncio.create_task(fetch_ticker(exchange, f'BTC/{usd_symbol.upper()}'))
        for exchange, usd_symbol in exchanges.items()
    ]

    results = None
    # Wait for results from all tasks
    try:
        results = await asyncio.gather(*tasks)
    except ccxt.NetworkError:
        pass

    if not results:
        raise ccxt.NetworkError('Failed to obtain ticker from any source')

    prices = [i['last'] for i in results]

    return sum(prices) / len(prices)
