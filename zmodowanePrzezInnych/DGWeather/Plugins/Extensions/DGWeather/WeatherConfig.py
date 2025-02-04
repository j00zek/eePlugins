from . import _
from enigma import eTimer, ePoint
from Components.ActionMap import ActionMap
from Components.config import *
from Components.ConfigList import ConfigListScreen
from Components.Label import Label
from Components.Pixmap import Pixmap
from Components.Sources.List import List
from Components.Sources.StaticText import StaticText
from Components.Language import language
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Screens.Standby import TryQuitMainloop
from Tools.Directories import *
from Tools.LoadPixmap import LoadPixmap
from Tools import Notifications
from xml.etree.cElementTree import fromstring as cet_fromstring
from os import listdir, remove, rename, system, path, symlink, chdir, makedirs
import shutil
import skin
import os

from Plugins.Extensions.DGWeather.components.utils import *

class WeatherConfig(Screen, ConfigListScreen):
    skin = """<screen name="WeatherConfig" backgroundColor="#30000000" size="1300,900" position="60,104">
                <widget name="config" position="15,15" size="1270,800" font="Regular; 32" itemHeight="45" scrollbarMode="showOnDemand" scrollbarWidth="4" scrollbarSliderForegroundColor="scrolbar_color" scrollbarSliderBorderWidth="0" backgroundColor="background" transparent="1" />
                <widget source="key_red" render="Label" position="20,850" size="280,38" foregroundColor="red" backgroundColor="black" zPosition="1" transparent="1" font="Regular;30" halign="left" />
                <widget source="key_green" render="Label" position="305,850" size="280,38" foregroundColor="green" backgroundColor="black" zPosition="1" transparent="1" font="Regular;30" halign="left" />
                <widget source="key_yellow" render="Label" position="589,850" size="280,38" foregroundColor="yellow" backgroundColor="black" zPosition="1" transparent="1" font="Regular;30" halign="left" />
                <widget source="key_blue" render="Label" position="870,850" size="280,38" foregroundColor="blue" backgroundColor="black" zPosition="1" transparent="1" font="Regular;30" halign="left" />
            </screen>"""

    def __init__(self, session, args = 0):
        write_log('WeatherConfig().__init__() >>>')
        self.session = session
        Screen.__init__(self, session)
        write_log('Screen.__init__()')
        self.list = []
        ConfigListScreen.__init__(self, self.list, session=self.session)
        write_log('ConfigListScreen.__init__()')
        #VTI nie obsluguje setTitle
        try: self.setTitle(_('VisualWeather VisualWeather Config'))
        except Exception: pass
        self['titleText'] = StaticText(_('VisualWeather VisualWeather Config'))
        self['key_red'] = StaticText(_('Cancel'))
        self['key_green'] = StaticText(_('OK'))
        self['key_yellow'] = StaticText('')
        self['key_blue'] = StaticText('')
        self['setupActions'] = ActionMap(['DirectionActions', 'SetupActions', 'ColorActions'], {'green': self.save,
         'left': self.keyLeft,
         'right': self.keyRight,
         'ok': self.save,
         'red': self.cancel,
         'cancel': self.cancel}, -2)
        self.timer = eTimer()
        self.timer.callback.append(self.createConfigList)
        self.onLayoutFinish.append(self.createConfigList)
        #self['HelpWindow'] = Pixmap()

    def createConfigList(self):
        write_log('WeatherConfig().createConfigList() >>>')
        tab = '          '
        self.list = []
        self.list.append(getConfigListEntry(_('Temperature unit'), config.plugins.dgWeather.tempUnit))
        self.list.append(getConfigListEntry(_('Windspeed unit'), config.plugins.dgWeather.windspeedUnit))
        self.list.append(getConfigListEntry(_('Wind Direction'), config.plugins.dgWeather.winddirection))
        self.list.append(getConfigListEntry(_('Pressure unit'), config.plugins.dgWeather.pressureUnit))
        self.list.append(getConfigListEntry(_('Weekday format'), config.plugins.dgWeather.WeekDay))
        self.list.append(getConfigListEntry(_('StartScreen'), config.plugins.dgWeather.StartScreen))
        self.list.append(getConfigListEntry(_('Weather Picon'), config.plugins.dgWeather.animatedWeather))
        self.list.append(getConfigListEntry(_('Provider'), config.plugins.dgWeather.Provider))
        self.list.append(getConfigListEntry(_('Number of decimal places'), config.plugins.dgWeather.numbers))
        self.list.append(getConfigListEntry(_('Refresh interval'), config.plugins.dgWeather.refreshInterval))
        self.list.append(getConfigListEntry(_('Language (weather descriptions)'), config.plugins.dgWeather.CountryCode))
        #geo
        self.list.append(getConfigListEntry(_('Location latitude)'), config.plugins.dgWeather.geolatitude))
        self.list.append(getConfigListEntry(_('Location longitude)'), config.plugins.dgWeather.geolongitude))
        #self.list.append(getConfigListEntry(_('Location name)'), config.plugins.dgWeather.geoLocationName))
        #airly
        self.list.append(getConfigListEntry(_('Airly location ID'), config.plugins.dgWeather.airlyID))
        self.list.append(getConfigListEntry(_('Airly APIKEY'), config.plugins.dgWeather.airlyAPIKEY))
        #klucze API
        self.list.append(getConfigListEntry(_('VisualWeather API-Key'), config.plugins.dgWeather.VisualWeather_apikey))
        self.list.append(getConfigListEntry(_('OpenWeathermap API-Key'), config.plugins.dgWeather.OpenWeathermap_apikey))
        self.list.append(getConfigListEntry(_('WeatherBit API-Key'), config.plugins.dgWeather.WeatherBit_apikey))
        self['config'].list = self.list
        self['config'].l.setList(self.list)

    def keyLeft(self):
        ConfigListScreen.keyLeft(self)
        self.mylist()

    def keyRight(self):
        ConfigListScreen.keyRight(self)
        self.mylist()

    def mylist(self):
        self.timer.start(100, True)

    def cancel(self):
        for x in self['config'].list:
            if len(x) > 1:
                x[1].cancel()

        self.close(self.session, True)

    def save(self):
        for x in self['config'].list:
            if len(x) > 1:
                x[1].save()

        configfile.save()
        restartbox = self.session.openWithCallback(self.restartGUI, MessageBox, _('Restart necessary, restart GUI now?'), MessageBox.TYPE_YESNO)
        restartbox.setTitle(_('Question'))

    def restartGUI(self, answer):
        if answer is True:
            configfile.save()
            self.session.open(TryQuitMainloop, 3)