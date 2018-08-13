from geeteventbus.eventbus import eventbus
from geeteventbus.event import event


class XEvent:
    module = None
    data = None
    cmd = None

    def __init__(self, eventobj):
        if not isinstance(eventobj, event):
            print('Invalid object type is passed.')
        data = eventobj.get_data()
        self.module, self.data, self.cmd = eventobj.get_topic(), data['data'], data['cmd']


class EventBus:
    def __init__(self):
        self.eb = eventbus()

    def reg_module(self, target):
        target.init(self)

    def on(self, topic, handler):
        self.eb.register_consumer(handler, topic)

    def send(self, module, cmd, data):
        self.eb.post(event(module, {'cmd': cmd, 'data': data}))

    def terminate(self):
        self.eb.shutdown()