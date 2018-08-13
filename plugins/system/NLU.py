from geeteventbus.subscriber import subscriber
from utils import Logger, XEvent, Config
import json
import sys
import os

try:
    import apiai
except ImportError:
    sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
    import apiai

conf = Config()
lg = Logger(__file__)


class DFResult:
    def __init__(self, jres):
        self.fulfillment = jres.get('fulfillment', {})
        self.speech = jres.get('fulfillment', {'speech': 'N/A'})['speech']
        self.is_incomplete = jres.get('actionIncomplete', False)
        self.params = jres.get('parameters', {})
        self.action = jres.get('action', '')


class DFNLUPlugin(subscriber):
    def __init__(self, eb):
        super().__init__()
        self.apiai = None
        self.eb = eb

        try:
            self.access_key = conf['DFNLU']['access_key']
        except KeyError:
            raise ValueError('No DialogFlow API access!')

        try:
            self.language = conf['MAIN']['language']
        except KeyError:
            self.language = 'ru-RU'

        try:
            self.apiai = apiai.ApiAI(self.access_key)
        except Exception as ex:
            lg.error('Exception while initializing DialogFlow: %s' % str(ex))

    def process(self, eventobj):
        event = XEvent(eventobj)
        if event.cmd == 'run':
            res = self.run(event.data)
            if res:
                self.eb.send('results', 'nlu-result-ok', res)

    def run(self, data):
        if self.apiai:
            try:
                request = self.apiai.text_request()
                request.lang = 'ru'
                request.session_id = conf['DFNLU']['sessionid']
                request.query = data
                jres = json.loads(request.getresponse().read().decode('utf-8'), encoding='utf-8')['result']
                return DFResult(jres)
            except Exception as ex:
                lg.error('DialogFlow process failed with: %s' % str(ex))
        return None


def init(core):
    target = DFNLUPlugin(core.eventbus())
    core.eventbus().on('broadcast', target)
    core.eventbus().on('nlu', target)
