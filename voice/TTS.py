from geeteventbus.subscriber import subscriber
from utils import Logger, XEvent, Config
from yandex_speech import TTS as YaTTS
from hashlib import md5
import os

conf = Config()
lg = Logger(__file__)


class YandexTTSPlugin(subscriber):
    """
    Uses the Yandex SpeechKit Cloud services.
    SpeechKit Cloud is a multilingual TTS and STT platform developed by Yandex.
    """

    def __init__(self, eb):
        super().__init__()
        self.tts = None
        self.eb = eb

        try:
            self.access_key = conf['TTS']['access_key']
        except KeyError:
            raise ValueError("No Yandex API access!")

        try:
            self.voice = conf['TTS']['voice']
        except KeyError:
            self.voice = "alyss"

        try:
            self.language = conf['MAIN']['language']
        except KeyError:
            self.language = 'ru-RU'

        if self.language.lower() not in ['ru-ru', 'en-en', 'tr-tr', 'uk-ua']:
            raise ValueError("Language '%s' not supported" % self.language)

    def process(self, eventobj):
        event = XEvent(eventobj)
        if event.cmd == 'run':
            self.say(**event.data)
        elif event.cmd == 'shutdown':
            self.eb.halted(__file__)

    def say(self, phrase, **kwargs):
        """
        Method used to utter words using the Yandex TTS plugin
        :param phrase:
        """
        phash = md5(phrase.encode('utf-8')).hexdigest()
        fname = os.path.join(os.getcwd(), 'temp_voice', '%s.wav' % phash)
        try:
            open(fname, 'r')
        except FileNotFoundError:
            lg.info('Preparing TTS...')
            try:
                if not self.tts:
                    self.tts = YaTTS(self.voice,
                                     "wav",
                                     lang=self.language,
                                     key=self.access_key)
            except Exception as ex:
                lg.error("Exception while loading TTS: %s" % str(ex))
                return None
            lg.info('Running TTS for phrase "%s"' % phrase)
            try:
                self.tts.generate(phrase)
                self.tts.save(path=fname)
            except Exception as ex:
                lg.error("Exception while running TTS: %s" % str(ex))
                return None
        with open(fname, 'rb') as f:
            data = f.read()
        if kwargs.get('autoplay', True):
            self.eb.send('audio', 'play', fname)
        return data


def init(eventbus):
    target = YandexTTSPlugin(eventbus)
    eventbus.on('broadcast', target)
    eventbus.on('tts', target)
