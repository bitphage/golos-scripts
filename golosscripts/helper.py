from golos import Steem
from golos.converter import Converter


class Helper(Steem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.converter = Converter(steemd_instance=self)
