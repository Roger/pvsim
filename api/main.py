# -*- coding: utf-8 -*-
from flask import Flask
from flask_socketio import SocketIO

import config
from utils import DateTimeEncoder, JsonWrapper
from kombu import Connection, Exchange


app = Flask(__name__)
app.json_encoder = DateTimeEncoder
socketio = SocketIO(app, message_queue=config.AMPQ_URI, json=JsonWrapper)

connection = Connection(config.AMPQ_URI)
producer = connection.Producer(
    exchange=Exchange("commands", type="direct"),
    routing_key="commands")


@socketio.on('command', namespace='/reads')
def handle_command(cmd, value=None):
    producer.publish({"type": cmd, "value": value})


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=6426)
