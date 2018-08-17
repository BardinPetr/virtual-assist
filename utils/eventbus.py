from geeteventbus.eventbus import eventbus
from geeteventbus.event import event
from threading import Thread
from utils import logger
import signal
import os

lg = logger.Logger(__file__)


class XEvent:
    module = None
    data = None
    cmd = None

    def __init__(self, eventobj=None, m=None, d=None, c=None):
        if not isinstance(eventobj, event):
            self.module = m
            self.data = d
            self.cmd = c
        else:
            data = eventobj.get_data()
            self.module, self.data, self.cmd = eventobj.get_topic(), data['data'], data['cmd']

    def __call__(self, eb):
        eb.send(self.module, {'cmd': self.cmd, 'data': self.data})


class EventBus:
    running_modules = 0

    def __init__(self):
        self.eb = eventbus()

    def reg_module(self, target, threaded=False):
        if threaded:
            t = Thread(target=target.init, args=(self,))
            t.start()
        else:
            target.init(self)
        self.running_modules += 1

    def halted(self, module):
        lg.warning('%s halted' % module)
        self.running_modules -= 1
        if self.running_modules == 0:
            lg.critical("Killing myself by SIGTERM...")
            os.kill(os.getpid(), signal.SIGTERM)
            lg.critical("Killing myself by SIGKILL...")
            os.kill(os.getpid(), signal.SIGKILL)

    def on(self, topic, handler):
        self.eb.register_consumer(handler, topic)

    def send(self, module, cmd, data):
        self.eb.post(event(module, {'cmd': cmd, 'data': data}))

    def terminate(self):
        self.send('broadcast', 'shutdown', None)
