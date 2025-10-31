# -*- coding: utf-8 -*-
#PY3 ONLY !!!
from . import _ , readCFG
from Plugins.Extensions.MSNweather.debug import printDEBUG
from Plugins.Extensions.MSNweather.version import Version
from Plugins.Extensions.MSNweather.getWeather import getWeather
from Plugins.Extensions.MSNweather.setupNP import initConfig, MSNWeatherEntriesListConfigScreen

from Components.ActionMap import ActionMap
from Components.config import ConfigSubsection, ConfigSubList, ConfigInteger, config, NoSave, ConfigEnableDisable, ConfigSelection, ConfigText, ConfigIP, ConfigYesNo, ConfigNothing, ConfigPassword
from Components.j00zekAccellPixmap import j00zekAccellPixmap
from Components.Renderer.j00zekMSNWeatherPixmap import j00zekMSNWeatherPixmap
from Components.Label import Label
from Components.Sources.List import List
from Components.Sources.StaticText import StaticText
from enigma import eTimer, ePicLoad, addFont
from Plugins.Plugin import PluginDescriptor
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Tools.Directories import resolveFilename, SCOPE_SKIN
from Tools.LoadPixmap import LoadPixmap
import time, os

from importlib import reload

DBG = True

WeatherMSNComp = None

