# -*- coding: utf-8 -*-
#
# WeatherPlugin E2
#
# Initially coded by Dr.Best (c) 2012
# Modified by j00zek 2018/2019
#
# This plugin is open source but it is NOT free software.
#
# This plugin may only be distributed to and executed on hardware which
# is licensed by Dream Multimedia GmbH.
# In other words:
# It's NOT allowed to distribute any parts of this plugin or its source code in ANY way
# to hardware which is NOT licensed by Dream Multimedia GmbH.
# It's NOT allowed to execute this plugin and its source code or even parts of it in ANY way
# on hardware which is NOT licensed by Dream Multimedia GmbH.
#
# If you want to use or modify the code or parts of it,
# you have to keep MY license and inform me about the modifications by mail.
#

from . import _
from Components.ActionMap import ActionMap
from Components.config import ConfigSubsection, ConfigSubList, ConfigInteger, config, NoSave, ConfigEnableDisable, ConfigSelection, ConfigText, ConfigIP, ConfigYesNo, ConfigNothing
#from Components.Pixmap import Pixmap
from Components.j00zekAccellPixmap import j00zekAccellPixmap
from Components.Label import Label
from Components.Sources.StaticText import StaticText
from debug import printDEBUG
from getWeather import getWeather
from Plugins.Plugin import PluginDescriptor
#from datetime import datetime, timedelta
#from enigma import eTimer
#from random import randint
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from setup import initConfig, MSNWeatherEntriesListConfigScreen
from Tools.Directories import resolveFilename, SCOPE_SKIN
from Tools.LoadPixmap import LoadPixmap
from version import Version
import time, os

DBG = False

config.plugins.WeatherPlugin = ConfigSubsection()
config.plugins.WeatherPlugin.entrycount =  ConfigInteger(0)
config.plugins.WeatherPlugin.currEntry =  NoSave(ConfigInteger(0))
config.plugins.WeatherPlugin.callbacksCount =  NoSave(ConfigInteger(0))
config.plugins.WeatherPlugin.FakeEntry = NoSave(ConfigNothing())
config.plugins.WeatherPlugin.Entry = ConfigSubList()

availableOptions = [("serviceIcons", _("MSN service icons"))]
if os.path.exists(os.path.dirname(resolveFilename(SCOPE_SKIN, config.skin.primary_skin.value)) + '/weather_icons/'):
    availableOptions.append(("weatherIcons", _("skin Icons")))
if os.path.exists('/usr/share/enigma2/animatedWeatherIcons'):
    availableOptions.append(("animIcons", _("animated Icons")))

config.plugins.WeatherPlugin.IconsType = ConfigSelection(choices = availableOptions, default = "serviceIcons")
config.plugins.WeatherPlugin.ScalePicType = ConfigSelection(choices = [ ("self.instance.setScale", _("internal E2")),
                                                                        ("ePicLoad", _("ePicLoad (E.g. Vu+ org)")) ],
                                                            default = "self.instance.setScale")

config.plugins.WeatherPlugin.BuildHistograms = ConfigEnableDisable(default = False)

config.plugins.WeatherPlugin.SensorsPriority = ConfigSelection(choices = [ ("AcTsAirlyMsn", _("AcTsAirlyMsn")),
                                                                           ("AcAirlyTsMsn", _("AcAirlyTsMsn")),
                                                                           ("AirlyTsAcMsn", _("AirlyTsAcMsn")),
                                                                           ("TsAirlyAcMsn", _("TsAirlyAcMsn")),
                                                                         ],
                                                                default = "AcTsAirlyMsn"
                                                               )

config.plugins.WeatherPlugin.AC1 = ConfigSelection(choices = [ ("off", _("not installed")), ("daikin", _("Daikin Air Conditioner")) , ("samsung", _("Samsung Air Conditioner"))], default = "off")
config.plugins.WeatherPlugin.AC1_IP = ConfigIP(default = [0,0,0,0])
config.plugins.WeatherPlugin.AC1_PORT = ConfigInteger(default = 80,limits=(80,999))
config.plugins.WeatherPlugin.AC1inf = ConfigText(default = _("AC in the living room"), visible_width = 100, fixed_size = False)
config.plugins.WeatherPlugin.AC2 = ConfigSelection(choices = [ ("off", _("not installed")), ("daikin", _("Daikin Air Conditioner")) , ("samsung", _("Samsung Air Conditioner"))], default = "off")
config.plugins.WeatherPlugin.AC2_IP = ConfigIP(default = [0,0,0,0])
config.plugins.WeatherPlugin.AC2_PORT = ConfigInteger(default = 80,limits=(80,999))
config.plugins.WeatherPlugin.AC2inf = ConfigText(default = _("AC in the bedroom"), visible_width = 100, fixed_size = False)


