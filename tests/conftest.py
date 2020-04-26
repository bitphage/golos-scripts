import asyncio
import logging

import pytest

log = logging.getLogger('golosscripts')
log.setLevel(logging.DEBUG)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def nodes():
    nodes = [
        'wss://golos.lexa.host/ws',
        'wss://golos.solox.world/ws',
        'wss://api.golos.blckchnd.com/ws' 'wss://api-full.golos.id/ws',
    ]
    return nodes


@pytest.fixture(scope="session")
def node_bts():
    return 'wss://eu.nodes.bitshares.ws'
