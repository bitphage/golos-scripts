import logging
import time
from datetime import datetime
from typing import List, Union

from golos.utils import parse_time
from golos.witness import Witness

from .golos_helper import GolosHelper

log = logging.getLogger(__name__)


class Monitor(GolosHelper):
    """Performs monitoring of missed blocks and automatically switches signing key."""

    def __init__(
        self,
        node: Union[str, List[str]],
        keys: Union[str, List[str]],
        witness: str,
        witness_pubkey: str,
        miss_window: int = 3600,
        allowed_misses: int = 1,
    ) -> None:
        """
        :param str,list node: golos node to connect to
        :param str,list keys: witness active keys
        :param str witness: witness name to update feed for
        :param str witness_pubkey: witness signing key
        :param int miss_window: time in seconds to observe block signing misses
        :param int allowed_misses: number of missed blocks per miss_window to allow before switching a key
        """

        self.witness = witness
        self.witness_pubkey = witness_pubkey
        self.miss_window = miss_window
        self.allowed_misses = allowed_misses

        self.miss_count = 0
        self.miss_window_start_time = datetime.now()

        # Helper setup
        super().__init__(nodes=node, keys=keys, num_retries=-1, mode='head')

    def check_node_sync(self) -> bool:
        """Checks if API node is in sync."""
        props = self.get_dynamic_global_properties()
        chain_time = parse_time(props['time'])
        time_diff = datetime.utcnow() - chain_time
        if time_diff.total_seconds() > 6:
            log.warning('node out of sync, timediff: {}, waiting...'.format(time_diff.total_seconds()))
            return False

        return True

    def set_miss_data(self, witness: Witness) -> None:
        self.miss_count = witness['total_missed']
        self.miss_window_start_time = datetime.now()

    def check_miss_window_end(self) -> bool:
        now = datetime.now()
        time_delta = now - self.miss_window_start_time

        if time_delta.total_seconds() > self.miss_window:
            return True

        return False

    def do_witness_check(self, witness: Witness) -> None:
        """Check whether witness configured on another node is missing blocks."""
        current_miss_count = witness['total_missed']
        miss_diff = current_miss_count - self.miss_count
        log.debug('current miss diff: {}'.format(miss_diff))

        if miss_diff > self.allowed_misses:
            log.info(
                'switching witness key, missed blocks exceed threshold: {} > {}'.format(miss_diff, self.allowed_misses)
            )
            self.witness_update(self.witness_pubkey, witness['url'], witness['props'], account=self.witness)
        elif self.check_miss_window_end():
            log.debug('miss_window ended, beginning a new one')
            self.set_miss_data(witness)

    def run_once(self) -> None:
        """Do miss check once."""
        in_sync = self.check_node_sync()
        if not in_sync:
            return

        witness = Witness(self.witness)
        producing_locally = witness['signing_key'] == self.witness_pubkey

        if producing_locally:
            if self.miss_count:
                log.info('stopping monitoring, reason: local block production')
            self.miss_count = 0
            return
        elif not self.miss_count:
            self.set_miss_data(witness)
            log.info('starting/resuming monitoring, current miss count: {}'.format(self.miss_count))
            return

        self.do_witness_check(witness)

    def run_forever(self) -> None:
        """Main loop."""
        while True:
            try:
                self.run_once()
            except Exception:
                log.exception('Exception in main loop')
            time.sleep(30)