if os.path.exists('/hdd/User_Configs/airlyAPIKEY'):
    config.plugins.WeatherPlugin.airlyAPIKEY = ConfigText(default = open('/hdd/User_Configs/airlyAPIKEY', 'r').readline().strip(), visible_width = 100, fixed_size = False)
elif os.path.exists('/etc/enigma2/Airly/api.txt'):
    config.plugins.WeatherPlugin.airlyAPIKEY = ConfigText(default = open('/etc/enigma2/Airly/api.txt', 'r').readline().strip(), visible_width = 100, fixed_size = False)
else:
    config.plugins.WeatherPlugin.airlyAPIKEY = ConfigText(default = "", visible_width = 100, fixed_size = False)

config.plugins.WeatherPlugin.DebugEnabled = ConfigEnableDisable(default = False)
config.plugins.WeatherPlugin.DebugSize = ConfigSelection(choices = [ ("10000", "10KB"), ("100000", "100KB"), ("1000000", "1MB"), ], default = "10000")

config.plugins.WeatherPlugin.DebugWeatherMSNupdater = ConfigEnableDisable(default = False)
config.plugins.WeatherPlugin.DebugMSNWeatherSource = ConfigEnableDisable(default = False)
config.plugins.WeatherPlugin.DebugMSNWeatherConverter = ConfigEnableDisable(default = False)

config.plugins.WeatherPlugin.DebugMSNWeatherPixmapRenderer = ConfigEnableDisable(default = False)

config.plugins.WeatherPlugin.DebugMSNWeatherThingSpeakConverter = ConfigEnableDisable(default = False)
config.plugins.WeatherPlugin.DebugMSNWeatherWebCurrentConverter = ConfigEnableDisable(default = False)
config.plugins.WeatherPlugin.DebugMSNWeatherWebhourlyConverter = ConfigEnableDisable(default = False)
config.plugins.WeatherPlugin.DebugMSNWeatherWebDailyConverter = ConfigEnableDisable(default = False)

config.plugins.WeatherPlugin.DebugGetWeatherBasic = ConfigEnableDisable(default = False)
config.plugins.WeatherPlugin.DebugGetWeatherXML = ConfigEnableDisable(default = False)
config.plugins.WeatherPlugin.DebugGetWeatherWEB = ConfigEnableDisable(default = False)
config.plugins.WeatherPlugin.DebugGetWeatherTS = ConfigEnableDisable(default = False)
config.plugins.WeatherPlugin.DebugGetWeatherFULL = ConfigEnableDisable(default = False)
config.plugins.WeatherPlugin.DebugMSNweatherHistograms = ConfigEnableDisable(default = False)
config.plugins.WeatherPlugin.DebugMSNweatherMaps = ConfigEnableDisable(default = True)

config.plugins.WeatherPlugin.HistoryPeriod = ConfigSelection(choices = [ ("86400", _("Last 24h")), ("43200", _("Last 12h")), ("21600", _("Last 6h")), ("10800", _("Last 3h")), ("3600", _("Last hour")), ], default = "43200")

printDEBUG('INIT', ' MSNweather NP plugin %s' % Version)
printDEBUG('config.plugins.WeatherPlugin.IconsType = "%s"' % config.plugins.WeatherPlugin.IconsType.value)

initConfig()

try:
    from updater import weathermsn
    WeatherMSNComp = weathermsn
    #printDEBUG('WeatherMSNComp initiated invoking getData()')
    #WeatherMSNComp.getData()
except Exception as e:
    WeatherMSNComp = None
    printDEBUG('Exception: %s' % str(e))

def main(session,**kwargs):
    session.open(MSNweather)

def sessionstart(session, **kwargs):
    session.screen["MSNWeather"] = getWeather()

def Plugins(**kwargs):
    list = [
        PluginDescriptor(name=_("MSN weather NP"), where = [PluginDescriptor.WHERE_PLUGINMENU, PluginDescriptor.WHERE_EXTENSIONSMENU], icon = "weather.png", fnc=main),
        PluginDescriptor(where = [PluginDescriptor.WHERE_SESSIONSTART], fnc = sessionstart)
    ]
    return list

