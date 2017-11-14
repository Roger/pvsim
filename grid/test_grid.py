from statistics import mean

import pytest

from kombu import Connection
from main import Meter, Worker, SIM_FAST, QUIT_WAIT

# mean for offsets
means = [
    (offset, max(offset-60, 0), offset+60*140)
    for offset in range(0, 9000, 100)
    ]


def get_power(calls):
    """Filter power events
    """
    return [
        c[0][0]['power']
        for c in calls
        if c[0][0]['type'] == 'event'
    ]


@pytest.fixture
def worker_mock(mocker):
    connection = Connection('memory:///')
    mocker.patch('time.sleep')
    mock = mocker.patch.object(Worker, 'send_message')
    worker = Worker(connection)
    return worker, mock


@pytest.mark.parametrize("offset,min_mean,max_mean", means)
def test_worker_offset(worker_mock, mocker, offset, min_mean, max_mean):
    (worker, mock) = worker_mock

    worker.on_message({"type": "offset", "value": offset}, mocker.Mock())
    worker.on_message({"type": "sim_type", "value": SIM_FAST}, mocker.Mock())
    worker.on_message({"type": "start"}, mocker.Mock())
    # close and join thread
    worker.close(QUIT_WAIT)

    power_mean = mean(get_power(mock.call_args_list))
    assert power_mean > min_mean and power_mean <= max_mean


def test_worker_defaults(worker_mock, mocker):
    (worker, mock) = worker_mock

    worker.on_message({"type": "sim_type", "value": SIM_FAST}, mocker.Mock())
    worker.on_message({"type": "start"}, mocker.Mock())
    # close and join thread
    worker.close(QUIT_WAIT)

    power_mean = mean(get_power(mock.call_args_list))
    assert power_mean > 0 and power_mean < 9000


def test_meter(mocker):
    mocker.patch('time.sleep')
    mock = mocker.Mock()
    meter = Meter(mock)

    mock.assert_not_called()

    meter.loop()
    mock.assert_not_called()

    meter.on_cmd({"type": "start"})
    mock.assert_not_called()

    meter.loop()
    mock.assert_called()

    args = mock.call_args[0]
    assert args[0]['type'] == 'event'
    assert args[0]['power'] > 0
    assert args[0]['power'] <= 9000

    meter.on_cmd({"type": "offset", "value": 3000})
    meter.loop()
    args = mock.call_args[0]
    assert args[0]['type'] == 'event'
    assert args[0]['power'] >= 2940
    assert args[0]['power'] <= 3060

    mock.reset_mock()
    meter.on_cmd({"type": "stop"})
    mock.assert_not_called()
