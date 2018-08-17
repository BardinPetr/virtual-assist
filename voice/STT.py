import xml.etree.ElementTree as XmlElementTree
from geeteventbus.subscriber import subscriber
from utils import Logger, XEvent, Config
import httplib2
import uuid

conf = Config()
lg = Logger(__file__)


class YandexSTTPlugin(subscriber):
    CHUNK_SIZE = 1024 ** 2

    def __init__(self, eb):
        super().__init__()
        self.eb = eb
        lg.info('STT starting...')
        try:
            self.access_key = conf['TTS']['access_key']
        except KeyError:
            raise ValueError("No Yandex API access!")

        try:
            self.language = conf['MAIN']['language']
        except KeyError:
            self.language = 'en-EN'

        if self.language.lower() not in ['ru-ru', 'en-en', 'tr-tr', 'uk-ua']:
            raise ValueError("Language '%s' not supported" % self.language)

        lg.info('STT started')

    def process(self, eventobj):
        event = XEvent(eventobj)
        if event.cmd == 'run':
            res = None
            try:
                res = self.speech_to_text(key=self.access_key,
                                          lang=self.language,
                                          filename=event.data)
            except Exception as ex:
                lg.error("Exception in STT: %s" % str(ex))
            else:
                if res:
                    self.eb.send('result', 'stt-result-ok', res)
        elif event.cmd == 'shutdown':
            self.eb.halted(__file__)

    @staticmethod
    def read_chunks(chunk_size, bytes):
        while True:
            chunk = bytes[:chunk_size]
            bytes = bytes[chunk_size:]
            yield chunk
            if not bytes:
                break

    def speech_to_text(self, key, filename=None, bytes=None, request_id=uuid.uuid4().hex, topic='queries',
                       lang='ru-RU'):
        lg.info('Transcribing file %s' % (filename or "%BYTES%"))
        if filename:
            with open(filename, 'br') as file:
                bytes = file.read()

        if not bytes:
            lg.error('No input for STT')

        url = '/asr_xml?uuid=%s&key=%s&topic=%s&lang=%s' % (
            request_id,
            key,
            topic,
            lang
        )

        chunks = self.read_chunks(YandexSTTPlugin.CHUNK_SIZE, bytes)

        connection = httplib2.HTTPConnectionWithTimeout('asr.yandex.net')

        connection.connect()
        connection.putrequest('POST', url)
        connection.putheader('Transfer-Encoding', 'chunked')
        connection.putheader('Content-Type', 'audio/x-wav')  # x-pcm;bit=16;rate=16000
        connection.endheaders()
        for chunk in chunks:
            connection.send(('%s\r\n' % hex(len(chunk))[2:]).encode())
            connection.send(chunk)
            connection.send('\r\n'.encode())
        connection.send('0\r\n\r\n'.encode())
        response = connection.getresponse()

        if response.code == 200:
            lg.debug('Transcribing finished with code 200(OK)')
            response_text = response.read()
            xml = XmlElementTree.fromstring(response_text)

            if int(xml.attrib['success']) == 1:
                max_confidence = - float("inf")
                text = ''

                for child in xml:
                    if float(child.attrib['confidence']) > max_confidence:
                        text = child.text
                        max_confidence = float(child.attrib['confidence'])

                if max_confidence != - float("inf"):
                    lg.info('Result fetched: %s' % text)
                    return text
                else:
                    lg.error('No text in STT response found.\nData:\n%s' % response_text)
            else:
                lg.error('No text in STT response found.\nData:\n%s' % response_text)
        else:
            lg.error('Unknown API error.\nCode: %s\n\n%s' % (response.code, response.read()))


def init(eventbus):
    target = YandexSTTPlugin(eventbus)
    eventbus.on('broadcast', target)
    eventbus.on('stt', target)
