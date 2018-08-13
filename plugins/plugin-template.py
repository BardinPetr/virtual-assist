from geeteventbus.subscriber import subscriber
from utils import Logger, XEvent, Config

conf = Config()
lg = Logger(__file__)


class MyPlugin(subscriber):
    def __init__(self, eb):
        super().__init__()
        self.eb = eb

    def process(self, eventobj):
        event = XEvent(eventobj)


def init(core):
    target = MyPlugin(core.eventbus())
    core.eventbus().on('broadcast', target)
    core.eventbus().on('smth0', target)
    core.eventbus().on('smth1', target)
    core.eventbus().on('smth2', target)
