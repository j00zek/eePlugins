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
from Components.Sources.List import List
from Components.Sources.StaticText import StaticText
from debug import printDEBUG, clearLogs
from enigma import eTimer, ePicLoad
from getWeather import getWeather
from Plugins.Plugin import PluginDescriptor
#from datetime import datetime, timedelta
#from random import randint
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from setup import initConfig, MSNWeatherEntriesListConfigScreen
from Tools.Directories import resolveFilename, SCOPE_SKIN
from Tools.LoadPixmap import LoadPixmap
from version import Version
import time, os

DBG = False

config.plugins.MSNweatherNP = ConfigSubsection()
config.plugins.MSNweatherNP.FakeEntry = NoSave(ConfigNothing())

config.plugins.MSNweatherNP.airlyLimits = NoSave(ConfigText(default = "", fixed_size = False))

choicesList = [ ("skin_MSNweatherNP-vertical.xml", _("Vertically")),
                ("skin_MSNweatherNP-horizontal.xml", _("Horizontally")),
              ]
                                                                         
if os.path.exists('/usr/share/enigma2/BlackHarmony/allScreens/MSNweatherNP/'):
    for mFile in os.listdir('/usr/share/enigma2/BlackHarmony/allScreens/MSNweatherNP/'):
        if mFile.startswith('skin_MSNweatherNP-') and mFile.endswith('.xml'):
            sFile = mFile[18:-4]
            sFile = 'BlackHarmony ' + _(sFile)
            choicesList.append(( os.path.join('/usr/share/enigma2/BlackHarmony/allScreens/MSNweatherNP/', mFile), sFile ))
config.plugins.MSNweatherNP.skinOrientation = ConfigSelection(choices = choicesList, default = "skin_MSNweatherNP-vertical.xml" )

config.plugins.MSNweatherNP.SensorsPriority = ConfigSelection(choices = [ ("TsAirlyMsn", _("TsAirlyMsn")),
                                                                           ("AirlyTsMsn", _("AirlyTsMsn")),
                                                                           ("MsnAirlyTs", _("MsnAirlyTs")),
                                                                           ("MsnTsAirly", _("MsnTsAirly")),
                                                                         ],
                                                                default = "MsnTsAirly"
                                                               )

config.plugins.MSNweatherNP.BuildHistograms = ConfigEnableDisable(default = False)

if os.path.exists('/hdd/User_Configs/airlyAPIKEY'):
    config.plugins.MSNweatherNP.airlyAPIKEY = ConfigText(default = open('/hdd/User_Configs/airlyAPIKEY', 'r').readline().strip(), visible_width = 100, fixed_size = False)
elif os.path.exists('/etc/enigma2/Airly/api.txt'):
    config.plugins.MSNweatherNP.airlyAPIKEY = ConfigText(default = open('/etc/enigma2/Airly/api.txt', 'r').readline().strip(), visible_width = 100, fixed_size = False)
else:
    config.plugins.MSNweatherNP.airlyAPIKEY = ConfigText(default = "", visible_width = 100, fixed_size = False)

config.plugins.MSNweatherNP.entrycount =  ConfigInteger(0)
config.plugins.MSNweatherNP.currEntry =  NoSave(ConfigInteger(0))
config.plugins.MSNweatherNP.callbacksCount =  NoSave(ConfigInteger(0))
config.plugins.MSNweatherNP.Entry = ConfigSubList()

availableOptions = [("serviceIcons", _("MSN service icons"))]
if os.path.exists(os.path.dirname(resolveFilename(SCOPE_SKIN, config.skin.primary_skin.value)) + '/weather_icons/'):
    availableOptions.append(("weatherIcons", _("skin Icons")))
if os.path.exists('/usr/share/enigma2/animatedWeatherIcons'):
    availableOptions.append(("animIcons", _("animated Icons")))

config.plugins.MSNweatherNP.IconsType = ConfigSelection(choices = availableOptions, default = "serviceIcons")
config.plugins.MSNweatherNP.ScalePicType = ConfigSelection(choices = [ ("self.instance.setScale", _("internal E2")),
                                                                        ("ePicLoad", _("ePicLoad (E.g. Vu+ org)")) ],
                                                            default = "self.instance.setScale")

