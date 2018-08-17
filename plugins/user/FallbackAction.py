from geeteventbus.subscriber import subscriber
from utils import Logger, XEvent, Config

conf = Config()
lg = Logger(__file__)


class FallbackAction(subscriber):
    def __init__(self, eb):
        super().__init__()
        self.eb = eb

    def process(self, eventobj):
        event = XEvent(eventobj)
        if event.cmd == 'shutdown':
            self.eb.halted(__file__)
        elif event.module == 'result' and \
                event.cmd == 'nlu-result-ok' and \
                event.data.action == 'input.unknown':
            self.eb.send('tts', 'run', {"phrase": event.data.speech})


def init(core):
    target = FallbackAction(core.eventbus())
    core.eventbus().on('broadcast', target)
    core.eventbus().on('result', target)
