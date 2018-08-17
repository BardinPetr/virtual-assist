from utils import EventBus, Config
import signal
import voice
import core

eb = EventBus()

eb.reg_module(voice.capture, threaded=True)
eb.reg_module(voice.player)
eb.reg_module(voice.TTS)
eb.reg_module(voice.STT)

eb.reg_module(core)

signal.signal(signal.SIGINT, lambda x, y: eb.terminate())
