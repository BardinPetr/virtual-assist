from geeteventbus.subscriber import subscriber
from utils import Logger, XEvent, Config

conf = Config()
lg = Logger(__file__)


class Core(subscriber):
    def __init__(self, eb):
        super().__init__()
        self.eb = eb

    def process(self, eventobj):
        event = XEvent(eventobj)
        if event.cmd == '':
            pass


def init(eventbus):
    target = Core(eventbus)
    eventbus.on('broadcast', target)
    eventbus.on('results', target)
