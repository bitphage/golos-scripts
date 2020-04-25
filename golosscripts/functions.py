import asyncio
import logging
from datetime import date, timedelta
from typing import Any, Dict, Optional

import aiohttp
import ccxt.async_support as ccxt
from defusedxml.minidom import parseString

log = logging.getLogger('golosscripts')


async def get_price_gold_rub_cbr(session: Optional[aiohttp.ClientSession] = None) -> float:
    """get price of 1 mg Gold from Russian Central Bank; return value is RUB."""

    if not session:
        session = aiohttp.ClientSession(raise_for_status=True)

    one_day = timedelta(days=1)
    today = date.today()
    yesterday = today - one_day
    # cbr metall codes: (1 - gold, 2 - silver, 3 - platinum, 4 - palladium)
    # cbr may return an empty value on Monday, so request 2 days history
    payload = {'date_req1': yesterday.strftime('%d/%m/%Y'), 'date_req2': today.strftime('%d/%m/%Y')}

    async with session.get('http://www.cbr.ru/scripts/xml_metall.asp', params=payload, timeout=30) as result:

        dom = parseString(await result.text())
        price = []

        for element in dom.getElementsByTagName('Record'):
            if element.getAttribute('Code') == '1':
                price.append(element.getElementsByTagName('Buy')[0].childNodes[0].data.split(',')[0])

        # return value is grams, so divide to 1000
        return float(price[0]) / 1000


async def get_price_usd_rub_cbr(session: Optional[aiohttp.ClientSession] = None) -> float:
    """get USD/RUB price from Russian Central Bank API mirror."""

    if not session:
        session = aiohttp.ClientSession(raise_for_status=True)

    async with session.get('https://www.cbr-xml-daily.ru/daily_json.js', timeout=30) as result:
        js = await result.json(content_type='application/javascript')

        return js['Valute']['USD']['Value']


async def get_price_gold_usd_cbr() -> float:
    """calculate gold price in USD based on cbr.ru rates."""

    session = aiohttp.ClientSession(raise_for_status=True)
    rub_gold_price, rub_usd_price = await asyncio.gather(
        get_price_gold_rub_cbr(session=session), get_price_usd_rub_cbr(session=session)
    )
    await session.close()

    usd_gold_price = rub_gold_price / rub_usd_price

    return usd_gold_price


async def fetch_ticker(exchange: str, market: str) -> Dict[str, Any]:
    _exchange = getattr(ccxt, exchange)()
    ticker = await _exchange.fetch_ticker(market)
    log.debug('got ticker from %s', exchange)
    await _exchange.close()

    return ticker


async def get_price_btc_usd_exchanges() -> float:
    """returns average BTC/USD price across some exchanges."""

    exchanges = {'binance': 'usdt', 'bittrex': 'usdt', 'coinbase': 'usd', 'gemini': 'usd'}
    tasks = [
        asyncio.create_task(fetch_ticker(exchange, f'BTC/{usd_symbol.upper()}'))
        for exchange, usd_symbol in exchanges.items()
    ]

    # Wait for results from all tasks
    try:
        results = await asyncio.gather(*tasks)
    except ccxt.NetworkError:
        pass

    prices = [i['last'] for i in results]

    return sum(prices) / len(prices)