class MSNweatherNP(Screen):
    def __init__(self, session):
        self.DEBUG('INIT', '>>>')
        addFont("/usr/lib/enigma2/python/Plugins/Extensions/MSNweather/skins/regular.ttf", "regularMSN", 110, False)
        addFont("/usr/lib/enigma2/python/Plugins/Extensions/MSNweather/skins/roboto.ttf", "robotoMSN", 100, False)
        if config.plugins.MSNweatherNP.skinOrientation.value.startswith('/') and os.path.exists(config.plugins.MSNweatherNP.skinOrientation.value):
            self.skin = open(config.plugins.MSNweatherNP.skinOrientation.value, 'r').read()
        else:
            if os.path.exists('/usr/lib/enigma2/python/Plugins/Extensions/MSNweather/skins/%s' % config.plugins.MSNweatherNP.skinOrientation.value):
                self.skin = open('/usr/lib/enigma2/python/Plugins/Extensions/MSNweather/skins/%s' % config.plugins.MSNweatherNP.skinOrientation.value, 'r').read()
            else:
                self.skin = open('/usr/lib/enigma2/python/Plugins/Extensions/MSNweather/skins/skin_MSNweatherNP-TV_bg.xml', 'r').read()
        Screen.__init__(self, session)
        self.DEBUG('INIT', '>>>')
        self.title = _('MSN weather NP @j00zek %s' % Version)
        self.setTitle(_('MSN weather NP @j00zek %s') % Version)
        self['actions'] = ActionMap(['MSNweatherNP'], {'keyCancel': self.close, 
               'keyMenu': self.config, 
               'keyRight': self.nextItem, 
               'keyLeft': self.previousItem, 
               'keyRed': self.keyRed, 
               'keyGreen': self.keyGreen, 
               'keyYellow': self.keyYellow, 
               'keyBlue': self.keyBlue, 
               'current_up': self.current_up, 
               'current_down': self.current_down, 
               'hourly_up': self.hourly_up, 
               'hourly_down': self.hourly_down, 
               'daily_up': self.daily_up, 
               'daily_down': self.daily_down, 
               'keyOk': self.openDailyDetails,
               'keyOkLong': self.openMonthlyForecast
               }, -1)

        self.StaticTextSources = [('currentData_WeatherPixmap', '["currentData"]["iconfilename"]["val"]'),
                                  ('currentData_temperature', '["currentData"]["temperature"]["valInfo"]'), 
                                  ('currentData_skytext', '["currentData"]["skytext"]["valInfo"]'),
                                  ('currentData_observationtime', ''), # '' = calculated in code
                                  ('currentData_AllObservationTimes', '["currentData"]["activeSources"]["observationtimesInfo"]'),
                                  ('observationpoint', ''),
                                  ('currentData_airQualityAccellPixmap', '["currentData"]["airIndex"]["iconfilename"]'),
                                  ('currentData_airIndexInfo', '["currentData"]["airIndex"]["info"]'),
                                  ('currentData_airIndexAdvice', '["currentData"]["airIndex"]["advice"]'),
                                  ('caption', 'self.weatherData.city'),
                                  ('airQualityTitle', ''),
                                  ('statustext', ''),
                                  ('sunrise_time', '["currentData"]["sun"]["sunrise"]["TZtime"]'),
                                  ('sunset_time' , '["currentData"]["sun"]["sunset"]["TZtime"]'),
                                  ('moon_iluminatedPerc', '["currentData"]["moon"]["illuminated_percentage"]'),
                                  #hourly sources
                                  ('hourlyData_title'               , "['hourlyData']['title']"),
                                  ('hourlyRecord_0_Summary'         , "['hourlyData']['Record=0']['summary']"),
                                  ('hourlyRecord_0_WeatherPixmap'   , "['hourlyData']['Record=0']['fromConfig']"),
                                  ('hourlyRecord_1_Summary'         , "['hourlyData']['Record=1']['summary']"),
                                  ('hourlyRecord_1_WeatherPixmap'   , "['hourlyData']['Record=1']['fromConfig']"),
                                  ('hourlyRecord_2_Summary'         , "['hourlyData']['Record=2']['summary']"),
                                  ('hourlyRecord_2_WeatherPixmap'   , "['hourlyData']['Record=2']['fromConfig']"),
                                  ('hourlyRecord_3_Summary'         , "['hourlyData']['Record=3']['summary']"),
                                  ('hourlyRecord_3_WeatherPixmap'   , "['hourlyData']['Record=3']['fromConfig']"),
                                  ('hourlyRecord_4_Summary'         , "['hourlyData']['Record=4']['summary']"),
                                  ('hourlyRecord_4_WeatherPixmap'   , "['hourlyData']['Record=4']['fromConfig']"),
                                  ('hourlyRecord_5_Summary'         , "['hourlyData']['Record=5']['summary']"),
                                  ('hourlyRecord_5_WeatherPixmap'   , "['hourlyData']['Record=5']['fromConfig']"),
                                  ('hourlyRecord_6_Summary'         , "['hourlyData']['Record=6']['summary']"),
                                  ('hourlyRecord_6_WeatherPixmap'   , "['hourlyData']['Record=6']['fromConfig']"),
                                  ('hourlyRecord_7_Summary'         , "['hourlyData']['Record=7']['summary']"),
                                  ('hourlyRecord_7_WeatherPixmap'   , "['hourlyData']['Record=7']['fromConfig']"),
                                  ('hourlyRecord_8_Summary'         , "['hourlyData']['Record=8']['summary']"),
                                  ('hourlyRecord_8_WeatherPixmap'   , "['hourlyData']['Record=8']['fromConfig']"),
                                  ('hourlyRecord_9_Summary'         , "['hourlyData']['Record=9']['summary']"),
                                  ('hourlyRecord_9_WeatherPixmap'   , "['hourlyData']['Record=9']['fromConfig']"),
                                  ('hourlyRecord_10_Summary'        , "['hourlyData']['Record=10']['summary']"),
                                  ('hourlyRecord_10_WeatherPixmap'  , "['hourlyData']['Record=10']['fromConfig']"),
                                  #daily sources
                                  ('daily_0_date_summary'     , "['dailyData']['Record=0']['date_summary']"),
                                  ('daily_0_WeatherPixmap'    , "['dailyData']['Record=0']['fromConfig']"),
                                  ('daily_0_summary'          , "['dailyData']['Record=0']['summary']"),
                                  ('daily_1_date_summary'     , "['dailyData']['Record=1']['date_summary']"),
                                  ('daily_1_WeatherPixmap'    , "['dailyData']['Record=1']['fromConfig']"),
                                  ('daily_1_summary'          , "['dailyData']['Record=1']['summary']"),
                                  ('daily_2_date_summary'     , "['dailyData']['Record=2']['date_summary']"),
                                  ('daily_2_WeatherPixmap'    , "['dailyData']['Record=2']['fromConfig']"),
                                  ('daily_2_summary'          , "['dailyData']['Record=2']['summary']"),
                                  ('daily_3_date_summary'     , "['dailyData']['Record=3']['date_summary']"),
                                  ('daily_3_WeatherPixmap'    , "['dailyData']['Record=3']['fromConfig']"),
                                  ('daily_3_summary'          , "['dailyData']['Record=3']['summary']"),
                                  ('daily_4_date_summary'     , "['dailyData']['Record=4']['date_summary']"),
                                  ('daily_4_WeatherPixmap'    , "['dailyData']['Record=4']['fromConfig']"),
                                  ('daily_4_summary'          , "['dailyData']['Record=4']['summary']"),
                                  ('daily_5_date_summary'     , "['dailyData']['Record=5']['date_summary']"),
                                  ('daily_5_WeatherPixmap'    , "['dailyData']['Record=5']['fromConfig']"),
                                  ('daily_5_summary'          , "['dailyData']['Record=5']['summary']"),
                                  ('daily_6_date_summary'     , "['dailyData']['Record=6']['date_summary']"),
                                  ('daily_6_WeatherPixmap'    , "['dailyData']['Record=6']['fromConfig']"),
                                  ('daily_6_summary'          , "['dailyData']['Record=6']['summary']"),
                                  ('daily_7_date_summary'     , "['dailyData']['Record=7']['date_summary']"),
                                  ('daily_7_WeatherPixmap'    , "['dailyData']['Record=7']['fromConfig']"),
                                  ('daily_7_summary'          , "['dailyData']['Record=7']['summary']"),
                                  ('daily_8_date_summary'     , "['dailyData']['Record=8']['date_summary']"),
                                  ('daily_8_WeatherPixmap'    , "['dailyData']['Record=8']['fromConfig']"),
                                  ('daily_8_summary'          , "['dailyData']['Record=8']['summary']"),
                                 ]
        for currItem in self.StaticTextSources:
            self[currItem[0]] = StaticText()
        

        self.Lists = ['currentData_infoList', 'currentData_WeatherinfoList', 'currentData_allInfoList', 'dailyData_infoList', 'hourlyData_infoList']
        for currItem in self.Lists:
            self[currItem] = List([])

        if config.plugins.MSNweatherNP.AC1.value == 'off':
            self['key_red'] = Label(_('Monthly forecast'))
        else:
            self['key_red'] = Label(config.plugins.MSNweatherNP.AC1inf.value)
        self['key_green'] = Label(config.plugins.MSNweatherNP.AC2inf.value)
        self['key_yellow'] = Label(_('Show Histograms'))
        self['key_blue'] = Label(_('Show Maps'))
        self.weatherPluginEntryIndex = -1
        self.weatherPluginEntry = None
        try:
            config.plugins.MSNweatherNP.currEntry.value = 0
            self.weatherPluginEntryCount = config.plugins.MSNweatherNP.entrycount.value
            if self.weatherPluginEntryCount >= 1:
                self.weatherPluginEntry = config.plugins.MSNweatherNP.Entry[0]
                self.weatherPluginEntryIndex = 1
        except Exception as e:
            self.DEBUG('MSNweather.__init__', ' Exception %s' % str(e))

        self.webSite = ''
        self.weatherData = None
        self.picload = ePicLoad()
        self.onClose.append(self.__onClose)
        self.onShown.append(self.__onShown)
        return

    def DEBUG(self, myFUNC='', myText=''):
        if DBG:
            printDEBUG(myFUNC, myText, logFileName='MSNweatherNP.log', devDBG = True)
        elif config.plugins.MSNweatherNP.DebugEnabled.value == True or 'EXCEPTION' in myFUNC or 'EXCEPTION' in myText:
            printDEBUG(myFUNC, myText, logFileName='MSNweatherNP.log')

    def __onClose(self):
        if self.weatherData is not None:
            self.weatherData.cancel()
            self.weatherData = None
        if config.plugins.MSNweatherNP.DebugEnabled.value:
            os.system('tar -czf /tmp/MSNdata_logs.tar.gz /tmp/.MSNdata/*')
        return

    def __onShown(self):
        self.startDelay = eTimer()
        self.startDelay.callback.append(self.startRun)
        self.startDelay.start(50, True)

    def current_up(self):
        try:
            self['currentData_infoList'].pageUp()
        except Exception:
            pass

    def current_down(self):
        try:
            self['currentData_infoList'].pageDown()
        except Exception:
            pass

    def hourly_up(self):
        try:
            self['hourlyData_infoList'].pageUp()
        except Exception:
            pass

    def hourly_down(self):
        try:
            self['hourlyData_infoList'].pageDown()
        except Exception:
            pass

    def daily_up(self):
        try:
            self['dailyData_infoList'].pageUp()
        except Exception:
            pass

    def daily_down(self):
        try:
            self['dailyData_infoList'].pageDown()
        except Exception:
            pass

    def startRun(self):
        self.startDelay.stop()
        if self.weatherPluginEntry is not None:
            self['statustext'].text = _('Getting weather information...')
            if self.weatherData is not None:
                self.weatherData.cancel()
                self.weatherData = None
            self.weatherData = getWeather()
            self.weatherData.getWeatherData(self.weatherPluginEntry, self.getWeatherDataCallback, None)
        else:
            self['statustext'].text = _("No locations defined...\nPress 'Menu' to do that.")
        return

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
        self.weatherPluginEntry = config.plugins.MSNweatherNP.Entry[(self.weatherPluginEntryIndex - 1)]
        config.plugins.MSNweatherNP.currEntry.value = self.weatherPluginEntryIndex - 1
        self.clearFields()
        self.startRun()

    def setFields(self, item):
        self.DEBUG('\tsetFields()', ' >>>')
        item.dictWeather
        for currItem in self.StaticTextSources:
            try:
                valPath = currItem[1]
                if 'Pixmap' in currItem[0]:
                    filename = None
                    iconsList = None
                    iconfilename = None
                    imgfilename = None
                    valPath = currItem[1].replace('"',"'")
                    if valPath.startswith('['):
                        #self.DEBUG("\t\t","valPath=%s" % valPath)
                        if valPath.endswith("['fromConfig']"):
                            iconfilename = eval('str(item.dictWeather%s)' % valPath.replace('fromConfig',"iconfilename"))
                            imgfilename = eval('str(item.dictWeather%s)' % valPath.replace('fromConfig',"imgfilename"))
                        else:
                            filename = eval('str(item.dictWeather%s)' % valPath)
                            #self.DEBUG("\t\t","filename=%s" % filename)
                    elif valPath == 'item.iconFilename':
                        filename = item.iconFilename
                        #self.DEBUG("\t\t","filename=item.iconFilename=%s" % filename)

                    if filename is None: #przydzielenie poprawnej ikony w zaleznosci od konfiguracji
                        if 'hourly' in currItem[0].lower() and config.plugins.MSNweatherNP.hIconsType.value == 'serviceIcons':
                            iconsList = (imgfilename, iconfilename)
                        elif config.plugins.MSNweatherNP.IconsType.value == 'serviceIcons':
                            iconsList = (imgfilename, iconfilename)
                        else:
                            iconsList = (iconfilename, imgfilename)
                
                        self.DEBUG('\t\t', '%s.iconsList: %s ' % (currItem[0],str(iconsList)))
                    
                        for tmpIcon in iconsList:
                            if not tmpIcon is None and tmpIcon.endswith('.png') and os.path.exists(tmpIcon):
                                filename = tmpIcon
                                break
                    
                    if filename is None:
                        self[currItem[0]].text = ''
                        self.DEBUG("\t\t","%s.filename='None'" % currItem[0])
                    elif os.path.exists(filename): 
                        self[currItem[0]].text = filename
                        self.DEBUG("\t\t","%s.filename='%s' found and exists" % (currItem[0],str(filename)))
                    else:
                        self[currItem[0]].text = ''
                        self.DEBUG("\t\t","%s.filename='%s' found but does NOT exist" % (currItem[0],str(filename)))
                else:
                    retVal = ''
                    if valPath.startswith('['):
                        retVal = str(eval('item.dictWeather%s' % valPath))
                    elif valPath.startswith('self.'):
                        retVal = str(eval(valPath))
                    self[currItem[0]].text = retVal
                    self.DEBUG("\t\t","%s.text='%s'" % (currItem[0],str(filename)))
            except Exception as e:
                #self[currItem[0]].text = ''
                self.DEBUG("setFields:StaticTextSources(%s) EXCEPTION: %s" % (str(currItem),str(e)))

    def clearFields(self):
        for currItem in self.StaticTextSources:
            self[currItem[0]].text = ''
            self.DEBUG("clearFields:StaticTextSources(%s)" % str(currItem[0]))

        for currItem in self.Lists:
            self[currItem].list = []

        self.webSite = ''

    def refreshWeatherMSNComp(self, configElement=None):
        if WeatherMSNComp is not None:
            if self.weatherData is not None:
                self.DEBUG('refreshWeatherMSNComp is invoking WeatherMSNComp.updateWeather')
                WeatherMSNComp.updateWeather(self.weatherData, getWeather.OK, None)
            else:
                self.DEBUG('MSNWeatherPlugin(Screen).refreshWeatherMSNComp self.weatherData is None =  no WeatherMSNComp update!!!')
        else:
            self.DEBUG('MSNWeatherPlugin(Screen)/refreshWeatherMSNComp WeatherMSNComp is None - nothing to update!!!')
        return

    def config(self):
        self.session.openWithCallback(self.setupFinished, MSNWeatherEntriesListConfigScreen)

    def setupFinished(self, index, entry=None):
        self.DEBUG('setupFinished(index = %s, entry = %s) >>>' % (str(index), str(entry)))
        self.weatherPluginEntryCount = config.plugins.MSNweatherNP.entrycount.value
        if entry is None:
            if self.weatherPluginEntryCount < 1:
                self.weatherPluginEntry = None
                self.weatherPluginEntryIndex = -1
            else:
                config.plugins.MSNweatherNP.currEntry.value = 0
                self.weatherPluginEntry = config.plugins.MSNweatherNP.Entry[0]
                self.weatherPluginEntryIndex = 1
        else:
            self.weatherPluginEntryIndex = index + 1
            config.plugins.MSNweatherNP.currEntry.value = index
            self.weatherPluginEntry = config.plugins.MSNweatherNP.Entry[index]
        self.clearFields()
        self.startDelay.start(50, True)
        return

    def error(self, errortext):
        self.clearFields()
        self['statustext'].text = errortext

    def doNothing(self, ret=False):
        pass

    def keyYellow(self):
        import Plugins.Extensions.MSNweather.histograms
        reload(Plugins.Extensions.MSNweather.histograms)
        self.session.open(Plugins.Extensions.MSNweather.histograms.MSNweatherHistograms)

    def keyBlue(self):
        import Plugins.Extensions.MSNweather.mapsNP
        reload(Plugins.Extensions.MSNweather.mapsNP)
        try:
            fc = self.weatherPluginEntry.Fcity.value
        except Exception:
            fc = _('Unknown')

        self.session.open(Plugins.Extensions.MSNweather.mapsNP.MSNweatherMaps, fc)

    def keyRed(self):
        if config.plugins.MSNweatherNP.AC1inf.value == '':
            self.openMonthlyForecast()
            return
        if config.plugins.MSNweatherNP.AC1inf.value in ('Close', 'Anuluj'):
            self.close()
        elif config.plugins.MSNweatherNP.AC1.value == 'off':
            self.openMonthlyForecast()
            #self.session.openWithCallback(self.doNothing, MessageBox, _('A/C type not set!'), MessageBox.TYPE_WARNING, timeout=5)
        elif config.plugins.MSNweatherNP.AC1_IP.value == [0, 0, 0, 0]:
            self.session.openWithCallback(self.doNothing, MessageBox, _('A/C IP address not set!'), MessageBox.TYPE_WARNING, timeout=5)
        elif config.plugins.MSNweatherNP.AC1.value == 'daikin':
            from Plugins.Extensions.MSNweather.aircon_Controller_daikin import DaikinController
            self.session.openWithCallback(self.doNothing, DaikinController, config.plugins.MSNweatherNP.AC1_IP.value, config.plugins.MSNweatherNP.AC1_PORT.value, config.plugins.MSNweatherNP.AC1inf.value)
        elif config.plugins.MSNweatherNP.AC1.value == 'samsung':
            from Plugins.Extensions.MSNweather.aircon_Controller_samsung import SamsungController
            self.session.openWithCallback(self.doNothing, SamsungController, config.plugins.MSNweatherNP.AC1_IP.value, config.plugins.MSNweatherNP.AC1_PORT.value, config.plugins.MSNweatherNP.AC1inf.value)

    def keyGreen(self):
        if config.plugins.MSNweatherNP.AC2inf.value == '':
            return
        if config.plugins.MSNweatherNP.AC2.value == 'off':
            self.session.openWithCallback(self.doNothing, MessageBox, _('A/C type not set!'), MessageBox.TYPE_WARNING, timeout=5)
        elif config.plugins.MSNweatherNP.AC2_IP.value == [0, 0, 0, 0]:
            self.session.openWithCallback(self.doNothing, MessageBox, _('A/C IP address not set!'), MessageBox.TYPE_WARNING, timeout=5)
        elif config.plugins.MSNweatherNP.AC2.value == 'daikin':
            from Plugins.Extensions.MSNweather.aircon_Controller_daikin import DaikinController
            self.session.openWithCallback(self.doNothing, DaikinController, config.plugins.MSNweatherNP.AC2_IP.value, config.plugins.MSNweatherNP.AC2_PORT.value, config.plugins.MSNweatherNP.AC2inf.value)
        elif config.plugins.MSNweatherNP.AC2.value == 'samsung':
            from Plugins.Extensions.MSNweather.aircon_Controller_samsung import SamsungController
            self.session.openWithCallback(self.doNothing, SamsungController, config.plugins.MSNweatherNP.AC2_IP.value, config.plugins.MSNweatherNP.AC2_PORT.value, config.plugins.MSNweatherNP.AC2inf.value)

    def openDailyDetails(self):
        if self.weatherData is not None:
            if self.weatherData.weatherItems.get('-1', None) is not None:
                item2 = self.weatherData.weatherItems.get('-1').dictWeather['dailyData']
                item2 = item2.get('Record=0', {})
                if os.path.exists('/tmp/.MSNdata/dictMSNweather_dailyforecast_%s.json' % config.plugins.MSNweatherNP.currEntry.value) and \
                   os.path.exists('/tmp/.MSNdata/dictMSNweather_dailytrend_%s.json' % config.plugins.MSNweatherNP.currEntry.value) and \
                   os.path.exists('/tmp/.MSNdata/dictMSNweather_hourlytrend_%s.json' % config.plugins.MSNweatherNP.currEntry.value):
                    import Plugins.Extensions.MSNweather.APIdailyDetails
                    reload(Plugins.Extensions.MSNweather.APIdailyDetails)
                    self.session.open(Plugins.Extensions.MSNweather.APIdailyDetails.advDailyDetails, self.weatherData.weatherItems.get('-1', None))
                elif len(item2.get('dictdetalis', {})) > 0:
                    import Plugins.Extensions.MSNweather.dailyDetailsNP
                    reload(Plugins.Extensions.MSNweather.dailyDetailsNP)
                    self.session.open(Plugins.Extensions.MSNweather.dailyDetailsNP.MSNweatherDailyDetails, self.weatherData.weatherItems.get('-1', None))
        return

    def openMonthlyForecast(self):
        self.DEBUG('openMonthlyForecast()', ' >>>')
        if self.weatherData is None:
            self.DEBUG('\t', ' self.weatherData is None :(')
        else:
            self.DEBUG('\t', ' self.weatherData is not None opening MonthlyForecast')
            import Plugins.Extensions.MSNweather.MonthlyForecast
            reload(Plugins.Extensions.MSNweather.MonthlyForecast)
            self.session.open(Plugins.Extensions.MSNweather.MonthlyForecast.MonthlyForecast)
        return

    def getWeatherDataCallback(self, result, errortext):
        self.DEBUG('getWeatherDataCallback()', ' >>>')
        self['statustext'].text = ''
        if result == getWeather.ERROR:
            self.DEBUG('\t', 'result == getWeather.ERROR')
            self.error(errortext)
        else:
            self.DEBUG('\t', 'result == %s' % str(result))
            self.webSite = self.weatherData.url
            item = self.weatherData.weatherItems.get('-1', None)
            if item is not None:
                self.setFields(item)
                try:
                    c = time.strptime(item.observationtime, '%H:%M:%S')
                    self['currentData_observationtime'].text = _('Actualization time: %s') % time.strftime('%H:%M', c)
                except Exception:
                    self['currentData_observationtime'].text = item.observationtime

                self['observationpoint'].text = _('Observation point: %s') % item.observationpoint
                #self.DEBUG('\t', 'item.skytext == %s' % item.skytext)
                if 1: #populate currentData lists
                    tmpDict = item.dictWeather.get('currentData', {})
                    tmpList = []
                    tmpAllList = []
                    tmpListWeather = []
                    if len(tmpDict) > 0:
                        alert = str(tmpDict.get('alert', {}).get('valInfo', ''))
                        if alert == '':
                            self['currentData_airIndexAdvice'].text = str(tmpDict.get('airIndex', {}).get('advice', ''))
                        else:
                            self['currentData_airIndexAdvice'].text = alert
                        for key in tmpDict:
                            valDict = tmpDict[key]
                            if isinstance(valDict, dict):
                                inList = valDict.get('inList', False)
                                if inList:
                                    tmpAllList.append((str(valDict['name']), str(valDict['valInfo'])))
                                    if key in ('dew_point_temp', 'feelslike', 'humidity',
                                                'rel. humidity', 'pressure', 'visibility',
                                                'wind_speed','cloud_cover','uv_info', 'wind_gust', 'water_temp'):
                                        tmpListWeather.append((str(valDict['name']), str(valDict['valInfo'])))
                                    else:
                                        try:
                                            tmpList.append((str(valDict.get('longName', valDict['name'])), str(valDict['valInfo'])))
                                        except Exception:
                                            pass

                        try:
                            tmpList.sort(key=lambda t: tuple(str(t[0]).lower()))
                        except Exception:
                            tmpList.sort()

                        try:
                            tmpListWeather.sort(key=lambda t: tuple(str(t[0]).lower()))
                        except Exception:
                            tmpListWeather.sort()

                        try:
                            tmpAllList.sort(key=lambda t: tuple(str(t[0]).lower()))
                        except Exception:
                            tmpAllList.sort()

                    self['currentData_infoList'].list = tmpList
                    if len(tmpList) > 0:
                        self['airQualityTitle'].text = _('Air quality')
                    self['currentData_WeatherinfoList'].list = tmpListWeather
                    self['currentData_allInfoList'].list = tmpAllList
                    self['hourlyData_infoList'].list = []
                if 1: #populate hourlyData lists for vertical view
                    tmpDict = item.dictWeather['hourlyData']
                    tmpList = []
                    if len(tmpDict) > 0:
                        index = 0
                        self.DEBUG('\t', 'populate hourlyData_infoList')
                        pngH = LoadPixmap(cached=True, path='/usr/lib/enigma2/python/Plugins/Extensions/MSNweather/icons/humidity_icon.png')
                        pngT = LoadPixmap(cached=True, path='/usr/lib/enigma2/python/Plugins/Extensions/MSNweather/icons/temperature_icon.png')
                        while index < len(tmpDict.keys()):
                            try:
                                record = tmpDict[('Record=%s' % index)]
                                index += 1
                            except Exception as e:
                                break

                            iconfilename = str(record['imgfilename'])
                            #self.DEBUG('\t', 'record = %s\n' % str(record))
                            if iconfilename.endswith('.png'):
                                png = LoadPixmap(cached=True, path=iconfilename)
                                tmpList.append((png, '%s:00' % str(record['time']),
                                    str(record['temperature']),
                                    str(record['rainprecip']),
                                    str(record['skytext']),
                                    pngT, pngH))

                    self['hourlyData_infoList'].list = tmpList
                if 1: #populate dailyData lists for vertical view
                    tmpDict = item.dictWeather['dailyData']
                    tmpList = []
                    index = 0
                    if len(tmpDict) > 0:
                        self.DEBUG('\t', 'populate dailyData_infoList')
                        while index < len(tmpDict.keys()):
                            png = None
                            iconfilename = ''
                            try:
                                record = tmpDict[('Record=%s' % index)]
                                index += 1
                            except Exception as e:
                                self.DEBUG('record=%s exception: %s\n' % (index, str(e)))
                                break

                            if config.plugins.MSNweatherNP.IconsType.value == 'serviceIcons':
                                iconsList = (
                                    str(record['imgfilename']), str(record['iconfilename']))
                            else:
                                iconsList = (
                                    str(record['iconfilename']), str(record['imgfilename']))
                            for tmpIcon in iconsList:
                                if tmpIcon.endswith('.png') and os.path.exists(tmpIcon):
                                    iconfilename = tmpIcon
                                    png = LoadPixmap(cached=True, path=iconfilename)
                                    break

                            tmpList.append((png, '%s, %s' % (str(record['weekday']), str(record['monthday'])),
                                str(record['temp_high']),
                                str(record['temp_low']),
                                str(record['rainprecip']),
                                str(record['forecast'])))

                    self['dailyData_infoList'].list = tmpList
        if WeatherMSNComp is not None:
            self.DEBUG('getWeatherDataCallback invoking WeatherMSNComp.updateWeather')
            WeatherMSNComp.updateWeather(self.weatherData, result, errortext)
        return
