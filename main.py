from utils import EventBus, Config
import voice

eb = EventBus()

eb.reg_module(voice.player)
eb.reg_module(voice.TTS)
eb.reg_module(voice.STT)

eb.send('broadcast', 'shutdown', None)
eb.terminate()
