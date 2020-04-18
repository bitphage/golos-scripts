from golos import Steem
from golos.converter import Converter
from golos.instance import set_shared_steemd_instance

key_types = ['owner', 'active', 'posting', 'memo']


class Helper(Steem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        set_shared_steemd_instance(self)

        self.converter = Converter()
