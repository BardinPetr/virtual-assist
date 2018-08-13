from geeteventbus.subscriber import subscriber
from snowboy import snowboydecoder
from utils.eventbus import XEvent
from utils.logger import Logger
from utils.config import Config
import alsaaudio
import webrtcvad
import wave
import time

lg = Logger(__file__)


class Capture(subscriber):
    MAX_RECORDING_LENGTH = 8

    VAD_SAMPLERATE = 16000
    VAD_FRAME_MS = 30
    VAD_PERIOD = int((VAD_SAMPLERATE / 1000) * VAD_FRAME_MS)
    VAD_SILENCE_TIMEOUT = 1000
    VAD_THROWAWAY_FRAMES = 10

    _vad = None
    _hwd = None
    _config = None
    _state_callback = None

    def __init__(self, eb):
        super().__init__()
        self._config = Config()['AUDIO']
        self.validate_config()
        self.running = False
        self.eb = eb

    def process(self, eventobj):
        event = XEvent(eventobj)
        if event.cmd == 'shutdown':
            pass

    def validate_config(self):
        input_device = self._config['input_device']
        input_devices = alsaaudio.pcms(alsaaudio.PCM_CAPTURE)

        if (input_device not in input_devices) and (not self._config['allow_unlisted_input_device']):
            raise Exception(
                "Your input_device '" + input_device + "' is invalid. Use one of the following:\n"
                + '\n'.join(input_devices))

    def setup(self, state_callback=None):
        self._vad = webrtcvad.Vad(2)
        self._state_callback = state_callback

        self._hwd = snowboydecoder.HotwordDetector("../assets/hotwords/h0.pmdl", sensitivity=0.1, audio_gain=1)
        self._hwd.start(lambda x: self.silence_listener())

    def silence_listener(self, throwaway_frames=None, force_record=None):
        if self.running:
            return False
        self.running = True
        throwaway_frames = throwaway_frames or self.VAD_THROWAWAY_FRAMES

        lg.info("Hotword detected!")
        lg.debug("Setting up recording")

        # Re-enable reading microphone raw data
        inp = alsaaudio.PCM(alsaaudio.PCM_CAPTURE, alsaaudio.PCM_NORMAL, self._config['input_device'])
        inp.setchannels(1)
        inp.setrate(self.VAD_SAMPLERATE)
        inp.setformat(alsaaudio.PCM_FORMAT_S16_LE)
        inp.setperiodsize(self.VAD_PERIOD)

        audio = wave.open('../temp_voice/' + 'recording.wav', 'wb')
        audio.setframerate(self.VAD_SAMPLERATE)
        audio.setnchannels(1)
        audio.setsampwidth(2)

        start = time.time()

        do_VAD = True
        if force_record and not force_record[1]:
            do_VAD = False

        # Buffer as long as we haven't heard enough silence or the total size is within max size
        threshold_silence_met = False
        frames = 0
        num_silence_runs = 0
        silence_run = 0

        lg.debug("Start recording...")

        if self._state_callback:
            self._state_callback()

        if do_VAD:
            # do not count first 10 frames when doing VAD
            while frames < throwaway_frames:
                length, data = inp.read()
                frames += 1
                if length:
                    audio.writeframes(data)

        # now do VAD
        while (force_record and force_record[0]()) or \
                (do_VAD and (threshold_silence_met is False) and
                 ((time.time() - start) < self.MAX_RECORDING_LENGTH)):

            length, data = inp.read()
            if length:
                audio.writeframes(data)

                if do_VAD and (length == self.VAD_PERIOD):
                    is_speech = self._vad.is_speech(data, self.VAD_SAMPLERATE)

                    if not is_speech:
                        silence_run += 1
                    else:
                        silence_run = 0
                        num_silence_runs += 1

            if do_VAD:
                if (num_silence_runs != 0) and ((silence_run * self.VAD_FRAME_MS) > self.VAD_SILENCE_TIMEOUT):
                    threshold_silence_met = True

        lg.debug("End recording")

        inp.close()

        if self._state_callback:
            self._state_callback(False)

        audio.close()

        self.running = False
        return


def init(eventbus):
    target = Capture(eventbus)
    eventbus.on('capture', target)
    eventbus.on('broadcast', target)
