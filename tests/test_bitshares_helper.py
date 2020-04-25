import re

import pytest

from golosscripts.bitshares_helper import BitSharesHelper


@pytest.fixture()
def helper():
    return BitSharesHelper()


def test_get_market_center_price(helper):
    market = 'BTS/RUBLE'

    with pytest.raises(ValueError, match='expected depth_pct or base_amount or quote_amount'):
        helper.get_market_center_price(market)

    with pytest.raises(ValueError, match=re.escape('depth_pct and (base_amount, quote_amount) are mutually exclusive')):
        helper.get_market_center_price(market, base_amount=1, depth_pct=1)

    price, volume = helper.get_market_center_price(market, base_amount=1, quote_amount=1)
    assert price > 0
    assert volume > 0

    price, volume = helper.get_market_center_price(market, depth_pct=5)
    assert price > 0
    assert volume > 0