config.plugins.MSNweatherNP.AC1 = ConfigSelection(choices = [ ("off", _("not installed")), ("daikin", _("Daikin Air Conditioner")) , ("samsung", _("Samsung Air Conditioner"))], default = "off")
config.plugins.MSNweatherNP.AC1_IP = ConfigIP(default = [0,0,0,0])
config.plugins.MSNweatherNP.AC1_PORT = ConfigInteger(default = 80,limits=(80,999))
config.plugins.MSNweatherNP.AC1inf = ConfigText(default = _("AC in the living room"), visible_width = 100, fixed_size = False)
config.plugins.MSNweatherNP.AC2 = ConfigSelection(choices = [ ("off", _("not installed")), ("daikin", _("Daikin Air Conditioner")) , ("samsung", _("Samsung Air Conditioner"))], default = "off")
config.plugins.MSNweatherNP.AC2_IP = ConfigIP(default = [0,0,0,0])
config.plugins.MSNweatherNP.AC2_PORT = ConfigInteger(default = 80,limits=(80,999))
config.plugins.MSNweatherNP.AC2inf = ConfigText(default = _("AC in the bedroom"), visible_width = 100, fixed_size = False)


config.plugins.MSNweatherNP.DebugEnabled = ConfigEnableDisable(default = False)
config.plugins.MSNweatherNP.DebugSize = ConfigSelection(choices = [ ("10000", "10KB"), ("100000", "100KB"), ("1000000", "1MB"), ], default = "10000")

config.plugins.MSNweatherNP.DebugWeatherMSNupdater = ConfigEnableDisable(default = False)
config.plugins.MSNweatherNP.DebugMSNWeatherSource = ConfigEnableDisable(default = False)
config.plugins.MSNweatherNP.DebugMSNWeatherConverter = ConfigEnableDisable(default = False)

config.plugins.MSNweatherNP.DebugMSNWeatherPixmapRenderer = ConfigEnableDisable(default = False)

config.plugins.MSNweatherNP.DebugMSNWeatherThingSpeakConverter = ConfigEnableDisable(default = False)
config.plugins.MSNweatherNP.DebugMSNWeatherWebCurrentConverter = ConfigEnableDisable(default = False)
config.plugins.MSNweatherNP.DebugMSNWeatherWebhourlyConverter = ConfigEnableDisable(default = False)
config.plugins.MSNweatherNP.DebugMSNWeatherWebDailyConverter = ConfigEnableDisable(default = False)

config.plugins.MSNweatherNP.DebugGetWeatherBasic = ConfigEnableDisable(default = False)
config.plugins.MSNweatherNP.DebugGetWeatherXML = ConfigEnableDisable(default = False)
config.plugins.MSNweatherNP.DebugGetWeatherWEB = ConfigEnableDisable(default = False)
config.plugins.MSNweatherNP.DebugGetWeatherTS = ConfigEnableDisable(default = False)
config.plugins.MSNweatherNP.DebugGetWeatherFULL = ConfigEnableDisable(default = False)
config.plugins.MSNweatherNP.DebugMSNweatherHistograms = ConfigEnableDisable(default = False)
config.plugins.MSNweatherNP.DebugMSNweatherMaps = ConfigEnableDisable(default = True)

config.plugins.MSNweatherNP.HistoryPeriod = ConfigSelection(choices = [ ("86400", _("Last 24h")), ("43200", _("Last 12h")), ("21600", _("Last 6h")), ("10800", _("Last 3h")), ("3600", _("Last hour")), ], default = "43200")

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
    clearLogs()
    printDEBUG('INIT', ' MSNweather NP plugin %s' % Version)
    printDEBUG('config.plugins.MSNweatherNP.IconsType = "%s"' % config.plugins.MSNweatherNP.IconsType.value)
    session.open(MSNweatherNP)

