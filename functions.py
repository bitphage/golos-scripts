#!/usr/bin/env python

import logging
import string
import random

from datetime import datetime
from datetime import timedelta

from piston import Steem
from piston.account import Account
from piston.amount import Amount
from piston.converter import Converter
from piston.dex import Dex

log = logging.getLogger(__name__)

CONTENT_CONSTANT = 2000000000000
STEEMIT_100_PERCENT = 10000
STEEMIT_VOTE_REGENERATION_SECONDS = 5*60*60*24 # 5 days
STEEMIT_BANDWIDTH_AVERAGE_WINDOW_SECONDS = 60*60*24*7 # 7 days
STEEMIT_BANDWIDTH_PRECISION = 1000000

def get_post_content(steem_instance, author, permlink):
    """ Wrapper for Steem.get_content()
        :param Steem steem_instance: Steem() instance to use when accesing a RPC
        :param str author: post author
        :param str permlink: post permlink
    """

    post_id = '@{}/{}'.format(author, permlink)
    try:
        p = steem_instance.get_content(post_id)
    except Exception as e:
        log.error(e)
        return False
    return p

def get_net_rshares(steem_instance, author, permlink):
    """ Get net_rshares for post
        :param Steem steem_instance: Steem() instance to use when accesing a RPC
        :param str author: post author
        :param str permlink: post permlink
    """
    p = get_post_content(steem_instance, author, permlink)
    if not p:
        return False

    # net_rshares is a sum of all rshares
    net_rshares = int(p['net_rshares'])
    log.debug('post net_rshares: %s', net_rshares)
    return net_rshares

def calc_rshares(steem_instance, account, vote_percent):
    """ Calc current rshares for an account
        :param Steem steem_instance: Steem() instance to use when accesing a RPC
        :param str account:
        :param float vote_percent: up percent, 0-100
    """

    a = Account(account, steem_instance=steem_instance)
    cv = Converter(steem_instance)
    try:
        voting_power = get_voting_power(steem_instance, account)
        b = steem_instance.get_balances(account=account)
        log.info('current voting_power: {}, {:.2f}'.format(account, voting_power))
    except Exception as e:
        log.error('error in calc_rshares(): %s', e)
        return False

    # look for detailed code in libraries/chain/steem_evaluator.cpp, search used_power

    vesting_shares = b['vesting_shares']
    sp = cv.vests_to_sp(vesting_shares.amount)
    rshares = cv.sp_to_rshares(sp, voting_power=voting_power*100, vote_pct=vote_percent*100)

    return rshares


def get_median_price(steem_instance):
    """ get current median GBG/GOLOS price from network
        :param Steem steem_instance: Steem() instance to use when accesing a RPC
    """

    cv = Converter(steem_instance)
    try:
        price = cv.sbd_median_price()
    except Exception as e:
        log.error(e)
        return False

    log.debug('current median price: %s', price)
    return price

def get_market_price(steem_instance):
    """
    Get current market price GBG/GOLOS
        :param Steem steem_instance: Steem() instance to use when accesing a RPC
        :return float price: return float or False
    """

    try:
        d = Dex(steem_instance=steem_instance)
        bid = d.get_higest_bid()
    except Exception as e:
        log.error(e)
        return False

    log.debug('current market price: %s', bid['price'])
    return bid['price']


def convert_golos_to_gbg(steem_instance, amount, price_source='median'):
    """ Take GOLOS and convert to GBG using median or market price
        :param Steem steem_instance: Steem() instance to use when accesing a RPC
        :param float amount
        :param str price_source: where to get price from - median or market
    """

    if price_source == 'median':
        price = get_median_price(steem_instance)
    elif price_source == 'market':
        price = get_market_price(steem_instance)
    else:
        log.error('unknown price_source')
        return False

    if not price:
        return False
    value = amount * price
    return value

def convert_gbg_to_golos(steem_instance, amount, price_source='median'):
    """ Convert GBG to GOLOS
        :param Steem steem_instance: Steem() instance to use when accessing a RPC
        :param float amount: amount of GBG to convert
        :param str price_source: where to get price from - median or market
    """

    if price_source == 'median':
        price = get_median_price(steem_instance)
    elif price_source == 'market':
        price = get_market_price(steem_instance)

    if not price:
        return False
    value = amount / price
    return value

def calc_payout(steem_instance, net_rshares):
    """ Calc payout in GOLOS based on net_rshares
        https://golos.io/ru--apvot50-50/@now/kak-na-samom-dele-rabotayut-kvadratichnye-nachisleniya-golosa-2kh-50-50
        :param Steem steem_instance: Steem() instance to use when accesing a RPC
        :param int net_rshares: net_rshares to calculate payout from
        :return float payout: payout amount in GOLOS
    """

    try:
        global_props = steem_instance.info()
    except Exception as e:
        log.error(e)
        return False

    # perform same calculations as golosd v0.16.4
    # c++ code: return (rshares + s) * (rshares + s) - s * s;
    vshares = (net_rshares + CONTENT_CONSTANT) * (net_rshares + CONTENT_CONSTANT) - CONTENT_CONSTANT**2

    total_reward_fund_steem = Amount(global_props['total_reward_fund_steem'])
    total_reward_shares2 = int(global_props['total_reward_shares2'])
    payout = vshares * total_reward_fund_steem.amount / total_reward_shares2
    log.debug('calculated post payout, GOLOS: {:.8f}'.format(payout))
    return payout

