from . import _
from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.ConfigList import ConfigListScreen
from Components.Sources.StaticText import StaticText
from Components.config import config, getConfigListEntry, ConfigNothing
from Plugins.Extensions.DGWeather.WeatherConfig import WeatherConfig
import skin
from importlib import reload

from Plugins.Extensions.DGWeather.components.utils import * 

class SettingsView(Screen, ConfigListScreen):
    skin = """<screen name="SettingsView" backgroundColor="#30000000" size="1100,900" position="60,104">
                <widget name="config" position="19,15" size="1071,800" font="Regular; 32" itemHeight="45" scrollbarMode="showOnDemand" backgroundColor="background" transparent="1" />
                <widget source="key_red" render="Label" position="20,850" size="280,38" foregroundColor="red" backgroundColor="black" zPosition="1" transparent="1" font="Regular;30" halign="left" />
                <widget source="key_green" render="Label" position="305,850" size="280,38" foregroundColor="green" backgroundColor="black" zPosition="1" transparent="1" font="Regular;30" halign="left" />
                <widget source="key_yellow" render="Label" position="589,850" size="280,38" foregroundColor="yellow" backgroundColor="black" zPosition="1" transparent="1" font="Regular;30" halign="left" />
                <widget source="key_blue" render="Label" position="870,850" size="280,38" foregroundColor="blue" backgroundColor="black" zPosition="1" transparent="1" font="Regular;30" halign="left" />
              </screen>"""

    def __init__(self, session, args = 0):
        write_log('SettingsView().__init__() >>>') 
        Screen.__init__(self, session)
        self.session = session
        self.list = []
        ConfigListScreen.__init__(self, self.list, session=self.session)
        self['titleText'] = StaticText(_('DGWeather'))
        self['key_red'] = StaticText(_('Exit'))
        self['key_green'] = StaticText('')
        self['key_yellow'] = StaticText('')
        self['key_blue'] = StaticText(_('Weather'))
        self['setupActions'] = ActionMap(['OkCancelActions', 'ColorActions'], {'ok': self.keyOk,
         'red': self.cancel,
         'blue': self.key_blue,
         'cancel': self.cancel}, -1)
        self.createConfigList()

    def createConfigList(self):
        self.weather = getConfigListEntry(_('Weather settings'), ConfigNothing())
        self.list = []
        self.list.append(self.weather)
        self['config'].list = self.list
        self['config'].l.setList(self.list)

    def keyOk(self):
        write_log('SettingsView().keyOk() >>>') 
        sel = self['config'].getCurrent()
        if sel is not None and sel == self.weather:
            self.session.open(WeatherConfig)
        return

    def key_blue(self):
        if config.plugins.dgWeather.Provider.value == 'VisualWeather':
            write_log('SettingsView().key_blue() opening VisualWeather') 
            import Plugins.Extensions.DGWeather.VisualWeather
            reload(Plugins.Extensions.DGWeather.VisualWeather)
            self.session.open(Plugins.Extensions.DGWeather.VisualWeather.VisualWeather)
        elif config.plugins.dgWeather.Provider.value == 'OpenWeathermap':
            write_log('SettingsView().key_blue() opening OpenWeathermap') 
            import Plugins.Extensions.DGWeather.OpenWeathermap
            reload(Plugins.Extensions.DGWeather.OpenWeathermap)
            self.session.open(Plugins.Extensions.DGWeather.OpenWeathermap.OpenWeathermap)
        elif config.plugins.dgWeather.Provider.value == 'WeatherBit':
            write_log('SettingsView().key_blue() opening WeatherBit') 
            import Plugins.Extensions.DGWeather.WeatherBit
            reload(Plugins.Extensions.DGWeather.WeatherBit)
            self.session.open(Plugins.Extensions.DGWeather.WeatherBit.WeatherBit)

    def cancel(self):
        self.close()