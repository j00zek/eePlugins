from Components.config import config
from Components.Language import language
from Plugins.Plugin import PluginDescriptor

from importlib import reload
import os
from . import _

from Plugins.Extensions.DGWeather.components.utils import *
from Plugins.Extensions.DGWeather.components.WeatherData import WeatherData

def main(session, **kwargs):
    if config.plugins.dgWeather.StartScreen.value == 'cst' and config.plugins.dgWeather.Provider.value == 'VisualWeather':
        import Plugins.Extensions.DGWeather.VisualWeather
        reload(Plugins.Extensions.DGWeather.VisualWeather)
        session.open(Plugins.Extensions.DGWeather.VisualWeather.VisualWeather)
    elif config.plugins.dgWeather.StartScreen.value == 'cst' and config.plugins.dgWeather.Provider.value == 'OpenWeathermap':
        import Plugins.Extensions.DGWeather.OpenWeathermap
        reload(Plugins.Extensions.DGWeather.OpenWeathermap)
        session.open(Plugins.Extensions.DGWeather.OpenWeathermap.OpenWeathermap)
    elif config.plugins.dgWeather.StartScreen.value == 'cst' and config.plugins.dgWeather.Provider.value == 'WeatherBit':
        import Plugins.Extensions.DGWeather.WeatherBit
        reload(Plugins.Extensions.DGWeather.WeatherBit)
        session.open(Plugins.Extensions.DGWeather.WeatherBit.WeatherBit)
    else:
        from Plugins.Extensions.DGWeather.SettingsView import SettingsView
        session.open(SettingsView)

weather_data = None

def AutoStart(reason, **kwargs):
    global weather_data
    if reason == 0: # Enigma start
        try:
            os.system('echo "SYSTEM RESTARTED" > /tmp/dgWeather/dgWeather.log')
            if weather_data is None:
                weather_data = WeatherData()
                weather_data.GetWeather()
            write_log('AutoStart() zainicjowano weather_data')
        except Exception:
            Exc_log()
                

def Plugins(**kwargs):
    return [PluginDescriptor(name='myDGWeather', description=_('Configuration tool for DGWeather_FHD'), where=PluginDescriptor.WHERE_PLUGINMENU, icon='plugin.png', fnc=main),
            PluginDescriptor(where = PluginDescriptor.WHERE_AUTOSTART, needsRestart = True, fnc = AutoStart)
           ]
