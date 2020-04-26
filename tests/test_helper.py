import pytest

from golosscripts.helper import Helper


@pytest.fixture(scope='module')
def helper(nodes):
    return Helper(nodes=nodes)


def test_parse_url():
    url = 'https://golos.id/@vvk/testpost'
    post = Helper.parse_url(url)
    assert post.author == 'vvk'
    assert post.permlink == 'testpost'

    url = 'https://golos.id/@vvk/testpost#@commenter/comment'
    post = Helper.parse_url(url)
    assert post.author == 'vvk'
    assert post.permlink == 'testpost'

    url = 'https://golos.id/@vvk/testpost something unrelated'
    post = Helper.parse_url(url)
    assert post.author == 'vvk'
    assert post.permlink == 'testpost'

    url = 'https://golos.id/@vvk/testpost\nadded_newline'
    post = Helper.parse_url(url)
    assert post.author == 'vvk'
    assert post.permlink == 'testpost'


def test_get_witness_pricefeed(helper):
    price = helper.get_witness_pricefeed('vvk')
    assert price > 0
