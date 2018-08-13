from geeteventbus.subscriber import subscriber
from utils import Logger, XEvent
import pyaudio
import wave

lg = Logger(__file__)


class Player(subscriber):
    def __init__(self, eb):
        super().__init__()
        lg.log('Initializing player')
        self.eb = eb
        self.audio = pyaudio.PyAudio()
        lg.log('Initializing player successfully finished')

    def process(self, eventobj):
        event = XEvent(eventobj)
        if event.cmd == 'play':
            self.play(event.data)
        elif event.cmd == 'shutdown':
            self.terminate()

    def play(self, file):
        lg.log('Playing file %s' % file)
        chunk = 1024
        f = wave.open(file, "rb")
        stream = self.audio.open(format=self.audio.get_format_from_width(f.getsampwidth()),
                                 channels=f.getnchannels(),
                                 rate=f.getframerate(),
                                 output=True)
        data = f.readframes(chunk)
        while data:
            stream.write(data)
            data = f.readframes(chunk)
        stream.stop_stream()
        stream.close()
        lg.log('Playing finished')

    def terminate(self):
        self.audio.terminate()


def init(eventbus):
    target = Player(eventbus)
    eventbus.on('audio', target)
    eventbus.on('broadcast', target)
