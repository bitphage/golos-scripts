import asyncio
import logging
import math
import re
from typing import List, Tuple, Union

from bitshares.aio import BitShares
from bitshares.aio.asset import Asset
from bitshares.aio.instance import set_shared_bitshares_instance
from bitshares.aio.market import Market

log = logging.getLogger(__name__)


class BitSharesHelper:
    """
    A helper class to interact with BitShares network.

    .. note::

        This class sets shared bitshares instance, see
        :py:func:`bitshares.aio.instance.set_shared_bitshares_instance`.

    :param str,list node: bitshares node(s)
    :param loop: :py:mod:`asyncio` event loop instance
    """

    def __init__(self, node: Union[str, list] = None, loop: asyncio.BaseEventLoop = None) -> None:
        self.bitshares = BitShares(node=node, loop=loop)
        set_shared_bitshares_instance(self.bitshares)  # avoids bugs with lost instance
        self.connected = False
        self.fetch_depth = 50

    @staticmethod
    def split_pair(market: str) -> List[str]:
        """
        Split market pair into QUOTE, BASE symbols.

        :param str market: market pair in format 'QUOTE/BASE'. Supported separators are: "/", ":", "-".
        :return: list with QUOTE and BASE as separate symbols
        :rtype: list
        """
        return re.split('/|:|-', market.upper())

    async def connect(self):
        """Connect to BitShares network."""
        if not self.connected:
            await self.bitshares.connect()
            self.connected = True

    async def get_market_buy_price_pct_depth(self, market: str, depth_pct: float) -> Tuple[float, float]:
        """
        Measure QUOTE volume and BASE/QUOTE price for [depth] percent deep starting from highest bid.

        :param str market: market in format 'QUOTE/BASE'
        :param float depth_pct: depth percent (1-100) to measure volume and average price
        :return: tuple with ("price as float", volume) where volume is actual quote volume
        """
        if not depth_pct > 0:
            raise ValueError('depth_pct should be greater than 0')

        _market = await self._get_market(market)

        market_orders = (await _market.orderbook(self.fetch_depth))['bids']
        market_fee = _market['base'].market_fee_percent

        if not market_orders:
            return (0, 0)

        highest_bid_price = market_orders[0]['price']
        stop_price = highest_bid_price / (1 + depth_pct / 100)
        quote_amount = 0
        base_amount = 0
        for order in market_orders:
            if order['price'] > stop_price:
                quote_amount += order['quote']['amount']
                base_amount += order['base']['amount']
            else:
                break

        quote_amount *= 1 + market_fee

        return (base_amount / quote_amount, quote_amount)

    async def get_market_sell_price_pct_depth(self, market: str, depth_pct: float) -> Tuple[float, float]:
        """
        Measure QUOTE volume and BASE/QUOTE price for [depth] percent deep starting from lowest ask.

        :param str market: market in format 'QUOTE/BASE'
        :param float depth_pct: depth percent (1-100) to measure volume and average price
        :return: tuple with ("price as float", volume) where volume is actual quote volume
        """
        if not depth_pct > 0:
            raise ValueError('depth_pct should be greater than 0')

        _market = await self._get_market(market)

        market_orders = (await _market.orderbook(self.fetch_depth))['asks']
        market_fee = _market['quote'].market_fee_percent

        if not market_orders:
            return (0, 0)

        lowest_ask_price = market_orders[0]['price']
        stop_price = lowest_ask_price * (1 + depth_pct / 100)
        quote_amount = 0
        base_amount = 0
        for order in market_orders:
            if order['price'] < stop_price:
                quote_amount += order['quote']['amount']
                base_amount += order['base']['amount']
            else:
                break

        quote_amount /= 1 + market_fee

        return (base_amount / quote_amount, quote_amount)

    async def get_market_buy_price(
        self, market: str, quote_amount: float = 0, base_amount: float = 0
    ) -> Tuple[float, float]:
        """
        Returns the BASE/QUOTE price for which [depth] worth of QUOTE could be sold.

        :param str market: market in format 'QUOTE/BASE'
        :param float quote_amount:
        :param float base_amount:
        :return: tuple with ("price as float", volume) where volume is actual base or quote volume
        """
        _market = await self._get_market(market)

        # In case amount is not given, return price of the highest buy order on the market
        if quote_amount == 0 and base_amount == 0:
            raise ValueError("quote_amount or base_amount must be given")

        # Like get_market_sell_price(), but defaulting to base_amount if both base and quote are specified.
        asset_amount = base_amount

        """ Since the purpose is never get both quote and base amounts, favor base amount if both given because
            this function is looking for buy price.
        """
        if base_amount > quote_amount:
            base = True
        else:
            asset_amount = quote_amount
            base = False

        market_orders = (await _market.orderbook(self.fetch_depth))['bids']
        market_fee = _market['base'].market_fee_percent

        target_amount = asset_amount * (1 + market_fee)

        quote_amount = 0
        base_amount = 0
        missing_amount = target_amount

        for order in market_orders:
            if base:
                # BASE amount was given
                if order['base']['amount'] <= missing_amount:
                    quote_amount += order['quote']['amount']
                    base_amount += order['base']['amount']
                    missing_amount -= order['base']['amount']
                else:
                    base_amount += missing_amount
                    quote_amount += missing_amount / order['price']
                    break
            elif not base:
                # QUOTE amount was given
                if order['quote']['amount'] <= missing_amount:
                    quote_amount += order['quote']['amount']
                    base_amount += order['base']['amount']
                    missing_amount -= order['quote']['amount']
                else:
                    base_amount += missing_amount * order['price']
                    quote_amount += missing_amount
                    break

        # Prevent division by zero
        if not quote_amount:
            return (0.0, 0)

        return (base_amount / quote_amount, base_amount if base else quote_amount)

    async def get_market_sell_price(
        self, market: str, quote_amount: float = 0, base_amount: float = 0
    ) -> Tuple[float, float]:
        """
        Returns the BASE/QUOTE price for which [depth] worth of QUOTE could be bought.

        :param str market: market in format 'QUOTE/BASE'
        :param float quote_amount:
        :param float base_amount:
        :return: tuple with ("price as float", volume) where volume is actual base or quote volume
        """
        _market = await self._get_market(market)

        # In case amount is not given, return price of the highest buy order on the market
        if quote_amount == 0 and base_amount == 0:
            raise ValueError("quote_amount or base_amount must be given")

        asset_amount = quote_amount
        """ Since the purpose is never get both quote and base amounts, favor quote amount if both given because
            this function is looking for sell price.
        """
        if quote_amount > base_amount:
            quote = True
        else:
            asset_amount = base_amount
            quote = False

        market_orders = (await _market.orderbook(self.fetch_depth))['asks']
        market_fee = _market['quote'].market_fee_percent

        target_amount = asset_amount * (1 + market_fee)

        quote_amount = 0
        base_amount = 0
        missing_amount = target_amount

        for order in market_orders:
            if quote:
                # QUOTE amount was given
                if order['quote']['amount'] <= missing_amount:
                    quote_amount += order['quote']['amount']
                    base_amount += order['base']['amount']
                    missing_amount -= order['quote']['amount']
                else:
                    base_amount += missing_amount * order['price']
                    quote_amount += missing_amount
                    break
            elif not quote:
                # BASE amount was given
                if order['base']['amount'] <= missing_amount:
                    quote_amount += order['quote']['amount']
                    base_amount += order['base']['amount']
                    missing_amount -= order['base']['amount']
                else:
                    base_amount += missing_amount
                    quote_amount += missing_amount / order['price']
                    break

        # Prevent division by zero
        if not quote_amount:
            return (0.0, 0)

        return (base_amount / quote_amount, quote_amount if quote else base_amount)

    async def get_market_center_price(
        self, market: str, base_amount: float = 0, quote_amount: float = 0, depth_pct: float = 0
    ) -> Tuple[float, float]:
        """
        Returns the center price of market.

        :param str market: market in format 'QUOTE/BASE'
        :param float base_amount:
        :param float quote_amount:
        :param float depth_pct: depth percent (1-100) to measure volume and average price
        :return: Tuple with market center price as float, volume in buy or sell side which is lower
        """

        if depth_pct and (base_amount or quote_amount):
            raise ValueError('depth_pct and (base_amount, quote_amount) are mutually exclusive')
        elif not depth_pct and not (base_amount or quote_amount):
            raise ValueError('expected depth_pct or base_amount or quote_amount')

        if depth_pct:
            # depth_pct has precedence over xxx_amount
            buy_price, buy_volume = await self.get_market_buy_price_pct_depth(market, depth_pct=depth_pct)
            sell_price, sell_volume = await self.get_market_sell_price_pct_depth(market, depth_pct=depth_pct)
        elif base_amount or quote_amount:
            buy_price, buy_volume = await self.get_market_buy_price(
                market, quote_amount=quote_amount, base_amount=base_amount
            )
            sell_price, sell_volume = await self.get_market_sell_price(
                market, quote_amount=quote_amount, base_amount=base_amount
            )

        if (buy_price is None or buy_price == 0.0) or (sell_price is None or sell_price == 0.0):
            return (0, 0)

        center_price = buy_price * math.sqrt(sell_price / buy_price)

        return (center_price, min(buy_volume, sell_volume))

    async def get_price_across_2_markets(self, market: str, via: str, depth_pct: float = 20) -> Tuple[float, float]:
        """
        Derive cross-price for A/C from A/B, B/C markets.

        :param str market: target market in format A/C
        :param str via: intermediate asset
        :param float depth_pct: depth percent (1-100) to measure volume and average price
        :return: tuple with price and volume
        """
        # Price and volume on A/B market
        quote, base = self.split_pair(market)
        market1 = f'{quote}/{via}'
        price1, volume1 = await self.get_market_center_price(market1, depth_pct=depth_pct)
        log.debug('Raw price {:.8f} {}/{}'.format(price1, quote, via))

        if base == via:
            return price1, volume1

        # Price and volume on B/C  market
        market2 = f'{via}/{base}'
        price2, volume2 = await self.get_market_center_price(market2, depth_pct=depth_pct)

        # Derived price A/C
        price = price1 * price2

        # Limit volume by smallest volume across steps
        try:
            volume = min(volume1, volume2 / price1)
        except ZeroDivisionError:
            volume = 0

        return price, volume

    async def get_feed_price(self, asset: str, invert: bool = False) -> float:
        """
        Get price data from feed.

        By default, price is MPA/BACKING, e.g. for USD asset price is how many USD per BTS.
        To get BACKING per MPA price, use `invert=True`

        :param str asset: name of the asset
        :param bool invert: return inverted price
        :return: price as float
        :rtype: float
        """
        _asset = await Asset(asset, blockchain_instance=self.bitshares)
        price = (await _asset.feed)['settlement_price']

        if invert:
            await price.invert()

        return float(price)

    async def _get_market(self, market):
        return await Market(market, bitshares_instance=self.bitshares)
