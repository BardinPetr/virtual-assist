from geeteventbus.subscriber import subscriber
from utils import Logger, XEvent, Config

conf = Config()
lg = Logger(__file__)


# TODO add scheduler core
class ScheduledEvent:
    def __init__(self, eb, id, iterations, time, event):
        self.iterations = iterations
        self.event = event
        self.time = time
        self.id = id
        self.eb = eb

    def __call__(self):
        self.event(self.eb)

    def initialise(self):
        pass

    def killself(self):
        pass


class EventScheduler(subscriber):
    def __init__(self, eb):
        super().__init__()
        self.eb = eb
        self.events = {}

    def process(self, eventobj):
        event = XEvent(eventobj)
        if event.module == 'schedule':
            id = event.data['id']
            if event.cmd == 'add':
                self.events[id] = ScheduledEvent(**event.data)
            elif event.cmd == 'del':
                self.events[id].killself()
                self.events.pop(id)
        elif event.cmd == 'shutdown':
            self.eb.halted(__file__)


def init(core):
    target = EventScheduler(core.eventbus())
    core.eventbus().on('broadcast', target)
    core.eventbus().on('schedule', target)
