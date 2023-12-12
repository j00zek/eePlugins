from Components.Language import language
from Plugins.Plugin import PluginDescriptor
from Components.config import config
import os
from Plugins.Extensions.DGWeather.SettingsView import SettingsView
from Plugins.Extensions.DGWeather.VisualWeather import VisualWeather
from . import _

from Plugins.Extensions.DGWeather.components.utils import *
from Plugins.Extensions.DGWeather.components.WeatherData import WeatherData

def main(session, **kwargs):
    if config.plugins.dgWeather.StartScreen.value == 'cfg':
        session.open(SettingsView)
    elif config.plugins.dgWeather.StartScreen.value == 'cst':
        session.open(VisualWeather)
    else:
        session.open(SettingsView)

def AutoStart(reason, **kwargs):
    if reason == 0: # Enigma start
        try:
            os.system('echo "SYSTEM RESTARTED" > /tmp/dgWeather/dgWeather.log')
            try:
                WeatherData().GetWeather()
            except Exception:
                pass
            write_log('AutoStart() zainicjowano weather_data')
        except Exception:
            Exc_log()
                

def Plugins(**kwargs):
    return [PluginDescriptor(name='myDGWeather', description=_('Configuration tool for DGWeather_FHD'), where=PluginDescriptor.WHERE_PLUGINMENU, icon='plugin.png', fnc=main),
            PluginDescriptor(where = PluginDescriptor.WHERE_AUTOSTART, needsRestart = True, fnc = AutoStart)
           ]
