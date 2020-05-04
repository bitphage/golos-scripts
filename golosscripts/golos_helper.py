import logging
import re
from collections import namedtuple
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union

from golos import Steem
from golos.account import Account
from golos.amount import Amount
from golos.converter import Converter
from golos.dex import Dex
from golos.instance import set_shared_steemd_instance
from golos.utils import parse_time
from golos.witness import Witness

STEEMIT_BANDWIDTH_AVERAGE_WINDOW_SECONDS = 60 * 60 * 24 * 7  # 7 days
STEEMIT_BANDWIDTH_PRECISION = 1000000
STEEMIT_100_PERCENT = 10000
STEEMIT_VOTE_REGENERATION_SECONDS = 5 * 60 * 60 * 24  # 5 days
STEEMIT_INFLATION_RATE_START_PERCENT = 1515
STEEMIT_INFLATION_RATE_STOP_PERCENT = 95
STEEMIT_INFLATION_NARROWING_PERIOD = 250000
STEEMIT_BLOCK_INTERVAL = 3
STEEMIT_BLOCKS_PER_YEAR = 365 * 24 * 60 * 60 / STEEMIT_BLOCK_INTERVAL
STEEMIT_BLOCKS_PER_DAY = 24 * 60 * 60 / STEEMIT_BLOCK_INTERVAL
STEEMIT_MAX_WITNESSES = 21
timeshare_weight = 5
top19_weight = 1
witness_pay_normalization_factor = 25

key_types = ['owner', 'active', 'posting', 'memo']
post_entry = namedtuple('post', ['author', 'permlink', 'id'])
bandwidth = namedtuple('bandwidth', ['used', 'avail', 'ratio'])
feed = namedtuple('feed', ['owner', 'price'])
emission = namedtuple(
    'emission',
    [
        'worker',
        'witness',
        'vesting',
        'content',
        'top19',
        'timeshare',
        'virtual_supply',
        'current_inflation_rate',
        'total',
    ],
)

log = logging.getLogger(__name__)