class MSNweather(Screen):
    skin = """
        <screen name="MSNweather" position="center,center" size="664,340" title="MSN weather NP">
            <widget render="Label" source="caption" position="10,20" zPosition="1" size="600,28" font="Regular;24" transparent="1"/>
            <widget render="Label" source="observationtime" position="374,45" zPosition="1" size="280,20" font="Regular;14" transparent="1" halign="right" />
            <widget render="Label" source="observationpoint" position="204,65" zPosition="1" size="450,40" font="Regular;14" transparent="1" halign="right" />
            <widget name="currenticon" position="10,95" zPosition="1" size="55,45" alphatest="blend"/>
            <widget render="Label" source="currentTemp" position="90,95" zPosition="1" size="100,23" font="Regular;22" transparent="1"/>
            <widget render="Label" source="feelsliketemp" position="90,120" zPosition="1" size="155,40" font="Regular;14" transparent="1"/>
            <widget render="Label" source="condition" position="270,95" zPosition="1" size="300,20" font="Regular;18" transparent="1"/>
            <widget render="Label" source="wind_condition" position="270,115" zPosition="1" size="300,20" font="Regular;18" transparent="1"/>
            <widget render="Label" source="humidity" position="270,135" zPosition="1" size="300,20" font="Regular;18" valign="bottom" transparent="1"/>
            
            <ePixmap pixmap="skin_default/buttons/red.png" position="0,300" size="35,27" alphatest="on" />
            <widget name="key_red" position="40,300" size="150,35" font="Roboto_HD; 24" backgroundColor="black" transparent="1"/>
            
            <ePixmap pixmap="skin_default/buttons/green.png" position="160,300" size="140,40" alphatest="on" />
            <widget name="key_green" position="40,300" size="150,35" font="Roboto_HD; 24" backgroundColor="black" transparent="1"/>

            <ePixmap pixmap="skin_default/buttons/yellow.png" position="330,300" size="140,40" alphatest="on" />
            <widget name="key_yellow" position="40,300" size="150,35" font="Roboto_HD; 24" backgroundColor="black" transparent="1"/>

            <ePixmap pixmap="skin_default/buttons/blue.png" position="490,300" size="140,40" alphatest="on" />
            <widget name="key_blue" position="40,300" size="150,35" font="Roboto_HD; 24" backgroundColor="black" transparent="1"/>

            <widget source="session.CurrentService" render="Label" position="10,295" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" >
              <convert type="j00zekTranslator">Close</convert>
            </widget>
            <widget source="session.CurrentService" render="Label" position="190,295" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" >
              <convert type="j00zekTranslator">Show Maps</convert>
            </widget>
            <widget source="session.CurrentService" render="Label" position="370,295" zPosition="1" size="180,40" font="Regular;20" halign="center" valign="center" backgroundColor="#a08500" transparent="1" >
              <convert type="j00zekTranslator">Show Histograms</convert>
            </widget>
        </screen>"""
    
    def __init__(self, session):
        Screen.__init__(self, session)
        self.title = _("MSN weather NP @j00zek %s" % Version)
        self.setTitle(_("MSN weather NP @j00zek %s") % Version) 
        self["actions"] = ActionMap(["MSNweatherNP"],

        {
            "keyCancel": self.close,
            "keyMenu": self.config,
            "keyRight": self.nextItem,
            "keyLeft": self.previousItem,
            "keyRed": self.keyRed,
            "keyGreen": self.keyGreen,
            "keyYellow": self.keyYellow,
            "keyBlue": self.keyBlue,
        }, -1)

        self["statustext"] = StaticText()
        self["currenticon"] = j00zekAccellPixmap()
        self["caption"] = StaticText()
        self["currentTemp"] = StaticText()
        self["condition"] = StaticText()
        self["wind_condition"] = StaticText()
        self["humidity"] = StaticText()
        self["observationtime"] = StaticText()
        self["observationpoint"] = StaticText()
        self["feelsliketemp"] = StaticText()

        self["key_red"] = Label(config.plugins.WeatherPlugin.AC1inf.value)
        self["key_green"] = Label(config.plugins.WeatherPlugin.AC2inf.value)
        self["key_yellow"] = Label(_("Show Histograms"))
        self["key_blue"] = Label(_("Show Maps"))

        self.weatherPluginEntryIndex = -1
        self.weatherPluginEntry = None
        try:
            config.plugins.WeatherPlugin.currEntry.value = 0
            self.weatherPluginEntryCount = config.plugins.WeatherPlugin.entrycount.value
            if self.weatherPluginEntryCount >= 1:
                self.weatherPluginEntry = config.plugins.WeatherPlugin.Entry[0]
                self.weatherPluginEntryIndex = 1
        except Exception as e:
            printDEBUG('MSNweather.__init__', ' Exception %s' % str(e))


        self.webSite = ""
        
        self.weatherData = None
        self.onLayoutFinish.append(self.startRun)
        self.onClose.append(self.__onClose)
        
    def __onClose(self):
        if self.weatherData is not None:
            self.weatherData.cancel()
            self.weatherData = None
        
    def startRun(self):
        if self.weatherPluginEntry is not None:
            self["statustext"].text = _("Getting weather information...")
            if self.weatherData is not None:
                self.weatherData.cancel()
                self.weatherData = None
            self.weatherData = getWeather()
            self.weatherData.getWeatherData(self.weatherPluginEntry.degreetype.value,
                                            self.weatherPluginEntry.weatherlocationcode.value,
                                            self.weatherPluginEntry.city.value,
                                            self.weatherPluginEntry.weatherSearchFullName.value,
                                            self.weatherPluginEntry.thingSpeakChannelID.value,
                                            self.weatherPluginEntry.Fcity.value,
                                            self.weatherPluginEntry.airlyID.value,
                                            self.getWeatherDataCallback,
                                            None) #self.showIcon)
        else:
            self["statustext"].text = _("No locations defined...\nPress 'Menu' to do that.")

    def nextItem(self):
        if self.weatherPluginEntryCount != 0:
            if self.weatherPluginEntryIndex < self.weatherPluginEntryCount:
                self.weatherPluginEntryIndex = self.weatherPluginEntryIndex + 1
            else:
                self.weatherPluginEntryIndex = 1
            self.setItem()

    def previousItem(self):
        if self.weatherPluginEntryCount != 0:
            if self.weatherPluginEntryIndex >= 2:
                self.weatherPluginEntryIndex = self.weatherPluginEntryIndex - 1
            else:
                self.weatherPluginEntryIndex = self.weatherPluginEntryCount
            self.setItem()

    def setItem(self):
        self.weatherPluginEntry = config.plugins.WeatherPlugin.Entry[self.weatherPluginEntryIndex-1]
        config.plugins.WeatherPlugin.currEntry.value = self.weatherPluginEntryIndex-1
        self.clearFields()
        self.startRun()

    def clearFields(self):
        self["caption"].text = ""
        self["currentTemp"].text = ""
        self["condition"].text = ""
        self["wind_condition"].text = ""
        self["humidity"].text = ""
        self["observationtime"].text = ""
        self["observationpoint"].text = ""
        self["feelsliketemp"].text = ""
        self["currenticon"].hide()
        self.webSite = ""

    def showIcon(self,index, filename):
        self["currenticon"].updateIcon(filename)
        self["currenticon"].show()

    def refreshWeatherMSNComp(self, configElement = None):
        if WeatherMSNComp is not None:
            if self.weatherData is not None:
                if DBG: printDEBUG('refreshWeatherMSNComp is invoking WeatherMSNComp.updateWeather')
                WeatherMSNComp.updateWeather(self.weatherData, getWeather.OK, None) #update data source again
            else:
                if DBG: printDEBUG('MSNWeatherPlugin(Screen).refreshWeatherMSNComp self.weatherData is None =  no WeatherMSNComp update!!!')
        else:
            if DBG: printDEBUG('MSNWeatherPlugin(Screen)/refreshWeatherMSNComp WeatherMSNComp is None - nothing to update!!!')
    
    def getWeatherDataCallback(self, result, errortext):
        self["statustext"].text = ""
        if result == getWeather.ERROR:
            if DBG: printDEBUG('MSNWeatherPlugin(Screen)getWeatherDataCallback result == getWeather.ERROR')
            self.error(errortext)
        else:
            if DBG: printDEBUG('getWeatherDataCallback result == %s' % result)
            self["caption"].text = self.weatherData.city
            self.webSite = self.weatherData.url
            #current data
            item = self.weatherData.weatherItems.get('-1', None)
            if item is not None:
                self["currentTemp"].text = "%s°%s" % (item.temperature, self.weatherData.degreetype)
                self["condition"].text = item.skytext
                self["humidity"].text = _("Humidity: %s %%") % item.humidity
                self["wind_condition"].text = item.winddisplay
                c =  time.strptime(item.observationtime, "%H:%M:%S")
                self["observationtime"].text = _("Observation time: %s") %  time.strftime("%H:%M",c)
                self["observationpoint"].text = _("Observation point: %s") % item.observationpoint
                self["feelsliketemp"].text = _("Feels like %s") % item.feelslike + "°" +  self.weatherData.degreetype
                if DBG: printDEBUG('getWeatherDataCallback item.skytext == %s' % item.skytext)
                self.showIcon( -1, item.iconFilename)
        
        if WeatherMSNComp is not None:
            if DBG: printDEBUG('getWeatherDataCallback invoking WeatherMSNComp.updateWeather')
            WeatherMSNComp.updateWeather(self.weatherData, result, errortext) #update data source

    def config(self):
        self.session.openWithCallback(self.setupFinished, MSNWeatherEntriesListConfigScreen)

    def setupFinished(self, index, entry = None):
        self.weatherPluginEntryCount = config.plugins.WeatherPlugin.entrycount.value
        if self.weatherPluginEntryCount >= 1:
            if entry is not None:
                self.weatherPluginEntry = entry
                self.weatherPluginEntryIndex = index + 1
            if self.weatherPluginEntry is None:
                self.weatherPluginEntry = config.plugins.WeatherPlugin.Entry[0]
                self.weatherPluginEntryIndex = 1
        else:
            self.weatherPluginEntry = None
            self.weatherPluginEntryIndex = -1

        self.clearFields()
        self.startRun()

    def error(self, errortext):
        self.clearFields()
        self["statustext"].text = errortext

    def doNothing(self, ret = False):
        return
      
    def keyYellow(self): #ShowHistograms
        from histograms import MSNweatherHistograms
        self.session.open(MSNweatherHistograms)

    def keyBlue(self): #ShowMaps
        from maps import MSNweatherMaps
        self.session.open(MSNweatherMaps)

    def keyRed(self): #
        if config.plugins.WeatherPlugin.AC1inf.value == '':
            return
        elif config.plugins.WeatherPlugin.AC1inf.value in ('Close', 'Anuluj'):
            self.close()
        elif config.plugins.WeatherPlugin.AC1.value == 'off': #"daikin" "samsung"
            self.session.openWithCallback(self.doNothing,MessageBox, _("A/C type not set!"), MessageBox.TYPE_WARNING, timeout = 5)
        elif config.plugins.WeatherPlugin.AC1_IP.value == [0,0,0,0]:
            self.session.openWithCallback(self.doNothing,MessageBox, _("A/C IP address not set!"), MessageBox.TYPE_WARNING, timeout = 5)
        elif config.plugins.WeatherPlugin.AC1.value == 'daikin':
            from aircon_Controller_daikin import DaikinController
            self.session.openWithCallback(self.doNothing, DaikinController, config.plugins.WeatherPlugin.AC1_IP.value, config.plugins.WeatherPlugin.AC1_PORT.value, config.plugins.WeatherPlugin.AC1inf.value)
        elif config.plugins.WeatherPlugin.AC1.value == 'samsung':
            from aircon_Controller_samsung import SamsungController
            self.session.openWithCallback(self.doNothing, SamsungController, config.plugins.WeatherPlugin.AC1_IP.value, config.plugins.WeatherPlugin.AC1_PORT.value, config.plugins.WeatherPlugin.AC1inf.value)

    def keyGreen(self): #
        if config.plugins.WeatherPlugin.AC2inf.value == '':  
            return
        elif config.plugins.WeatherPlugin.AC2.value == 'off': #"daikin" "samsung"
            self.session.openWithCallback(self.doNothing,MessageBox, _("A/C type not set!"), MessageBox.TYPE_WARNING, timeout = 5)
        elif config.plugins.WeatherPlugin.AC2_IP.value == [0,0,0,0]:
            self.session.openWithCallback(self.doNothing,MessageBox, _("A/C IP address not set!"), MessageBox.TYPE_WARNING, timeout = 5)
        elif config.plugins.WeatherPlugin.AC2.value == 'daikin':
            from aircon_Controller_daikin import DaikinController
            self.session.openWithCallback(self.doNothing, DaikinController, config.plugins.WeatherPlugin.AC2_IP.value, config.plugins.WeatherPlugin.AC2_PORT.value, config.plugins.WeatherPlugin.AC2inf.value)
        elif config.plugins.WeatherPlugin.AC2.value == 'samsung':
            from aircon_Controller_samsung import SamsungController
            self.session.openWithCallback(self.doNothing, SamsungController, config.plugins.WeatherPlugin.AC2_IP.value, config.plugins.WeatherPlugin.AC2_PORT.value, config.plugins.WeatherPlugin.AC2inf.value)
