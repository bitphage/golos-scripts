import asyncio
import logging
import statistics
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List

from golos.utils import parse_time
from golos.witness import Witness

from .bitshares_helper import BitSharesHelper
from .functions import fetch_ticker, get_price_usd_gold_cbr, price_troyounce_to_price_1mg
from .helper import Helper

log = logging.getLogger(__name__)
bitshares_markets = [
    'RUDEX.GOLOS/BTS',
    'RUDEX.GOLOS/RUDEX.BTC',
    'RUDEX.GOLOS/RUBLE',
    'RUDEX.GOLOS/RUDEX.USDT',
]


class PriceSource(Enum):
    bitshares = 1
    kuna = 2


class Metric(Enum):
    median = 1
    mean = 2
    weighted_average = 3


class FeedUpdater:
    """This class is used to calculate and update 'sbd_exchange_rate' for witness."""

    def __init__(self, config: Dict[str, Any], dry_run: bool = False,) -> None:
        """
        Instantiate FeedUpdater.

        config is supposed to contain following configuration directives:

            - node: golos node to connect to
            - node_bts: bitshares node
            - keys: witness active keys
            - markets: list of markets to use to obtain price, in format ['QUOTE/BASE']
            - metric: what metric to use to calculate price
            - depth_pct: how deeply measure market for volume

        :param dict config: dictionary containing configuration directives
        :param bool dry_run: only do price calculation without sending transaction
        """

        self.dry_run = dry_run

        self.witness = config.get('witness')
        if not self.witness:
            raise ValueError('witness is not set in config')

        price_source = config.get('source', 'bitshares')
        try:
            self.price_source = getattr(PriceSource, price_source)
        except AttributeError:
            raise ValueError('unknown price source: %s', price_source)

        metric = config.get('metric', 'weighted_average')
        try:
            self.metric = getattr(Metric, metric)
        except AttributeError:
            raise ValueError('unknown metric: %s', metric)

        if 'node' not in config:
            raise ValueError('node is not set in config')
        if 'keys' not in config:
            raise ValueError('no keys in config')
        self.helper = Helper(nodes=config['node'], keys=config['keys'])

        if self.price_source == PriceSource.bitshares:
            if 'node_bts' not in config:
                raise ValueError('node_bts is not set in config')
            self.bitshares = BitSharesHelper(node=config['node_bts'])

        self.markets = config.get('markets', bitshares_markets)
        self.depth_pct = config.get('depth_pct', 20)
        self.threshold_pct = config.get('threshold_pct', 10) / 100
        self.interval = config.get('interval', 3600)
        self.correction = config.get('k', 1)
        self.max_age = config.get('max_age', 86400)

    @staticmethod
    def calc_weighted_average_price(prices: List[Dict[str, float]]) -> float:
        """
        Calculate weighted average price using "volume" key.

        :param list prices: list of dicts [{'price': price, 'volume': volume, 'market': market}]
        """
        sum_volume = sum((i['volume'] for i in prices))
        weighted_average_price = sum((i['price'] * i['volume'] / sum_volume for i in prices))

        return weighted_average_price

    @staticmethod
    def is_last_price_too_old(witness_data: Dict, max_age: int) -> bool:
        """Check last price update time and return True if older than max_age."""

        last_update = parse_time(witness_data['last_sbd_exchange_update'])
        log.debug('last price update: %s', last_update)
        log.debug('max_age: %s', max_age)

        delta = datetime.utcnow() - last_update
        log.debug('time passed since last update: %s seconds', delta.total_seconds())

        if delta.total_seconds() > max_age:
            log.debug('price too old, need update')
            return True

        return False

    async def calc_price_bts_golos(self) -> float:
        """Calculate price BTS/GOLOS using GOLOS markets on bitshares."""
        await self.bitshares.connect()

        price_data = []

        for market in self.markets:
            quote, base = self.bitshares.split_pair(market)
            target_market = '{}/BTS'.format(quote)
            price, volume = await self.bitshares.get_price_across_2_markets(
                target_market, via=base, depth_pct=self.depth_pct
            )
            log.debug('Derived price from market {}: {:.8f} BTS/GOLOS, volume: {:.0f}'.format(market, price, volume))
            price_data.append({'price': price, 'volume': volume, 'market': market})

        prices = [element['price'] for element in price_data if element['price'] > 0]
        price_bts_golos_median = statistics.median(prices)
        log.debug('Median market price: {:.8f} BTS/GOLOS'.format(price_bts_golos_median))

        price_bts_golos_mean = statistics.mean(prices)
        log.debug('Mean market price: {:.8f} BTS/GOLOS'.format(price_bts_golos_mean))

        price_bts_golos_wa = self.calc_weighted_average_price(price_data)
        log.debug('Weighted average market price: {:.8f} BTS/GOLOS'.format(price_bts_golos_wa))

        if self.metric == Metric.median:
            price_bts_golos = price_bts_golos_median
        elif self.metric == Metric.mean:
            price_bts_golos = price_bts_golos_mean
        elif self.metric == Metric.weighted_average:
            price_bts_golos = price_bts_golos_wa
        else:
            raise ValueError('unsupported metric')

        return price_bts_golos

    async def calc_price_gbg_golos_bitshares(self) -> float:
        """Calculate price GBG/GOLOS using GOLOS markets on bitshares."""
        await self.bitshares.connect()

        try:
            price_usd_gold = await get_price_usd_gold_cbr()
            log.debug('Gold price from cbr.ru: %s USD/1mgGOLD', price_usd_gold)
        except Exception:
            log.exception('failed to calc BTS/GOLD price, trying fallback')
            try:
                feed = 'HONEST.XAU'
                price_troyounce = await self.bitshares.get_feed_price(feed, invert=True)
            except Exception:
                log.exception('%s feed failed', feed)
                feed = 'GOLD'
                price_troyounce = await self.bitshares.get_feed_price(feed, invert=True)

            price_bts_gold = price_troyounce_to_price_1mg(price_troyounce)
            log.debug('Gold price from %s feed, USD/1mg: %s', feed, price_bts_gold)
        else:
            try:
                market = 'BTS/RUDEX.USDT'
                price_usd_bts, _ = await self.bitshares.get_market_center_price(market, depth_pct=self.depth_pct)
                log.debug('Price USD/BTS taken from market %s: %s', market, price_usd_bts)
            except Exception:
                log.exception('failed to get USDT/BTS price from market')
                price_usd_bts = await self.bitshares.get_feed_price('HONEST.USD')
                log.debug('Price USD/BTS taken from HONEST.USD feed: %s', price_usd_bts)

            price_bts_gold = price_usd_gold / price_usd_bts
            log.info('Gold price in BTS: {:.8f} BTS/1mgGOLD'.format(price_bts_gold))

        price_bts_golos = await self.calc_price_bts_golos()
        log.info(f'GOLOS price is: {price_bts_golos:.8f} BTS/GOLOS')

        price_gold_golos = price_bts_golos / price_bts_gold
        log.info('Calculated price {:.3f} GBG/GOLOS'.format(price_gold_golos))

        return price_gold_golos

    async def calc_price_kuna(self) -> float:
        """Calculate price GBG/GOLOS using kuna.io GOL ticker."""
        price_usd_gold = await get_price_usd_gold_cbr()
        log.debug('Gold price from cbr.ru: %s USD/1mgGOLD', price_usd_gold)

        ticker = await fetch_ticker('kuna', 'GOL/BTC')
        price_btc_golos = ticker['last']
        log.info(f'BTC/GOLOS: {price_btc_golos:.8f}')

        ticker = await fetch_ticker('kuna', 'BTC/USDT')
        price_usd_btc = ticker['last']
        log.info(f'USDT/BTC: {price_usd_btc:.8f}')

        price_btc_gold = price_usd_gold / price_usd_btc
        log.info(f'BTC/1mgGOLD: {price_btc_gold:.8f}')

        price_gold_golos = price_btc_golos / price_btc_gold
        log.info('Calculated price {:.3f} GBG/GOLOS'.format(price_gold_golos))

        return price_gold_golos

    async def publish_price(self, force: bool = False) -> None:
        """
        Publish price feed once.

        :param bool force: force-publish price even if update is not needed
        """
        # flag variable which determine should we actually update price or not
        need_publish = False

        # calculate prices
        if self.price_source == PriceSource.bitshares:
            price = await self.calc_price_gbg_golos_bitshares()
        elif self.price_source == PriceSource.kuna:
            price = await self.calc_price_kuna()

        witness_data = Witness(self.witness)
        old_price = self.helper.get_witness_pricefeed(witness_data)

        median_price = self.helper.converter.sbd_median_price()
        log.info('current median price: {:.3f}'.format(median_price))

        # apply correction if k defined
        if self.correction != 1:
            price = price * self.correction
            log.info('price after correction: {:.3f}'.format(price))

        # check whether our price is too old
        last_price_update_too_old = self.is_last_price_too_old(witness_data, self.max_age)
        if last_price_update_too_old:
            log.info('Our last price update older than max_age, forcing update')
            need_publish = True

        # check for price difference between our old price and new price
        diff_rel = abs((old_price / price) - 1)
        if diff_rel > self.threshold_pct:
            log.info('publishing price, difference is: {:.2%}'.format(diff_rel))
            need_publish = True
        else:
            log.debug('price difference is too low, not publishing price')

        # finally publish price if needed
        if need_publish or force:
            if self.dry_run:
                log.info('--dry-run mode, not publishing price feed')
            else:
                final_gbg_price = format(price, '.3f')
                log.info('price to publish: %s' % final_gbg_price)
                self.helper.witness_feed_publish(final_gbg_price, quote='1.000', account=self.witness)

    async def run_forever(self) -> None:
        """Run in continuos mode to make price feed updates periodically."""
        # main loop
        while True:
            try:
                await self.publish_price()
            except Exception:
                log.exception('exception in main loop:')

            log.info('Sleeping for %s', self.interval)
            await asyncio.sleep(self.interval)
