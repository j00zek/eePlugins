# -*- coding: utf-8 -*-
from __future__ import absolute_import #zmiana strategii ladowanie modulow w py2 z relative na absolute jak w py3
from . import _
from Plugins.Extensions.MSNweather.MSNcomponents.GetAsyncWebDataNP import IMGtoICON
from Plugins.Extensions.MSNweather.MSNcomponents.mappings import *

from Components.j00zekModHex2strColor import Hex2strColor as h2c, clr
#from Components.j00zekAccellPixmap import j00zekAccellPixmap
from Components.Renderer.j00zekMSNWeatherPixmap import j00zekMSNWeatherPixmap
from Components.j00zekSunCalculations import Sun
from Components.ActionMap import ActionMap
from datetime import datetime, timedelta
from enigma import getDesktop, ePoint, eSize, eTimer
from Components.config import config
from Components.Label import Label
from Components.Pixmap import Pixmap
from Components.Sources.List import List
from Components.Sources.StaticText import StaticText
from os import path
from Screens.Screen import Screen
from Tools.Directories import resolveFilename, SCOPE_SKIN
from Tools.LoadPixmap import LoadPixmap
import datetime, json, os, time, sys

PyMajorVersion = sys.version_info.major

DBG = True

class MonthlyForecast(Screen):
    def __init__(self, session):
        self.session = session
        self.skin = open('/usr/lib/enigma2/python/Plugins/Extensions/MSNweather/skins/skin_MonthlyForecast.xml', 'r').read()
        Screen.__init__(self, session)
        self['setupActions'] = ActionMap(['MonthlyForecast'], 
                                         {'keyCancel': self.cancel, 
                                          'keyUp': self.NextMonth, 
                                          'keyDown': self.PreviousMonth, 
                                          'keyLeft': self.PreviousMonth, 
                                          'keyRight': self.NextMonth
                                         }, -2
                                        )
        self.DEBUG('INIT', 'MonthlyForecast(Screen).__init__ >>>')
        self.CalendarDaysDict = {}
        self.unitsDict = {}
        self.iconsDict = {}
        self.CalendarMonthsDict = {}
        self.monthIDX = 0
        self.months = 0
        
        #month summary
        self['monthStr'] = StaticText()
        self['averageHigh'] = StaticText()
        self['averageLow'] = StaticText()
        self['sunnyDays'] = StaticText()
        self['rainyOrSnowyDays'] = StaticText()
        self['MonthSummary'] = StaticText()

        self.daysData = [('d0_Summary', 'd0_WeatherPixmap'),   ('d1_Summary', 'd1_WeatherPixmap'),
                         ('d2_Summary', 'd2_WeatherPixmap'),   ('d3_Summary', 'd3_WeatherPixmap'),
                         ('d4_Summary', 'd4_WeatherPixmap'),   ('d5_Summary', 'd5_WeatherPixmap'),
                         ('d6_Summary', 'd6_WeatherPixmap'),   ('d7_Summary', 'd7_WeatherPixmap'),
                         ('d8_Summary', 'd8_WeatherPixmap'),   ('d9_Summary', 'd9_WeatherPixmap'),
                         ('d10_Summary', 'd10_WeatherPixmap'), ('d11_Summary', 'd11_WeatherPixmap'),
                         ('d12_Summary', 'd12_WeatherPixmap'), ('d13_Summary', 'd13_WeatherPixmap'),
                         ('d14_Summary', 'd14_WeatherPixmap'), ('d15_Summary', 'd15_WeatherPixmap'),
                         ('d16_Summary', 'd16_WeatherPixmap'), ('d17_Summary', 'd17_WeatherPixmap'),
                         ('d18_Summary', 'd18_WeatherPixmap'), ('d19_Summary', 'd19_WeatherPixmap'),
                         ('d20_Summary', 'd20_WeatherPixmap'), ('d21_Summary', 'd21_WeatherPixmap'),
                         ('d22_Summary', 'd22_WeatherPixmap'), ('d23_Summary', 'd23_WeatherPixmap'),
                         ('d24_Summary', 'd24_WeatherPixmap'), ('d25_Summary', 'd25_WeatherPixmap'),
                         ('d26_Summary', 'd26_WeatherPixmap'), ('d27_Summary', 'd27_WeatherPixmap'),
                         ('d28_Summary', 'd28_WeatherPixmap'), ('d29_Summary', 'd29_WeatherPixmap'),
                         ('d30_Summary', 'd30_WeatherPixmap'), ('d31_Summary', 'd31_WeatherPixmap'),
                         ('d32_Summary', 'd32_WeatherPixmap')
                        ]
        for currItem in self.daysData:
            for subItem in currItem:
                self[subItem] = StaticText()

        self['key_red'] = Label(_('Cancel'))
        self['key_green'] = Label('')
        self['key_yellow'] = Label('')
        self['key_blue'] = Label('')
        self.CurrentSkinPath = '/usr/share/enigma2/%s/weather_icons/' % config.skin.primary_skin.value.replace('skin.xml', '').replace('/', '')
        self.onShown.append(self.__onShown)

    def DEBUG(self, myFUNC='', myText=''):
        if DBG or 'EXCEPTION' in myFUNC or 'EXCEPTION' in myText:
            from Plugins.Extensions.MSNweather.debug import printDEBUG
            printDEBUG(myFUNC, myText, logFileName='MonthlyForecast.log')

    def __onShown(self):
        self.DEBUG('__onShown', ' >>>')
        self.setTitle(_('Monthly forecast'))
        self.title = _('Monthly forecast')
        tmpDict = self.getJSONdata('dictMSNweather_calendar')
        try:
            self.CalendarDaysDict = tmpDict["value"][0]["responses"][0]["weather"][0]['days']
            self.CalendarMonthsDict = tmpDict["value"][0]["responses"][0]["weather"][0]['summaries']
            self.unitsDict = tmpDict["value"][0]["units"]
            tmpDict = None
        except Exception as e:
            self.DEBUG('__onShown', 'EXCEPTION: %s' % str(e))
        tmpDict = self.getJSONdata('dictWeather')
        self.iconsDict = tmpDict.get('iconsData', {})
        
        self.months = len(self.CalendarMonthsDict) - 1
        self.DEBUG('__onShown', 'self.months = %s' % self.months)
        self.startDelay = eTimer()
        self.startDelay.callback.append(self.startRun)
        self.startDelay.start(30, True)

    def startRun(self):
        self.startDelay.stop()
        self.humidity_icon = LoadPixmap(cached=False, path='/usr/lib/enigma2/python/Plugins/Extensions/MSNweather/icons/humidity_icon.png')
        self.temperature_icon = LoadPixmap(cached=False, path='/usr/lib/enigma2/python/Plugins/Extensions/MSNweather/icons/temperature_icon.png')
        self.tempHigh_icon = LoadPixmap(cached=False, path='/usr/lib/enigma2/python/Plugins/Extensions/MSNweather/icons/temp+.png')
        self.tempLow_icon = LoadPixmap(cached=False, path='/usr/lib/enigma2/python/Plugins/Extensions/MSNweather/icons/temp-.png')
        self.rain = LoadPixmap(cached=False, path='/usr/lib/enigma2/python/Plugins/Extensions/MSNweather/icons/rain_icon.png')
        self.uv = LoadPixmap(cached=False, path='/usr/lib/enigma2/python/Plugins/Extensions/MSNweather/icons/uv_icon.png')
        self.no_icon = LoadPixmap(cached=False, path='/usr/lib/enigma2/python/Plugins/Extensions/MSNweather/icons/no_icon.png')
        self.updateInfo()

    def NextMonth(self):
        self.monthIDX += 1
        if self.monthIDX >= self.months:
            self.monthIDX = self.months
        self.updateInfo()

    def PreviousMonth(self):
        self.monthIDX -= 1
        if self.monthIDX < 0:
            self.monthIDX = 0
        self.updateInfo()

    def getJSONdata(self,fileName):
        self.DEBUG('getJSONdata(%s)' % fileName,'>>>')
        retDict = {}
        FileName = '/tmp/.MSNdata/%s_%s.json' % (fileName,config.plugins.MSNweatherNP.currEntry.value)
        if os.path.exists(FileName):
            try:
                with open(FileName, 'r') as (json_file):
                    retDict = json.load(json_file)
                    json_file.close()
                self.DEBUG('\t','%s records loaded' % len(retDict))
            except Exception as e:
                self.DEBUG('\t','EXCEPTION: %s' % (str(e)))
        else:
            self.DEBUG('\t','File does NOT exist !!!')
        
        return retDict

    def updateInfo(self):
        self.DEBUG('updateInfo()', '>>>')
        self.clearDaysData()
        try: #CalendarMonthsDict
            self.DEBUG('\t', 'podsumowanie miesiąca')
            self['monthStr'].text = self.CalendarMonthsDict[self.monthIDX]['monthStr'] + ' ' + str(self.CalendarMonthsDict[self.monthIDX]['year'])
            self['MonthSummary'].text = '\n'.join(self.CalendarMonthsDict[self.monthIDX]['summary'])
            self['averageHigh'].text = str(int(self.CalendarMonthsDict[self.monthIDX]['averageHigh'])) + self.unitsDict['temperature']
            self['averageLow'].text = str(int(self.CalendarMonthsDict[self.monthIDX]['averageLow'])) + self.unitsDict['temperature']
            self['sunnyDays'].text = str(int(self.CalendarMonthsDict[self.monthIDX]['sunnyDays'])) + ' ' + _('days')
            self['rainyOrSnowyDays'].text = str(int(self.CalendarMonthsDict[self.monthIDX]['rainyOrSnowyDays'])) + ' ' + _('days')
        except Exception as e:
            self.DEBUG('\t', 'Exception: %s' % str(e))
            return

        try: #CalendarDaysDict
            self.DEBUG('\t', 'dane dzienne')
            monthNR = self.CalendarMonthsDict[self.monthIDX]['month']
            minMonthIDX = -1
            maxMonthIDX = -1
            currIDX = 0
            for day in self.CalendarDaysDict:
                dayMonth = int(str(self.CalendarDaysDict[currIDX]['daily']['valid']).split('-')[1])
                if monthNR == dayMonth:
                    if minMonthIDX == -1:
                        minMonthIDX = currIDX
                    else:
                        maxMonthIDX = currIDX
                currIDX += 1
            self.DEBUG('\t', 'minMonthIDX=%s, maxMonthIDX=%s' % (minMonthIDX,maxMonthIDX))
            
            currIDX = minMonthIDX
            days = [_('Mon'), _('Tue'), _('Wed'), _('Thu'), _('Fri'), _('Sat'), _('Sun')]
            for currItem in self.daysData:
                currItemDict = self.CalendarDaysDict[currIDX]['daily']
                dayDateSTR = currItemDict['valid'].split('T')[0].split('-')
                dayDate = datetime.date(int(dayDateSTR[0]), int(dayDateSTR[1]), int(dayDateSTR[2]))
                dayNo = str(dayDate.day)
                tempHi = str(int(currItemDict['tempHi'])) + self.unitsDict['temperature']
                tempLo = str(int(currItemDict['tempLo'])) + self.unitsDict['temperature']
                rainPrecip = str(int(currItemDict['precip']))
                self[currItem[0]].text = '%s, %s\n\n\n\n\n%s | %s\n%s' % (dayNo, days[dayDate.weekday()],tempHi,tempLo, rainPrecip) + '%'
                picona = self.iconsDict.get(str(currItemDict['icon']), '')
                self.DEBUG('\t', picona)
                self[currItem[1]].text = picona
                currIDX += 1
                if currIDX > 32: #maxMonthIDX:
                    break
        except Exception as e:
            self.DEBUG('\t EXCEPTION: ', str(e))

        return
    
    def clearDaysData(self):
        for currItem in self.daysData:
            for subItem in currItem:
                self[subItem].text = ''
                self.DEBUG("clearFields:StaticTextSources(%s)" % str(subItem))

    def keyOk(self):
        self.close()

    def cancel(self):
        self.close()
