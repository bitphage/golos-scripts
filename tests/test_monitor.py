from datetime import datetime

import pytest
from graphenecommon.utils import formatTime

from golosscripts.monitor import Monitor

witness = {'signing_key': 'key_of_another_node', 'total_missed': 10, 'url': 'none', 'props': 'xxxx'}


@pytest.fixture()
def monitor(nodes):
    # Key is just random, don't bother
    config = {
        'witness': 'lex',
        'node': nodes,
        'keys': '5JypMRUoJpsTZcYw2y9PX58WeHa937eJE3FzhA1cQe9zsHTHCWd',
        'witness_pubkey': 'GLS89Tvw7offn5QrGE1fXFxhxyKkSxTqeSUSztLZgsWCJLoRQPbEs',
    }

    return Monitor(**config)


def test_check_node_sync(monitor, monkeypatch):
    def mock1():
        return {'time': '2020-04-30T06:03:00'}

    def mock2():
        return {'time': formatTime(datetime.utcnow())}

    monkeypatch.setattr(monitor, 'get_dynamic_global_properties', mock1)
    assert monitor.check_node_sync() is False

    monkeypatch.setattr(monitor, 'get_dynamic_global_properties', mock2)
    assert monitor.check_node_sync() is True


def test_check_miss_window_end(monitor):
    assert monitor.check_miss_window_end() is False

    monitor.miss_window_start_time = datetime(2000, 1, 1)
    assert monitor.check_miss_window_end() is True


def test_do_witness_check(monitor, monkeypatch, mocker):
    mocker.patch('golos.commit.Commit.witness_update')
    monitor.do_witness_check(witness)
    monitor.witness_update.assert_called_once()

    monkeypatch.setitem(witness, 'total_missed', 0)
    monkeypatch.setattr(monitor, 'check_miss_window_end', lambda: True)
    spy = mocker.spy(monitor, 'set_miss_data')
    monitor.do_witness_check(witness)
    spy.assert_called_once()


class TestRunOnce:
    @pytest.fixture()
    def monitor(self, monitor, monkeypatch):
        monkeypatch.setattr(monitor, 'check_node_sync', lambda: True)
        return monitor

    def test_producing_locally(self, monitor, mocker, monkeypatch):

        monkeypatch.setitem(witness, 'signing_key', monitor.witness_pubkey)
        mocker.patch('golosscripts.monitor.Witness', return_value=witness)
        monitor.run_once()

    def test_not_miss_count(self, monitor, mocker):
        mocker.patch('golosscripts.monitor.Witness', return_value=witness)
        spy = mocker.spy(monitor, 'set_miss_data')
        monitor.run_once()
        spy.assert_called_once()

    def test_do_check(self, monitor, mocker):
        mocker.patch('golosscripts.monitor.Witness', return_value=witness)
        monitor.miss_count = 1
        mocker.patch('golos.commit.Commit.witness_update')
        spy = mocker.spy(monitor, 'do_witness_check')
        monitor.run_once()
        spy.assert_called_once()
