import csv
import random
from flask_socketio import SocketIO

from kombu import Connection, Exchange, Queue
from kombu.mixins import ConsumerMixin

import config
from curve import calculate_pv_curve

CSV_FILENAME = './files/data.csv'
socketio = SocketIO(message_queue=config.AMPQ_URI)


class Worker(ConsumerMixin):
    """Consume events from meter, aggregates pv value
    and push to socketio"""

    meter_queue = Queue(
        name="meter",
        exchange=Exchange("meter", type="direct"),
        routing_key="meter")

    def __init__(self, connection):
        self.connection = connection

    def get_consumers(self, Consumer, channel):
        return [Consumer(queues=[self.meter_queue],
                         accept=['json', 'pickle'],
                         callbacks=[self.on_message])]

    def append_to_csv(self, body):
        row = [
            body['time'].timestamp(),
            body['pv'],
            body['power'],
            body['total']]
        with open(CSV_FILENAME, 'a') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(row)

    def truncate_csv(self):
        with open(CSV_FILENAME, 'w') as csvfile:
            csvfile.close()

    def on_message(self, body, message):
        if body['type'] == 'event':
            date = body['time']
            noise = random.uniform(-40, 40)
            body['pv'] = calculate_pv_curve(date)
            if body['pv'] >= 40:
                body['pv'] += noise
            body['total'] = body['power'] - body['pv']
            self.append_to_csv(body)
            socketio.emit('read', body, namespace='/reads')
        else:
            if body['type'] == 'start':
                self.truncate_csv()
            socketio.emit('command', body, namespace='/reads')
        message.ack()


if __name__ == '__main__':  # pragma: no cover
    with Connection(config.AMPQ_URI, heartbeat=4) as conn:
        worker = Worker(conn)
        worker.run()
