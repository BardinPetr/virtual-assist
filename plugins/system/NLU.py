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

    def __str__(self):
        return '<DFResult: Action %s; FF %s; II %s; Params %s' % (self.action, str(self.fulfillment),
                                                                  str(self.is_incomplete), str(self.params))

    def __repr__(self):
        return '<DFResult: Action %s; FF %s; II %s; Params %s' % (self.action, str(self.fulfillment),
                                                                  str(self.is_incomplete), str(self.params))


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
            self.apiai._base_url = conf['DFNLU'].get('base_url', 'api.api.ai')
        except Exception as ex:
            lg.error('Exception while initializing DialogFlow: %s' % str(ex))

    def process(self, eventobj):
        event = XEvent(eventobj)
        if event.cmd == 'run':
            res = self.run(event.data)
            if res:
                self.eb.send('result', 'nlu-result-ok', res)
        elif event.cmd == 'shutdown':
            self.eb.halted(__file__)

    def run(self, data):
        if self.apiai:
            try:
                lg.info('Sending request to APIAI')
                request = self.apiai.text_request()
                request.lang = 'ru'
                request.session_id = conf['DFNLU']['sessionid']
                request.query = data
                jres = json.loads(request.getresponse().read().decode('utf-8'), encoding='utf-8')['result']
                data = DFResult(jres)
                lg.info('APIAI result fetched with action: %s' % data.action)
                return data
            except Exception as ex:
                lg.error('DialogFlow process failed with: %s' % str(ex))
        return None


def init(core):
    target = DFNLUPlugin(core.eventbus())
    core.eventbus().on('broadcast', target)
    core.eventbus().on('nlu', target)
