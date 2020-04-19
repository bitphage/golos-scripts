import re
from collections import namedtuple

from golos import Steem
from golos.converter import Converter
from golos.instance import set_shared_steemd_instance

key_types = ['owner', 'active', 'posting', 'memo']
post_entry = namedtuple('post', ['author', 'permlink'])


class Helper(Steem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        set_shared_steemd_instance(self)

        self.converter = Converter()

    @staticmethod
    def parse_url(url: str) -> post_entry:
        """Parses an url to exctract author and permlink."""
        result = re.search(r'@(.*?)/([^/\ #$\n\']+)', url)
        if result is None:
            raise ValueError('Wrong URL')
        else:
            author = result.group(1)
            permlink = result.group(2)

        return post_entry(author, permlink)
