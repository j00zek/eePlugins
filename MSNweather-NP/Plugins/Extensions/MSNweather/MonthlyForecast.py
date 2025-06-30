# -*- coding: utf-8 -*-
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
import datetime, json, os, time, sys, traceback

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
        self['alertsDescr'] = StaticText()

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
        if 'EXCEPTION' in myFUNC.upper() or 'EXCEPTION' in myText.upper():
            doTrace = True
        else:
            doTrace = False
        if DBG or doTrace:
            from Plugins.Extensions.MSNweather.debug import printDEBUG
            if doTrace:
                printDEBUG(myFUNC, '%s\n%s' % (myText, traceback.format_exc()), logFileName='MonthlyForecast.log')
            else:
                printDEBUG(myFUNC, myText, logFileName='MonthlyForecast.log')

    def __onShown(self):
        self.DEBUG('__onShown', ' >>>')
        self.setTitle(_('Monthly forecast'))
        self.title = _('Monthly forecast')
        tmpDict = self.getJSONdata('dictMSNweather_weathertrends')
        try:
            self.CalendarDaysDict = tmpDict["value"][0]["responses"][0]["calendar"]["weather"][0]['days']
            self.DEBUG('\t', 'len(self.CalendarDaysDict): %s' % len(self.CalendarDaysDict))
        except Exception as e:
            self.CalendarDaysDict = {}
            self.DEBUG('\t', 'EXCEPTION: %s' % str(e))
        try:
            self.CalendarMonthsDict = tmpDict["value"][0]["responses"][0]["calendar"]["weather"][0]['summaries']
            self.DEBUG('\t', 'len(self.CalendarMonthsDict): %s' % len(self.CalendarMonthsDict))
        except Exception as e:
            self.CalendarMonthsDict = {}
            self.DEBUG('\t', 'EXCEPTION: %s' % str(e))
        try:
            self.unitsDict = tmpDict["value"][0]["units"]
        except Exception as e:
            self.unitsDict = { "distance": "km", "height": "cm", "pressure": "mbar", "speed": "km/h", 
                                "system": "Metric", "temperature": "°C", "time": "s"
                             }
            self.DEBUG('\t', 'EXCEPTION: %s' % str(e))
        tmpDict = None
        tmpDict = self.getJSONdata('dictWeather')
        self.iconsDict = tmpDict.get('iconsData', {})
        tmpDict = None
        
        if len(self.CalendarMonthsDict) == 0:
            self.months = 0
        else:
            self.months = len(self.CalendarMonthsDict) - 1
        self.DEBUG('\t', 'self.months = %s' % self.months)
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
        if self.months > 0:
            try: #CalendarMonthsDict
                self.DEBUG('\t', 'tworzę podsumowanie miesiąca')
                self['monthStr'].text = self.CalendarMonthsDict[self.monthIDX]['monthStr'] + ' ' + str(self.CalendarMonthsDict[self.monthIDX]['year'])
                self['MonthSummary'].text = '\n'.join(self.CalendarMonthsDict[self.monthIDX]['summary'])
                self['averageHigh'].text = str(int(self.CalendarMonthsDict[self.monthIDX]['averageHigh'])) + self.unitsDict['temperature']
                self['averageLow'].text = str(int(self.CalendarMonthsDict[self.monthIDX]['averageLow'])) + self.unitsDict['temperature']
                self['sunnyDays'].text = str(int(self.CalendarMonthsDict[self.monthIDX]['sunnyDays'])) + ' ' + _('days')
                self['rainyOrSnowyDays'].text = str(int(self.CalendarMonthsDict[self.monthIDX]['rainyOrSnowyDays'])) + ' ' + _('days')
            except Exception as e:
                self.DEBUG('\t', 'Exception: %s' % str(e))

        try: #CalendarDaysDict
            self.DEBUG('\t', 'tworzę dane dzienne')
            if self.months > 0:
                monthNR = self.CalendarMonthsDict[self.monthIDX]['month']
            else:
                monthNR = int(str(self.CalendarDaysDict[0]['daily']['valid']).split('-')[1])
                self['monthStr'].text = str(self.CalendarDaysDict[0]['daily']['valid'])[:7]
            minMonthIDX = -1
            maxMonthIDX = -1
            sumTempHigh = 0.0
            sumTempLow = 0.0
            sumRainyDays = 0
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
            currItemID = 0
            for currItem in self.daysData:
                currItemID += 1
                currItemDict = self.CalendarDaysDict[currIDX]['daily']
                sumTempHigh += float(currItemDict['tempHi'])
                sumTempLow += float(currItemDict['tempLo'])
                dayDateSTR = currItemDict['valid'].split('T')[0].split('-')
                dayDate = datetime.date(int(dayDateSTR[0]), int(dayDateSTR[1]), int(dayDateSTR[2]))
                dayNo = str(dayDate.day)
                tempHi = str(int(currItemDict['tempHi'])) + self.unitsDict['temperature'][:-1]
                tempLo = str(int(currItemDict['tempLo'])) + self.unitsDict['temperature'][:-1]
                rainPrecip = str(int(currItemDict['precip']))
                dayInfo = '%s, %s\n\n\n\n\n%s | %s | %s' % (dayNo, days[dayDate.weekday()],tempHi,tempLo, rainPrecip) + '%\n'
                dayInfo += str(int(currItemDict['windMax'])) + self.unitsDict['speed'] + ' '
                windDir = int(currItemDict['windMaxDir'])
                if windDir >= 45-23 and windDir < 45+23: dayInfo += chr(0x2199)
                elif windDir >= 90-23 and windDir < 90+23: dayInfo += chr(0x2190)
                elif windDir >= 90+45-23 and windDir < 90+45+23: dayInfo += chr(0x2196)
                elif windDir >= 180-23 and windDir < 180+23: dayInfo += chr(0x2191)
                elif windDir >= 180+45-23 and windDir < 180+45+23: dayInfo += chr(0x2197)
                elif windDir >= 270-23 and windDir < 270+23: dayInfo += chr(0x2192)
                elif windDir >= 270+45-23 and windDir < 270+45+23: dayInfo += chr(0x2198)
                else: dayInfo += chr(0x2193)
                self[currItem[0]].text = dayInfo
                picona = int(currItemDict['icon'])
                if picona in [19, 20, 22, 23, 46, 47, 75, 76, 81, 85]: sumRainyDays += 1
                picona = iconsMap.get(currItemDict['symbol']+'.png', self.iconsDict.get(str(picona), ''))
                self.DEBUG('\t', 'icon=%s, wicon=%s, micon=%s, picona=%s' % (currItemDict['icon'],self.iconsDict.get(str(picona), '?'), currItemDict['symbol'],picona))
                self[currItem[1]].text = picona
                currIDX += 1
                if currIDX > 32: #maxMonthIDX:
                    break
            if self.months == 0:
                self['averageHigh'].text = str(round(sumTempHigh / float(currItemID),1)) + "°C"
                self['averageLow'].text = str(round(sumTempLow / float(currItemID),1)) + "°C"
                self['sunnyDays'].text = str(currItemID - sumRainyDays) + ' ' + _('days')
                self['rainyOrSnowyDays'].text = str(sumRainyDays) + ' ' + _('days')
            
            try:
                alertDict = self.CalendarDaysDict[0]["alerts"][0]
                alertDescr = alertDict.get("credit")
                alertDescr += ' alert ' + alertDict.get("severity") + ' ' + alertDict.get("statusText")
                alertDescr += ' od ' + alertDict.get("start") + ' do ' + alertDict.get("start") + '\n'
                alertDescr += alertDict.get("desc")
                self['alertsDescr'].text = alertDescr
            except Exception:
                pass
        except Exception as e:
            self.DEBUG('\t EXCEPTION: ', str(e))

        return
    
    def clearDaysData(self):
        self.DEBUG("clearDaysData() >>>")
        for currItem in self.daysData:
            for subItem in currItem:
                self[subItem].text = ''
                #self.DEBUG("clearFields:StaticTextSources(%s)" % str(subItem))

    def keyOk(self):
        self.close()

    def cancel(self):
        self.close()
