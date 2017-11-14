import time
import queue
import threading

import random
from datetime import datetime
from datetime import timedelta

from kombu import Connection, Exchange, Queue
from kombu.mixins import ConsumerProducerMixin

import config


SIM_REALTIME = 0
SIM_FAST = 1

QUIT_WAIT = 0   # wait for day to end to stop running(usefull in tests)
QUIT_NOW = 1    # quit without finishing generating the day


class Meter(threading.Thread):
    """Meter thread, that simulates comsume from the grid
    uses a queue to process commands and change parameters while running
    """
    def __init__(self, send_message, simulation_type=SIM_REALTIME, start=False,
                 offset=None, *args, **kwargs):
        super(Meter, self).__init__(*args, **kwargs)
        self.send_message = send_message
        self.simulation_type = simulation_type
        self.queue = queue.Queue()

        self.running = start
        self.power = offset and offset or random.randrange(0, 9000)
        # only used in SIM_FAST
        self.current_time = datetime.now().replace(hour=0, minute=0, second=0)
        self.setDaemon(False)
        self.quit = False

    def get_info(self):
        return {
            "running": self.running,
            "simulation_type": self.simulation_type,
            "power": self.power,
        }

    def on_cmd(self, cmd):
        self.queue.put(cmd)

    def process_commands(self):
        while True:
            try:
                cmd = self.queue.get(False)
                if cmd['type'] == 'start':
                    self.current_time = datetime.now().replace(
                            hour=0, minute=0, second=0)
                    self.running = True
                    self.send_message({"type": "start"})
                elif cmd['type'] == 'stop':
                    self.running = False
                    self.send_message({"type": "stop"})
                elif cmd['type'] == 'info':
                    self.send_message({
                        "type": "info",
                        "offset": self.power,
                        "sim_type": self.simulation_type,
                        "current_time": self.current_time,
                        })
                elif cmd['type'] == 'quit':
                    self.quit = cmd['value']
                elif cmd['type'] == 'offset':
                    self.power = cmd['value']
                    self.send_message({"type": "offset", "value": self.power})
                elif cmd['type'] == 'sim_type':
                    self.simulation_type = cmd['value']
                    if self.simulation_type == SIM_FAST:
                        self.current_time = self.current_time.replace(
                                hour=0, minute=0, second=0
                                )
                    self.send_message({
                        "type": "sim_type", "value": self.simulation_type
                        })

                else:
                    print('Unnknown Command', cmd)
            except queue.Empty:
                break

    def run(self):
        while True:
            self.loop()
            if (self.quit is QUIT_WAIT and not self.running) or \
                    self.quit is QUIT_NOW:
                break

    def loop(self):
        # if not running only keep listening to commands
        self.process_commands()
        if not self.running:
            time.sleep(0.5)
            return

        if self.simulation_type == SIM_REALTIME:
            time.sleep(1)
            current_time = datetime.now()
        else:
            time.sleep(1/32)
            current_time = self.current_time
            new_time = self.current_time + timedelta(seconds=60)
            if new_time.day != self.current_time.day:
                self.running = False
                self.send_message({"type": "end"})
            else:
                self.current_time = new_time

        power = self.power + random.randrange(-60, 60)
        if power < 0:
            power = 0

        self.send_message({
            "type": "event",
            "power": power,
            "time": current_time,
            })


class Worker(ConsumerProducerMixin):
    """Worker consuming commands from config channel
    and producing events from threads for meter channel
    """
    commands_queue = Queue(
        name="commands",
        exchange=Exchange("commands", type="direct"),
        routing_key="commands"
    )

    def __init__(self, connection):
        self.connection = connection

        self.meter = Meter(
            self.send_message,
            start=False,
            simulation_type=SIM_FAST
            )
        self.meter.start()

    def get_consumers(self, Consumer, channel):
        return [Consumer(queues=[self.commands_queue],
                         callbacks=[self.on_message])]

    def on_message(self, body, message):
        self.meter.on_cmd(body)

        message.ack()

    def send_message(self, message):
        self.producer.publish(
            message,
            exchange=Exchange('meter', type='direct'),
            routing_key='meter',
            serializer='pickle',
            )

    def close(self, wait=QUIT_NOW):
        self.meter.on_cmd({"type": "quit", "value": wait})
        self.meter.join()


if __name__ == '__main__':  # pragma: no cover
    with Connection(config.AMPQ_URI) as conn:
        worker = Worker(conn)
        worker.run()
