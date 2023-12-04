from . import _
from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.Sources.StaticText import StaticText
from Components.config import config
import skin
import os

from Plugins.Extensions.DGWeather.components.utils import *

def getSkinFileName():
    if 'VisualWeather' in config.plugins.dgWeather.Provider.value:
        VWskin = 'VisualWeather'
    else:
        VWskin = ''
    if 'OpenWeatherMap' in config.plugins.dgWeather.Provider.value:
        OWskin = 'OpenWeatherMap'
    else:
        OWskin = ''
    #budowa nazwy pliku skorki
    skinFileName = '%s%s.xml' % (VWskin, OWskin)
    if not os.path.join(os.path.join(skinPath,skinFileName)):
        skinFileName = 'VisualWeather.xml'
    write_log("loading %s skin" % skinFileName)
    return loadskin(skinFileName)

class VisualWeather(Screen):
    def __init__(self, session, args = None):
        self.skin = getSkinFileName()
        Screen.__init__(self, session)
        self.session = session
        self['key_red'] = StaticText('')
        self['key_red'].setText(_('Exit'))
        self['key_green'] = StaticText('')
        self['key_green'].setText(_('Setup'))
        self['actions'] = ActionMap(['OkCancelActions', 'InputActions', 'ColorActions'], {'red': self.cancel,
         'green': self.key_green,
         'cancel': self.cancel}, -1)
        self['astrodaylengthtxt'] = StaticText(_('Astro Day Length'))
        self['cloudcovertxt'] = StaticText(_('Cloud Cover'))
        self['countrytxt'] = StaticText(_('Country'))
        self['dewpointtxt'] = StaticText(_('Dew Point'))
        self['feelsliketxt'] = StaticText(_('Feels Like'))
        self['geolocationtxt'] = StaticText(_('Geo-Location'))
        self['hourlytxt'] = StaticText(_('Weather Hourly'))
        self['humiditytxt'] = StaticText(_('Humidity'))
        self['intensitytxt'] = StaticText(_('Intensity'))
        self['ozonetxt'] = StaticText(_('Ozone'))
        self['precipitationtxt'] = StaticText(_('Precipitation'))
        self['pressuretxt'] = StaticText(_('Pressure'))
        self['citenametxt'] = StaticText(_('City'))
        self['temperaturetxt'] = StaticText(_('Temperature'))
        self['timezonetxt'] = StaticText(_('Time Zone'))
        self['titletxt'] = StaticText(_('Weather'))
        self['updatetimetxt'] = StaticText(_('Update Time'))
        self['uvindextxt'] = StaticText(_('Uv Index'))
        self['visibilitytxt'] = StaticText(_('Visibility'))
        self['weektxt'] = StaticText(_('Weather Week'))
        self['winddirectiontxt'] = StaticText(_('Wind Direction'))
        self['windgusttxt'] = StaticText(_('Wind Gust'))
        self['windspeedtxt'] = StaticText(_('Wind Speed'))

    def key_green(self):
        from Plugins.Extensions.DGWeather.WeatherConfig import WeatherConfig
        self.session.open(WeatherConfig)
        self.close()

    def cancel(self):
        self.close()