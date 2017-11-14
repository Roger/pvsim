from datetime import datetime

import pytest

from kombu import Connection
from main import Worker
from curve import calculate_pv_curve


curve_values = [
    [0, 0, 0.0],
    [2, 0, 0.0],
    [6, 0, 0.0],
    [12, 0, 3044.0],
    [18, 0, 1887.0],
    [21, 0, 0.0],
    [22, 0, 0.0],
    [23, 59, 0.0],
]


@pytest.fixture
def worker_mock(mocker):
    connection = Connection('memory:///')
    mock = mocker.patch('flask_socketio.SocketIO.emit')
    worker = Worker(connection)
    return worker, mock


@pytest.mark.parametrize("hour,minute,value", curve_values)
def test_curve(hour, minute, value):
    time = datetime(2017, 11, 16, hour, minute)
    assert pytest.approx(calculate_pv_curve(time), 0.01) == value


@pytest.mark.parametrize("hour,minute,value", curve_values)
def test_worker(mocker, worker_mock, hour, minute, value):
    (worker, mock) = worker_mock

    power = 200
    time = datetime(2017, 11, 16, hour, minute)
    worker.on_message({
        "type": "event",
        "time": time,
        "power": power},
        mocker.Mock())
    io_msg = mock.call_args[0][1]
    # take into account the noise
    assert io_msg['type'] == 'event'
    assert io_msg['power'] == power
    assert io_msg['pv'] >= value - 41
    assert io_msg['pv'] <= value + 41
    assert io_msg['total'] >= (power - value - 41)
    assert io_msg['total'] <= (power - value + 41)

    mock.reset_mock()
    worker.on_message({"type": "start"}, mocker.Mock())
    io_msg = mock.call_args[0][1]
    assert io_msg['type'] == 'start'