def sessionstart(session, **kwargs):
    session.screen["MSNweatherNP"] = getWeather()

def Plugins(**kwargs):
    list = [
        PluginDescriptor(name=_("MSN weather NP"), where = [PluginDescriptor.WHERE_PLUGINMENU, PluginDescriptor.WHERE_EXTENSIONSMENU], icon = "weather.png", fnc=main),
        PluginDescriptor(where = [PluginDescriptor.WHERE_SESSIONSTART], fnc = sessionstart)
    ]
    return list

class MSNweatherNP(Screen):
    def __init__(self, session):
        if config.plugins.MSNweatherNP.skinOrientation.value.startswith('/') and os.path.exists(config.plugins.MSNweatherNP.skinOrientation.value):
            self.skin = open(config.plugins.MSNweatherNP.skinOrientation.value,'r').read()
        elif os.path.exists("/usr/lib/enigma2/python/Plugins/Extensions/MSNweather/skins/%s" % config.plugins.MSNweatherNP.skinOrientation.value):
            self.skin = open("/usr/lib/enigma2/python/Plugins/Extensions/MSNweather/skins/%s" % config.plugins.MSNweatherNP.skinOrientation.value,'r').read()
        else:
            self.skin = open("/usr/lib/enigma2/python/Plugins/Extensions/MSNweather/skins/skin_MSNweatherNP-vertical.xml",'r').read()
            
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
            "current_up": self.current_up,
            "current_down": self.current_down,
            "hourly_up": self.hourly_up,
            "hourly_down": self.hourly_down,
            "daily_up": self.daily_up,
            "daily_down": self.daily_down,
            "keyOk": self.openDailyDetails,
        }, -1)

        self["statustext"] = StaticText()
        self["currenticon"] = j00zekAccellPixmap()
        self["caption"] = StaticText()
        self["currentData_weathericon"] = StaticText()
        self["currentData_temperature"] = StaticText()
        self["currentData_skytext"] = StaticText()
        self["currentData_observationtime"] = StaticText()
        self["currentData_AllObservationTimes"] = StaticText()
        self["observationpoint"] = StaticText()
        self["currentData_airlyInfo"] = StaticText()
        self["currentData_airlyAdvice"] = StaticText()

        self["currentData_infoList"] = List([])
        #self["currentData_infoList"].list = []

        self["currentData_WeatherinfoList"] = List([])
        #self["currentData_WeatherinfoList"].list = []

        self["currentData_allInfoList"] = List([])

        self["dailyData_infoList"] = List([])
        #self["dailyData_infoList"].list = []

        self["hourlyData_infoList"] = List([])
        #self["hourlyData_infoList"].list = []

        self["key_red"] = Label(config.plugins.MSNweatherNP.AC1inf.value)
        self["key_green"] = Label(config.plugins.MSNweatherNP.AC2inf.value)
        self["key_yellow"] = Label(_("Show Histograms"))
        self["key_blue"] = Label(_("Show Maps"))

        self.weatherPluginEntryIndex = -1
        self.weatherPluginEntry = None
        try:
            config.plugins.MSNweatherNP.currEntry.value = 0
            self.weatherPluginEntryCount = config.plugins.MSNweatherNP.entrycount.value
            if self.weatherPluginEntryCount >= 1:
                self.weatherPluginEntry = config.plugins.MSNweatherNP.Entry[0]
                self.weatherPluginEntryIndex = 1
        except Exception as e:
            printDEBUG('MSNweather.__init__', ' Exception %s' % str(e))


        self.webSite = ""
        
        self.weatherData = None

        self.picload = ePicLoad()

        self.onClose.append(self.__onClose)
        #self.onLayoutFinish.append(self.__onLayoutFinish)
        self.onShown.append(self.__onShown)
        
    def __onClose(self):
        if self.weatherData is not None:
            self.weatherData.cancel()
            self.weatherData = None
    
    def __onShown(self):
        self.startDelay = eTimer()
        self.startDelay.callback.append(self.startRun)
        self.startDelay.start(50, True)
            
    def current_up(self):
        try: self["currentData_infoList"].pageUp()
        except Exception: pass
    
    def current_down(self):
        try: self["currentData_infoList"].pageDown()
        except Exception: pass
    
    def hourly_up(self):
        try: self["hourlyData_infoList"].pageUp()
        except Exception: pass
    
    def hourly_down(self):
        try: self["hourlyData_infoList"].pageDown()
        except Exception: pass
    
    def daily_up(self):
        try: self["dailyData_infoList"].pageUp()
        except Exception: pass
    
    def daily_down(self):
        try: self["dailyData_infoList"].pageDown()
        except Exception: pass

    def startRun(self):
        self.startDelay.stop()
        if self.weatherPluginEntry is not None:
            self["statustext"].text = _("Getting weather information...")
            if self.weatherData is not None:
                self.weatherData.cancel()
                self.weatherData = None
            self.weatherData = getWeather()
            self.weatherData.getWeatherData(self.weatherPluginEntry, self.getWeatherDataCallback, None) #self.showIcon)
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
        self.weatherPluginEntry = config.plugins.MSNweatherNP.Entry[self.weatherPluginEntryIndex-1]
        config.plugins.MSNweatherNP.currEntry.value = self.weatherPluginEntryIndex-1
        self.clearFields()
        self.startRun()

    def clearFields(self):
        self["caption"].text = ""
        self["currentData_temperature"].text = ""
        self["currentData_skytext"].text = ""
        self["currentData_observationtime"].text = ""
        self["currentData_AllObservationTimes"].text = ""
        self["observationpoint"].text = ""
        self["currenticon"].hide()
        self.webSite = ""
        self["currentData_allInfoList"].list = []
        self["currentData_infoList"].list = []
        self["dailyData_infoList"].list = []
        self["hourlyData_infoList"].list = []
        self["currentData_airlyInfo"].text = ""
        self["currentData_WeatherinfoList"].list = []
        self["currentData_airlyInfo"].text = ""
        self["currentData_airlyAdvice"].text = ""

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

    def config(self):
        self.session.openWithCallback(self.setupFinished, MSNWeatherEntriesListConfigScreen)

    def setupFinished(self, index, entry = None):
        self.weatherPluginEntryCount = config.plugins.MSNweatherNP.entrycount.value
        if self.weatherPluginEntryCount >= 1:
            if entry is not None:
                self.weatherPluginEntry = entry
                self.weatherPluginEntryIndex = index + 1
            if self.weatherPluginEntry is None:
                self.weatherPluginEntry = config.plugins.MSNweatherNP.Entry[0]
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
        self.session.open(MSNweatherMaps, self.weatherPluginEntry.Fcity.value,)

    def keyRed(self): #
        if config.plugins.MSNweatherNP.AC1inf.value == '':
            return
        elif config.plugins.MSNweatherNP.AC1inf.value in ('Close', 'Anuluj'):
            self.close()
        elif config.plugins.MSNweatherNP.AC1.value == 'off': #"daikin" "samsung"
            self.session.openWithCallback(self.doNothing,MessageBox, _("A/C type not set!"), MessageBox.TYPE_WARNING, timeout = 5)
        elif config.plugins.MSNweatherNP.AC1_IP.value == [0,0,0,0]:
            self.session.openWithCallback(self.doNothing,MessageBox, _("A/C IP address not set!"), MessageBox.TYPE_WARNING, timeout = 5)
        elif config.plugins.MSNweatherNP.AC1.value == 'daikin':
            from aircon_Controller_daikin import DaikinController
            self.session.openWithCallback(self.doNothing, DaikinController, config.plugins.MSNweatherNP.AC1_IP.value, config.plugins.MSNweatherNP.AC1_PORT.value, config.plugins.MSNweatherNP.AC1inf.value)
        elif config.plugins.MSNweatherNP.AC1.value == 'samsung':
            from aircon_Controller_samsung import SamsungController
            self.session.openWithCallback(self.doNothing, SamsungController, config.plugins.MSNweatherNP.AC1_IP.value, config.plugins.MSNweatherNP.AC1_PORT.value, config.plugins.MSNweatherNP.AC1inf.value)

    def keyGreen(self): #
        if config.plugins.MSNweatherNP.AC2inf.value == '':  
            return
        elif config.plugins.MSNweatherNP.AC2.value == 'off': #"daikin" "samsung"
            self.session.openWithCallback(self.doNothing,MessageBox, _("A/C type not set!"), MessageBox.TYPE_WARNING, timeout = 5)
        elif config.plugins.MSNweatherNP.AC2_IP.value == [0,0,0,0]:
            self.session.openWithCallback(self.doNothing,MessageBox, _("A/C IP address not set!"), MessageBox.TYPE_WARNING, timeout = 5)
        elif config.plugins.MSNweatherNP.AC2.value == 'daikin':
            from aircon_Controller_daikin import DaikinController
            self.session.openWithCallback(self.doNothing, DaikinController, config.plugins.MSNweatherNP.AC2_IP.value, config.plugins.MSNweatherNP.AC2_PORT.value, config.plugins.MSNweatherNP.AC2inf.value)
        elif config.plugins.MSNweatherNP.AC2.value == 'samsung':
            from aircon_Controller_samsung import SamsungController
            self.session.openWithCallback(self.doNothing, SamsungController, config.plugins.MSNweatherNP.AC2_IP.value, config.plugins.MSNweatherNP.AC2_PORT.value, config.plugins.MSNweatherNP.AC2inf.value)

    def openDailyDetails(self):
        if self.weatherData is not None:
            if self.weatherData.weatherItems.get('-1', None) is not None:
                import dailyDetails
                reload(dailyDetails)             
                self.session.open(dailyDetails.MSNweatherDailyDetails, self.weatherData.weatherItems.get('-1', None))
            
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
                self["currentData_temperature"].text = str(item.dictWeather.get('currentData', {}).get('temperature', {}).get('valInfo', '')) #"%s°%s" % (item.temperature, self.weatherData.degreetype)
                self["currentData_skytext"].text = item.skytext
                    
                try:
                    c =  time.strptime(item.observationtime, "%H:%M:%S")
                    self["currentData_observationtime"].text = _("Actualization time: %s") %  time.strftime("%H:%M",c)
                except Exception:
                    self["currentData_observationtime"].text = item.observationtime
                self["observationpoint"].text = _("Observation point: %s") % item.observationpoint
                if DBG: printDEBUG('getWeatherDataCallback item.skytext == %s' % item.skytext)
                self.showIcon( -1, item.iconFilename)
                
                #self["currentData_weathericon"] = item.iconFilename
                
                tmpDict = item.dictWeather.get('currentData', {})
                
                #populate currentData_infoList
                tmpList = []
                tmpAllList = []
                tmpListWeather = []
                if len(tmpDict) > 0:
                    #info o aktualuzaci
                    tmpVal = str(tmpDict.get('observationtime', {}).get('name', ""))
                    tmpVal += ' ' + str(tmpDict.get('observationtime', {}).get('time', ""))
                    if str(tmpDict.get('tsobservationtime', {}).get('time', "")) != '':
                        tmpVal += ', TS %s' % str(tmpDict.get('tsobservationtime', {}).get('time', ""))
                    if str(tmpDict.get('airlyobservationtime', {}).get('time', "")) != '':
                        tmpVal += ', Airly %s' % str(tmpDict.get('airlyobservationtime', {}).get('time', ""))
                    self["currentData_AllObservationTimes"].text = tmpVal
                    
                    self["currentData_airlyInfo"].text = str(tmpDict.get('airlyIndex', {}).get('info', ""))
                    alert = str(tmpDict.get('alert', {}).get('valInfo', ''))
                    if alert == '':
                        self["currentData_airlyAdvice"].text = str(tmpDict.get('airlyIndex', {}).get('advice', ""))
                    else:
                        self["currentData_airlyAdvice"].text = alert
                    for key in tmpDict:
                        valDict = tmpDict[key]
                        if isinstance(valDict,dict):
                            inList = valDict.get('inList', False)
                            if inList:
                                tmpAllList.append((str(valDict['name']),str(valDict['valInfo'])))
                                if key in ('dew_point_temp','feelslike','humidity','pressure','visibility','wind_speed'):
                                    tmpListWeather.append((str(valDict['name']),str(valDict['valInfo'])))
                                else:
                                    try:
                                        tmpList.append((str(valDict['name']),str(valDict['valInfo'])))
                                    except Exception:
                                        pass
                    try: tmpList.sort(key=lambda t : tuple(str(t[0]).lower()))
                    except Exception: tmpList.sort()
                    try: tmpListWeather.sort(key=lambda t : tuple(str(t[0]).lower()))
                    except Exception: tmpListWeather.sort()
                    try: tmpAllList.sort(key=lambda t : tuple(str(t[0]).lower()))
                    except Exception: tmpAllList.sort()
                    
                self["currentData_infoList"].list = tmpList
                self["currentData_WeatherinfoList"].list = tmpListWeather
                self["currentData_allInfoList"].list = tmpAllList
                
                if 1: #populate hourlyData_infoList
                    self["hourlyData_infoList"].list = []
                    tmpDict = item.dictWeather['hourlyData']
                    tmpList = []
                    if len(tmpDict) > 0:
                        index = 0
                        if DBG: printDEBUG('populate hourlyData_infoList')
                        pngH = LoadPixmap(cached=True, path='/usr/lib/enigma2/python/Plugins/Extensions/MSNweather/icons/humidity_icon.png')
                        pngT = LoadPixmap(cached=True, path='/usr/lib/enigma2/python/Plugins/Extensions/MSNweather/icons/temperature_icon.png')
                        while index < len(tmpDict.keys()):
                            try:
                                record = tmpDict['Record=%s' % index]
                                index += 1
                            except Exception as e:
                                break
                            iconfilename = str(record['imgfilename'])
                            if DBG: printDEBUG('record = %s\n' % str(record))
                            if iconfilename.endswith('.png'):
                                png = LoadPixmap(cached=True, path=iconfilename)
                                tmpList.append(( png, '%s:00' % str(record['time']) ,
                                                                str(record['temperature']), 
                                                                str(record['rainprecip']),
                                                                str(record['skytext']),
                                                                pngT, pngH ))
                    self["hourlyData_infoList"].list = tmpList
                
                #populate dailyData_infoList
                self["dailyData_infoList"].list = []
                tmpDict = item.dictWeather['dailyData']
                tmpList = []
                index = 0
                if len(tmpDict) > 0:
                    if DBG: printDEBUG('populate dailyData_infoList')
                    while index < len(tmpDict.keys()):
                        png = None
                        iconfilename = ''
                        try:
                            record = tmpDict['Record=%s' % index]
                            index += 1
                        except Exception as e:
                            if DBG: printDEBUG('record=%s exception: %s\n' % (index,str(e)))
                            break
                        if config.plugins.MSNweatherNP.IconsType.value == "serviceIcons":
                            iconsList = (str(record['imgfilename']),str(record['iconfilename']))
                        else:
                            iconsList = (str(record['iconfilename']),str(record['imgfilename']))
                        for tmpIcon in iconsList:
                            if tmpIcon.endswith('.png') and os.path.exists(tmpIcon):
                                iconfilename = tmpIcon
                                png = LoadPixmap(cached=True, path=iconfilename)
                                break
                        #if DBG: printDEBUG('record = %s\n' % str(record))
                        tmpList.append(( png, '%s, %s' % (str(record['weekday']), str(record['monthday'])) ,
                                                                str(record['temp_high']), 
                                                                str(record['temp_low']),
                                                                str(record['rainprecip']),
                                                                str(record['forecast'])
                                        ))
                self["dailyData_infoList"].list = tmpList

                
        if WeatherMSNComp is not None:
            if DBG: printDEBUG('getWeatherDataCallback invoking WeatherMSNComp.updateWeather')
            WeatherMSNComp.updateWeather(self.weatherData, result, errortext) #update data source
