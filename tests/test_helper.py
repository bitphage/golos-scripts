from golosscripts.helper import Helper


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
