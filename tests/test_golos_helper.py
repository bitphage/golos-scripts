import pytest

from golosscripts.golos_helper import GolosHelper


@pytest.fixture(scope='module')
def helper(nodes):
    return GolosHelper(nodes=nodes)


def test_parse_url():
    url = 'https://golos.id/@vvk/testpost'
    post = GolosHelper.parse_url(url)
    assert post.author == 'vvk'
    assert post.permlink == 'testpost'

    url = 'https://golos.id/@vvk/testpost#@commenter/comment'
    post = GolosHelper.parse_url(url)
    assert post.author == 'vvk'
    assert post.permlink == 'testpost'

    url = 'https://golos.id/@vvk/testpost something unrelated'
    post = GolosHelper.parse_url(url)
    assert post.author == 'vvk'
    assert post.permlink == 'testpost'

    url = 'https://golos.id/@vvk/testpost\nadded_newline'
    post = GolosHelper.parse_url(url)
    assert post.author == 'vvk'
    assert post.permlink == 'testpost'

    url = 'https://example.com/xynta'
    with pytest.raises(ValueError, match='Wrong URL'):
        post = GolosHelper.parse_url(url)


def test_get_witness_pricefeed(helper):
    price = helper.get_witness_pricefeed('vvk')
    assert price > 0