def estimate_author_payout(steem_instance, pending_payout_value):
    """ Estimate author payout
        :param Steem steem_instance: Steem() instance to use when accesing a RPC
        :param Amount pending_payout_value: Amount object representing amount in GBG or GOLOS
    """

    if pending_payout_value.asset == 'GOLOS':
        log.error('expected GBG for pending_payout_value')
        return False

    # subtract curators reward
    author_reward = pending_payout_value.amount * 0.75
    half = author_reward / 2

    # Golos Power
    author_payout_gp = convert_gbg_to_golos(steem_instance, half)

    # determine GBG payout
    props = steem_instance.info()
    author_payout_gbg = half * props['sbd_print_rate'] / STEEMIT_100_PERCENT

    # determine GOLOS payout
    reminder = half - author_payout_gbg
    author_payout_golos = convert_gbg_to_golos(steem_instance, reminder)

    return author_payout_gp, author_payout_gbg, author_payout_golos


def get_voting_power(steem_instance, account):
    """ Calculate real voting power instead of stale info in get_account()
        :param Steem steem_instance: Steem() instance to use when accesing a RPC
        :param str account: account name
    """

    try:
        a = Account(account, steem_instance=steem_instance)
        vp = a.voting_power()
    except Exception as e:
        log.error('error in get_voting_power(): %s', e)
        return False

    last_vote_time = datetime.strptime(a['last_vote_time'], '%Y-%m-%dT%H:%M:%S')
    elapsed_time = datetime.utcnow() - last_vote_time

    regenerated_power = STEEMIT_100_PERCENT * elapsed_time.total_seconds() / STEEMIT_VOTE_REGENERATION_SECONDS
    current_power = vp + regenerated_power/100
    if current_power > 100:
        current_power = 100
    return current_power

def get_bandwidth(steem_instance, account, type='market'):
    """ Estimate current account bandwidth and usage ratio
        :param Steem steem_instance: Steem() instance to use when accesing a RPC
        :param str account: account name
        :param str type: 'market' used for transfer operations, forum - for posting and voting
    """

    a = Account(account, steem_instance=steem_instance)

    global_props = steem_instance.info()

    account_vshares = Amount(a['vesting_shares']).amount
    log.debug('account_vshares: {:.>50.0f}'.format(account_vshares))

    # get bandwidth info from network
    if type == 'market':
        account_average_bandwidth = int(a['new_average_market_bandwidth'])
        last_bw_update_time = datetime.strptime(a['last_market_bandwidth_update'], '%Y-%m-%dT%H:%M:%S')
    elif type == 'forum':
        account_average_bandwidth = int(a['new_average_bandwidth'])
        last_bw_update_time = datetime.strptime(a['last_bandwidth_update'], '%Y-%m-%dT%H:%M:%S')

    # seconds passed since last bandwidth update
    elapsed_time = (datetime.utcnow() - last_bw_update_time).total_seconds()

    max_virtual_bandwidth = int(global_props['max_virtual_bandwidth'])
    log.debug('max_virtual_bandwidth: {:.>44.0f}'.format(max_virtual_bandwidth))

    total_vesting_shares = Amount(global_props['total_vesting_shares']).amount
    log.debug('total_vesting_shares: {:.>45.0f}'.format(total_vesting_shares))


    # calculate bandwidth regeneration
    if elapsed_time > STEEMIT_BANDWIDTH_AVERAGE_WINDOW_SECONDS:
        new_bandwidth = 0
    else:
        new_bandwidth = (((STEEMIT_BANDWIDTH_AVERAGE_WINDOW_SECONDS - elapsed_time) * account_average_bandwidth)
                / STEEMIT_BANDWIDTH_AVERAGE_WINDOW_SECONDS)

    # example code to estimate whether your new transaction will exceed bandwidth or not
    #trx_size = 1024*2 # imagine 2 KB trx
    #trx_bandwidth = trx_size * STEEMIT_BANDWIDTH_PRECISION
    #account_average_bandwidth = new_bandwidth + trx_bandwidth

    account_average_bandwidth = new_bandwidth
    log.debug('account_average_bandwidth: {:.>40.0f}\n'.format(account_average_bandwidth))


    # c++ code:
    # has_bandwidth = (account_vshares * max_virtual_bandwidth) > (account_average_bandwidth * total_vshares);

    avail = account_vshares * max_virtual_bandwidth
    used = account_average_bandwidth * total_vesting_shares


    log.info('used: {:.>62.0f}'.format(used))
    log.info('avail: {:.>61.0f}'.format(avail))
    log.info('used ratio: {:.>56.2%}'.format(used/avail))

    if used < avail:
        log.debug('has bandwidth')
    else:
        log.debug('no bandwidth')

    return used/avail * 100


def generate_password(size=53, chars=string.ascii_letters + string.digits):
    """ Generate random word with letters and digits
    """
    return ''.join(random.choice(chars) for x in range(size))