class GolosHelper(Steem):
    """
    Helper class for Golos which implements additional methods.

    Please see base class documentation on instantiation.

    .. note::

        On instantiation this class calls :py:func:`golos.instance.set_shared_steemd_instance`!
        This means all your golos objects like ``Account()`` etc will use that instance.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        set_shared_steemd_instance(self)

        self.converter = Converter()
        self.dex = Dex()

    @staticmethod
    def parse_url(url: str) -> post_entry:
        """
        Parses an url to exctract author and permlink.

        :param url: URL to post/comment
        :rtype: post_entry
        """
        result = re.search(r'@(.*?)/([^/\ #$\n\']+)', url)
        if result is None:
            raise ValueError('Wrong URL')
        else:
            author = result.group(1)
            permlink = result.group(2)

        post_id = '@{}/{}'.format(author, permlink)

        return post_entry(author, permlink, post_id)

    def get_bandwidth(self, account: str, type_: str = 'market') -> bandwidth:
        """
        Estimate current account bandwidth and usage ratio.

        :param str account: account name
        :param str type_: 'market' used for transfer operations, forum - for posting and voting,
            custom - custom ops
        """

        acc = Account(account)

        global_props = self.get_dynamic_global_properties()

        account_vshares = Amount(acc['vesting_shares'])['amount']
        delegated_vshares = Amount(acc['delegated_vesting_shares'])['amount']
        received_vshares = Amount(acc['received_vesting_shares'])['amount']
        account_vshares = account_vshares - delegated_vshares + received_vshares
        log.debug('{:.<30}{:.>30.0f}'.format('account_vshares:', account_vshares))

        # get bandwidth info from network
        if type_ == 'market':
            account_average_bandwidth = int(acc['average_market_bandwidth'])
            last_bw_update_time = parse_time(acc['last_market_bandwidth_update'])
        elif type_ == 'forum':
            account_average_bandwidth = int(acc['average_bandwidth'])
            last_bw_update_time = parse_time(acc['last_bandwidth_update'])
        elif type == 'custom':
            raise NotImplementedError

        # seconds passed since last bandwidth update
        elapsed_time = (datetime.utcnow() - last_bw_update_time).total_seconds()

        max_virtual_bandwidth = int(global_props['max_virtual_bandwidth'])
        log.debug('{:.<30}{:.>30.0f}'.format('max_virtual_bandwidth:', max_virtual_bandwidth))
        log.debug(
            '{:.<30}{:.>30.0f}'.format(
                'max_virtual_bandwidth, KB:', max_virtual_bandwidth / STEEMIT_BANDWIDTH_PRECISION / 1024
            )
        )

        total_vesting_shares = Amount(global_props['total_vesting_shares']).amount
        log.debug('{:.<30}{:.>30.0f}'.format('total_vesting_shares:', total_vesting_shares))

        # calculate bandwidth regeneration
        if elapsed_time > STEEMIT_BANDWIDTH_AVERAGE_WINDOW_SECONDS:
            new_bandwidth = 0
        else:
            new_bandwidth = (
                (STEEMIT_BANDWIDTH_AVERAGE_WINDOW_SECONDS - elapsed_time) * account_average_bandwidth
            ) / STEEMIT_BANDWIDTH_AVERAGE_WINDOW_SECONDS

        # example code to estimate whether your new transaction will exceed bandwidth or not
        # trx_size = 1024*2 # imagine 2 KB trx
        # trx_bandwidth = trx_size * STEEMIT_BANDWIDTH_PRECISION
        # account_average_bandwidth = new_bandwidth + trx_bandwidth

        account_average_bandwidth = new_bandwidth
        log.debug('{:.<30}{:.>30.0f}'.format('account_average_bandwidth:', account_average_bandwidth))

        # c++ code:
        # has_bandwidth = (account_vshares * max_virtual_bandwidth) > (account_average_bandwidth * total_vshares);

        avail = account_vshares * max_virtual_bandwidth
        used = account_average_bandwidth * total_vesting_shares
        log.debug('{:.<30}{:.>30.0f}'.format('used:', used))
        log.debug('{:.<30}{:.>30.0f}'.format('avail:', avail))

        used_ratio = used / avail
        log.debug('{:.<30}{:.>30.2%}'.format('used ratio:', used_ratio))

        # account bandwidth is actually a representation of sent bytes, so get these bytes
        used_kb = account_average_bandwidth / STEEMIT_BANDWIDTH_PRECISION / 1024

        # market ops uses x10 bandwidth
        if type_ == 'market':
            used_kb = used_kb / 10
        log.debug('{:.<30}{:.>30.2f}'.format('used KB:', used_kb))

        # available account bandwidth is a fraction of max_virtual_bandwidth based on his portion of
        # total_vesting_shares
        avail_kb = account_vshares / total_vesting_shares * max_virtual_bandwidth / STEEMIT_BANDWIDTH_PRECISION / 1024
        if type_ == 'market':
            avail_kb = avail_kb / 10
        log.debug('{:.<30}{:.>30.2f}'.format('avail KB:', avail_kb))

        if used < avail:
            log.debug('has bandwidth')
        else:
            log.debug('no bandwidth')

        return bandwidth(used_kb, avail_kb, used_ratio)

    def get_market_price(self, type_: str = 'bid') -> float:
        """
        Get current market price GBG/GOLOS from internal Dex.

        :param str type_: bid or ask
        :return: price as float
        """

        ticker = self.dex.get_ticker()
        if type_ == 'bid':
            price = ticker['highest_bid']
        elif type_ == 'ask':
            price = ticker['lowest_ask']

        return price

    def get_min_price(self) -> float:
        """Get GBG/GOLOS minimal price (limit by chain)."""

        props = self.get_dynamic_global_properties()
        sbd_supply = Amount(props['current_sbd_supply'])
        current_supply = Amount(props['current_supply'])

        # libraries/chain/database.cpp
        # this min_price caps system debt to 10% of GOLOS market capitalisation
        min_price = 9 * sbd_supply.amount / current_supply.amount

        return min_price

    def get_price_feeds(self) -> List[feed]:
        """Get current price feeds as reported by witnesses."""
        witnesses = self.get_active_witnesses()
        witnesses = [Witness(i) for i in witnesses]

        # add price key
        for i in witnesses:
            base = Amount(i['sbd_exchange_rate']['base']).amount
            quote = Amount(i['sbd_exchange_rate']['quote']).amount
            try:
                i['price'] = base / quote
            except ZeroDivisionError:
                pass

        feeds = [feed(i['owner'], i['price']) for i in witnesses if 'price' in i]
        feeds = sorted(feeds, key=lambda k: k.price)

        return feeds

    def get_witness_pricefeed(self, witness: Union[str, Dict]) -> float:
        """Obtain current published price for single witness."""

        if isinstance(witness, str):
            witness_data = Witness(witness)
        else:
            witness_data = witness
        base = Amount(witness_data['sbd_exchange_rate']['base']).amount
        quote = Amount(witness_data['sbd_exchange_rate']['quote']).amount

        # whether witness not exists yet, return 0
        if quote == 0:
            return 0

        price = base / quote

        return price

    def estimate_median_price(self) -> float:
        """Calculate new expected median price based on last median price feed."""

        last_feed = self.get_feed_history()['price_history'][-1]

        base = Amount(last_feed['base']).amount
        quote = Amount(last_feed['quote']).amount
        price = base / quote

        return price

    def get_voting_power(self, account: str) -> float:
        """
        Calculate real voting power instead of stale info in get_account()

        :param str account: account name
        :return: voting power 0-100
        """

        acc = Account(account)
        vp = acc.voting_power()

        last_vote_time = parse_time(acc['last_vote_time'])
        elapsed_time = datetime.utcnow() - last_vote_time

        regenerated_power = STEEMIT_100_PERCENT * elapsed_time.total_seconds() / STEEMIT_VOTE_REGENERATION_SECONDS
        current_power = min(vp + regenerated_power / 100, 100)

        return current_power

    def calc_inflation(
        self,
        start_block_num: Optional[int] = None,
        stop_block_num: Optional[int] = None,
        virtual_supply: Optional[float] = None,
        worker_percent: Optional[int] = None,
        witness_percent: Optional[int] = None,
        vesting_percent: Optional[int] = None,
        precise_rewards: bool = False,
    ) -> emission:
        """
        Calculate inflation in range from start block to stop block.

        :param int start_block_num: start block
        :param int stop_block_num: stop block
        :param float virtual_supply: initial virtual_supply
        :param int worker_percent: worker fund inflation percent (0-10000)
        :param int witness_percent: witness pay inflation percent (0-10000)
        :param int vesting_percent: vesting inflation percent (0-10000)
        :param bool precise_rewards: calculate precise witness reward; precise but slow;
            Gives a little better results (difference is very low)
        :return: new emission detailed data for requested period
        """
        props = self.get_dynamic_global_properties()

        if start_block_num is not None:
            start = start_block_num
        else:
            start = props['head_block_number']

        if stop_block_num is not None:
            stop = stop_block_num
        else:
            days = 1
            delta = timedelta(days=days)
            stop = start + int(delta.total_seconds() / STEEMIT_BLOCK_INTERVAL)

        log.debug(f'calculating inflation from block {start} to {stop}')

        if virtual_supply is not None:
            _virtual_supply = virtual_supply
        else:
            _virtual_supply = Amount(props['virtual_supply']).amount
            log.debug('current virtual_supply: {:,.0f}'.format(_virtual_supply))

        if worker_percent is not None and witness_percent is not None and vesting_percent is not None:
            _worker_percent = worker_percent
            _witness_percent = witness_percent
            _vesting_percent = vesting_percent
        else:
            log.debug('Using inflation distribution percents from median props')
            # get inflation params
            median_props = self.get_chain_properties()
            _worker_percent = median_props['worker_reward_percent']
            _witness_percent = median_props['witness_reward_percent']
            _vesting_percent = median_props['vesting_reward_percent']

        worker_reward_per_period = float()
        vesting_reward_per_period = float()
        witness_reward_per_period = float()
        content_reward_per_period = float()
        top19_reward_per_period = float()
        timeshare_reward_per_period = float()
        new_steem_total = float()

        start_inflation_rate = STEEMIT_INFLATION_RATE_START_PERCENT
        inflation_rate_floor = STEEMIT_INFLATION_RATE_STOP_PERCENT

        while start < stop:
            inflation_rate_adjustment = start / STEEMIT_INFLATION_NARROWING_PERIOD
            current_inflation_rate = max(start_inflation_rate - inflation_rate_adjustment, inflation_rate_floor)
            new_steem = _virtual_supply * current_inflation_rate / (STEEMIT_100_PERCENT * STEEMIT_BLOCKS_PER_YEAR)

            if precise_rewards:

                worker_reward = new_steem * _worker_percent / STEEMIT_100_PERCENT
                witness_reward = new_steem * _witness_percent / STEEMIT_100_PERCENT
                vesting_reward = new_steem * _vesting_percent / STEEMIT_100_PERCENT
                content_reward = new_steem - worker_reward - witness_reward - vesting_reward

                witness_reward = witness_reward * STEEMIT_MAX_WITNESSES
                if start % 21 == 0:
                    witness_reward = witness_reward * timeshare_weight
                    witness_reward = witness_reward / witness_pay_normalization_factor
                    timeshare_reward_per_period += witness_reward
                else:
                    witness_reward = witness_reward * top19_weight
                    witness_reward = witness_reward / witness_pay_normalization_factor
                    top19_reward_per_period += witness_reward

                new_steem = content_reward + vesting_reward + witness_reward

                worker_reward_per_period += worker_reward
                content_reward_per_period += content_reward
                vesting_reward_per_period += vesting_reward
                witness_reward_per_period += witness_reward

            _virtual_supply += new_steem
            new_steem_total += new_steem
            start += 1

        if precise_rewards:
            total = (
                content_reward_per_period
                + vesting_reward_per_period
                + witness_reward_per_period
                + content_reward_per_period
            )
        else:
            worker_reward_per_period = new_steem_total * _worker_percent / STEEMIT_100_PERCENT
            witness_reward_per_period = new_steem_total * _witness_percent / STEEMIT_100_PERCENT
            vesting_reward_per_period = new_steem_total * _vesting_percent / STEEMIT_100_PERCENT
            content_reward = (
                new_steem_total - worker_reward_per_period - witness_reward_per_period - vesting_reward_per_period
            )
            total = new_steem_total

        data = emission(
            worker_reward_per_period,
            witness_reward_per_period,
            vesting_reward_per_period,
            content_reward_per_period,
            top19_reward_per_period,
            timeshare_reward_per_period,
            _virtual_supply,
            current_inflation_rate / STEEMIT_100_PERCENT,
            total,
        )
        return data
