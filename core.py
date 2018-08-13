from geeteventbus.subscriber import subscriber
from utils import Logger, XEvent, Config
from pluginbase import PluginBase
from functools import partial
import os

here = os.path.abspath(os.path.dirname(__file__))
get_path = partial(os.path.join, here)

plugin_base = PluginBase(package='virtual-assist.plugins',
                         searchpath=[os.path.join(os.getcwd(), 'plugins', 'user'),
                                     os.path.join(os.getcwd(), 'plugins', 'system')])

conf = Config()
lg = Logger(__file__)


class Core(subscriber):
    def __init__(self, eb):
        super().__init__()
        self.eb = eb

        self.plugins = plugin_base.make_plugin_source(
            searchpath=[os.path.join(os.getcwd(), 'plugins', 'user'),
                        os.path.join(os.getcwd(), 'plugins', 'system')],
            identifier=__name__)

        for plugin_name in self.plugins.list_plugins():
            plugin = self.plugins.load_plugin(plugin_name)
            plugin.init(self)

    def process(self, eventobj):
        event = XEvent(eventobj)
        if event.module == 'result':
            if event.cmd == 'stt-result-ok':
                self.eb.send('nlu', 'run', event.data)

    def eventbus(self):
        return self.eb


def init(eventbus):
    target = Core(eventbus)
    eventbus.on('broadcast', target)
    eventbus.on('results', target)
