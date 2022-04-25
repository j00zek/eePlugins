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
import json, os, time, sys

PyMajorVersion = sys.version_info.major

DBG = True

class advDailyDetails(Screen):
    def __init__(self, session, weatherItems):
        self.session = session
        self.item = weatherItems
        self.skin = open('/usr/lib/enigma2/python/Plugins/Extensions/MSNweather/skins/skin_advDailyDetails.xml', 'r').read()
        Screen.__init__(self, session)
        self['setupActions'] = ActionMap(['advDailyDetails'], {'keyCancel': self.cancel, 
           'keyNextDay': self.NextDay, 
           'keyPreviousDay': self.PreviousDay, 
           'keyHourLeft': self.HourLeft, 
           'keyHourRight': self.HourRight}, -2)
        self.DEBUG('INIT', 'advDailyDetails(Screen).__init__ >>>')
        self.dailyForecastDict = {}
        self.dailyTrendDict = {}
        self.hourlyTrendDict = {}
        self.dayIDX = 0
        self.Days = 0
        self.hourIDX = 0
        self.Hours = 0
        self.MaxHours = 6
        self['day_date'] = StaticText()
        self['day_tempHi'] = StaticText()
        self['day_tempLo'] = StaticText()
        self['day_UV'] = StaticText()

        self['moonriseLabel'] = StaticText()
        self['moonrise'] = StaticText()
        self['moonsetLabel'] = StaticText()
        self['moonset'] = StaticText()
        self['moonPhase'] = StaticText()

        self['day_length_summary'] = StaticText()

        self['day_title'] = StaticText(_('W dzień:'))
        self['day_icon'] = StaticText()
        self['Day_Forecast'] = StaticText()

        self['night_title'] = StaticText(_('W nocy:'))
        self['night_icon'] = StaticText()
        self['night_Forecast'] = StaticText()

        self['hourlyData_title'] = StaticText()
        self['h0_infoList'] = List([])
        self['h1_infoList'] = List([])
        self['h2_infoList'] = List([])
        self['h3_infoList'] = List([])
        self['h4_infoList'] = List([])
        self['h5_infoList'] = List([])
        
        self['h0_WeatherPixmap'] = StaticText()
        self['h1_WeatherPixmap'] = StaticText()
        self['h2_WeatherPixmap'] = StaticText()
        self['h3_WeatherPixmap'] = StaticText()
        self['h4_WeatherPixmap'] = StaticText()
        self['h5_WeatherPixmap'] = StaticText()
        
        self.WeekDays = {'Pn': 'Poniedziałek', 'Wt': 'Wtorek', 
           'Śr': 'Środa', 
           'Cz': 'Czwartek', 
           'Pt': 'Piątek', 
           'So': 'Sobota', 
           'N': 'Niedziela'}
        self['key_red'] = Label(_('Cancel'))
        self['key_green'] = Label('')
        self['key_yellow'] = Label('')
        self['key_blue'] = Label('')
        self.CurrentSkinPath = '/usr/share/enigma2/%s/weather_icons/' % config.skin.primary_skin.value.replace('skin.xml', '').replace('/', '')
        self.onShown.append(self.__onShown)

    def DEBUG(self, myFUNC='', myText=''):
        if DBG or 'EXCEPTION' in myFUNC or 'EXCEPTION' in myText:
            from Plugins.Extensions.MSNweather.debug import printDEBUG
            printDEBUG(myFUNC, myText, logFileName='advDailyDetails.log')

    def __onShown(self):
        self.DEBUG('__onShown', ' >>>')
        self.setTitle(_('Detailed forecast'))
        self.title = _('Detailed forecast')
        self.Days = len(self.item.dictWeather['dailyData']) - 1
        self.DEBUG('__onShown', 'self.Days = %s' % self.Days)
        self.startDelay = eTimer()
        self.startDelay.callback.append(self.startRun)
        self.startDelay.start(30, True)
        self.dailyForecastDict = self.getJSONdata('dictMSNweather_dailyforecast')
        self.dailyTrendDict = self.getJSONdata('dictMSNweather_dailytrend')
        self.hourlyTrendDict = self.getJSONdata('dictMSNweather_hourlytrend')

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

    def NextDay(self):
        self.dayIDX += 1
        if self.dayIDX >= self.Days:
            self.dayIDX = self.Days - 1
        self.hourIDX = 0
        self.updateInfo()

    def PreviousDay(self):
        self.dayIDX -= 1
        if self.dayIDX < 0:
            self.dayIDX = 0
        self.hourIDX = 0
        self.updateInfo()

    def HourLeft(self):
        if self.hourIDX > 0:
            self.hourIDX -= 1
        self.DEBUG('HourLeft() ', 'self.Hours = %s/%s' % (self.hourIDX, self.Hours))
        self.updateInfo()

    def HourRight(self):
        if self.hourIDX < self.Hours - 1:
            self.hourIDX += 1
        self.DEBUG('HourRight() ', 'self.Hours = %s/%s' % (self.hourIDX, self.Hours))
        self.updateInfo()

    def getIcon(self, skytext, urlIcon, hourlyIDX, sunsetInt, sunriseInt):
        self.DEBUG('\tgetIcon', '>>>')
        retPNG = None
        iconPath = resolveFilename(SCOPE_SKIN, config.skin.primary_skin.value + '/weather_icons/').replace('/skin.xml','')
        if skytext != '' and urlIcon != '':
            imgfilename = '/usr/lib/enigma2/python/Plugins/Extensions/MSNweather/icons/%s' % os.path.basename(urlIcon).replace('.img','.png')
            iconfilename = IMGtoICON(imgfilename, skytext, int(hourlyIDX), sunsetInt, sunriseInt)
            iconfilename = os.path.join(iconPath, iconfilename)
            self.DEBUG('\t\t', 'imgfilename: %s ' % imgfilename)
            self.DEBUG('\t\t', 'iconfilename: %s ' % iconfilename)
            self.DEBUG('\t\t', 'IconsType: %s ' % config.plugins.MSNweatherNP.IconsType.value)
            if config.plugins.MSNweatherNP.IconsType.value == 'serviceIcons':
                iconsList = (imgfilename, iconfilename)
            else:
                iconsList = (iconfilename, imgfilename)
            self.DEBUG('\t\t', 'iconsList: %s ' % str(iconsList))
            for tmpIcon in iconsList:
                if tmpIcon.endswith('.png') and os.path.exists(tmpIcon):
                    retPNG = tmpIcon
                    break

        self.DEBUG('\t\t', 'retPNG: %s ' % str(retPNG))
        return str(retPNG)

    def getWindIcon(self, iconName=None):
        retPNG = None
        self.DEBUG('\t', 'getWindIcon(iconName=%s) >>>' % iconName)
        if iconName is None or iconName == '':
            return
        retPNG = getWindIconName(iconName)
        self.DEBUG('\t\t', 'retPNG= %s' % str(retPNG))
        if retPNG is not None and os.path.exists(retPNG):
            return LoadPixmap(cached=False, path=retPNG)
        return

    def getJSONdata(self,fileName):
        self.DEBUG('getJSONdata(%s)' % fileName,'>>>')
        retDict = {}
        FileName = '/tmp/.MSNdata/%s_%s.json' % (fileName,config.plugins.MSNweatherNP.currEntry.value)
        if os.path.exists(FileName):
            try:
                if PyMajorVersion == 2:
                    with open(FileName, 'r') as (json_file):
                        data = json_file.read().decode('utf-8')
                        json_file.close()
                        retDict = json.loads(data)
                else:
                    with open(FileName, 'r') as (json_file):
                        retDict = json.load(json_file)
                        json_file.close()
                self.DEBUG('\t','%s records loaded' % len(retDict))
            except Exception as e:
                self.DEBUG('\t','EXCEPTION: %s' % (str(e)))
        else:
            self.DEBUG('\t','File does NOT exist !!!')
        
        return retDict

    def infoGodzin(self, valInt):
        if valInt == 1:         return '%s godzinę' % valInt
        elif valInt in [2,3,4]: return '%s godziny' % valInt
        else:                   return '%s godzin' % valInt
    
    def infoMinut(self, valInt):
        if valInt == 1: return '%s minutę' % valInt
        elif valInt in [2,3,4,22,23,24,32,33,34,42,43,44,52,53,54]: return '%s minuty' % valInt
        else:           return '%s minut' % valInt
    
    def infoSekund(self, valInt):
        if valInt == 1: return '%s sekundę' % valInt
        elif valInt in [2,3,4,22,23,24,32,33,34,42,43,44,52,53,54]: return '%s sekundy' % valInt
        else:           return '%s sekund' % valInt
    
    def updateInfo(self):
        self.DEBUG('updateInfo()', '>>>')
        try: #dailyDict
            self.DEBUG('\t', 'pobranie dailyDict')
            dailyDict = self.dailyForecastDict["value"][0]["responses"][0]["weather"][0]["days"][self.dayIDX]
            weekday = _(datetime.strptime(dailyDict['daily']['valid'][:10], '%Y-%m-%d').strftime("%a"))
            #day info
            self.DEBUG('\t', 'pogoda za dnia')
            self['day_icon'].text = self.getIcon(str(dailyDict['daily']['day']['cap']), dailyDict['daily']['day']['urlIcon'], 12, 7, 20)
            self['Day_Forecast'].text = str('\n'.join(dailyDict['daily']['day']['summaries']))
            if not 'wiatr' in self['Day_Forecast'].text.lower():
                self['Day_Forecast'].text += '\n' + getWindSummary(dailyDict['daily']['day']['windSpd'])
            self.DEBUG('\t', 'pogoda w nocy')
            self['night_icon'].text = self.getIcon(str(dailyDict['daily']['night']['cap']), dailyDict['daily']['night']['urlIcon'], 22, 7, 20)
            self['night_Forecast'].text = str('\n'.join(dailyDict['daily']['night']['summaries']))
            if not 'wiatr' in self['night_Forecast'].text.lower():
                self['night_Forecast'].text += '\n' + getWindSummary(dailyDict['daily']['night']['windSpd'])
            #windIcon = self.getWindIcon(str(dictdetails.get('windDir', str(dictdetails.get('winddir', '?')) )))
            
            self.DEBUG('\t', 'podsumowanie dnia')
            self['day_date'].text = _('Prognoza na %s, %s') % (weekday , str(dailyDict['daily']['valid'][:10]))
            self['day_tempHi'].text = str(int(dailyDict['daily']['tempHi'])) + '‎°'
            self['day_tempLo'].text = str(int(dailyDict['daily']['tempLo'])) + '‎°'
            self['day_UV'].text = str(dailyDict['daily']['uvDesc'])

            #info dla księżyca
            self['moonriseLabel'].text = _('Wschód księżyca')
            self['moonrise'].text = str(dailyDict['almanac']['moonrise'][11:16])
            self['moonsetLabel'].text = _('Zachód księżyca')
            self['moonset'].text = str(dailyDict['almanac']['moonset'][11:16])
            self['moonPhase'].text = str(dailyDict['almanac']['moonPhase'])

            longitude = self.item.dictWeather['currentData']['geo']['longitude']
            latitude = self.item.dictWeather['currentData']['geo']['latitude']
            sun = Sun()
            dayDate = datetime.strptime(dailyDict['daily']['valid'][:10], '%Y-%m-%d')
            DayDiffTimesDict = sun.getDayDiffTimes(longitude, latitude, year=dayDate.year, month=dayDate.month, day=dayDate.day)
            sunrise = str(dailyDict['almanac']['sunrise'])[11:16]
            sunset = str(dailyDict['almanac']['sunset'])[11:16]
            sunriseMins = int(sunrise.split(':')[0]) * 60 + int(sunrise.split(':')[1])
            sunsetMins = int(sunset.split(':')[0]) * 60 + int(sunset.split(':')[1])
            dayLenghtMins = sunsetMins - sunriseMins
            

            dictTrend = self.dailyTrendDict["value"][0]["responses"][0]["average"][0]["days"][self.dayIDX]

            dayLengthH = int(dayLenghtMins / 60.0)
            dayLengthM = dayLenghtMins - dayLengthH * 60
            textMainColor = h2c(16777062)
            
            #podsumowanie dnia
            summaryDayInfo = _('Sun ')
            if sunriseMins > (datetime.now().hour * 60 + datetime.now().minute): 
                summaryDayInfo += _('will rise at %s') % sunrise[1:]
            else:
                summaryDayInfo += _('rose at %s') % sunrise[1:]
            if sunsetMins > (datetime.now().hour * 60 + datetime.now().minute):
                summaryDayInfo += _(' and goes down at %s. ') % sunset
            else:
                summaryDayInfo += _(' and went down at %s. ') % sunset
            summaryDayInfo += _('Day will take %s%s and %s') % (clr['B'], self.infoGodzin(dayLengthH), self.infoMinut(dayLengthM))
            
            summaryDayInfo += textMainColor + ', będzie dłuższy od najkrótszego o ' + clr['G']
            if DayDiffTimesDict['diffToShortesttHours'] != 0:
                summaryDayInfo += self.infoGodzin(DayDiffTimesDict['diffToShortesttHours']) + ' i '

            summaryDayInfo += self.infoMinut(DayDiffTimesDict['diffToShortestMinutes'])

            if DayDiffTimesDict['diffToShortesttHours'] == 0:
                summaryDayInfo += ' i ' + self.infoSekund(DayDiffTimesDict['diffToShortestSeconds'])
            
            
            summaryDayInfo += ' ' + textMainColor + 'i krótszy od najdłuższego o ' + clr['R']
            if DayDiffTimesDict['diffToLongestHours'] != 0:
                summaryDayInfo += self.infoGodzin(DayDiffTimesDict['diffToLongestHours']) + ' i '
            summaryDayInfo += self.infoMinut(DayDiffTimesDict['diffToLongestMinutes'])
            if DayDiffTimesDict['diffToLongestHours'] == 0:
                summaryDayInfo += ' i ' + self.infoSekund(DayDiffTimesDict['diffToLongestSeconds'])
            
            summaryDayInfo += clr['Gray'] + '\n' + 'W ostatnich ' + str(int(dictTrend['aggYears'])) + ' latach w tym dniu...'
            for condition in dictTrend['conditions']:
                if condition['days'] > 0:
                    if condition['type'] == 'Rain':
                        summaryDayInfo += clr['Gray'] + '\n' + '- deszcz padał ' + str(int(condition['days'])) + ' dni, średnie opady ' + str(dictTrend['avgPrecip'])
                        summaryDayInfo += clr['Gray'] + ', maksymalne ' + str(dictTrend['recPrecip']) + ' w ' + str(dictTrend['precipDate'][:4]) + 'r'
                    elif condition['type'] == 'Snow':
                        summaryDayInfo += clr['Gray'] + '\n' + '- śnieg padał ' + str(int(condition['days'])) + ' dni, średnie opady ' + str(dictTrend['avgSnow'])
                        summaryDayInfo += clr['Gray'] + ', maksymalne ' + str(dictTrend['recSnow']) + ' w ' + str(dictTrend['snowDate'][:4]) + 'r'
                    else:
                        summaryDayInfo += clr['Gray'] + '\n- ' + _(str(condition['type'])) + ' padal ' + str(int(condition['days'])) + ' dni, '
            if summaryDayInfo[:-2] == ', ':
                summaryDayInfo = summaryDayInfo[:-2]
            summaryDayInfo += clr['Gray'] + '\n' + '- Średnia temperatura maksymalna wynosiła %s%s°C%s, najwyższa zanotowana %s%s°C%s w %s%sr' % (clr['R'], 
                                                                                                                                             str(int(dictTrend['tempHi'])), 
                                                                                                                                             clr['Gray'],
                                                                                                                                             clr['R'],
                                                                                                                                             str(int(dictTrend['recHi'])),
                                                                                                                                             clr['Gray'],
                                                                                                                                             clr['Y'],
                                                                                                                                             str(dictTrend['hiDate'])[:4])
            summaryDayInfo += clr['Gray'] + '\n' + '- Średnia temperatura minimalna wynosiła %s%s°C%s, najniższa zanotowana %s%s°C%s w %s%sr' % (clr['B'], 
                                                                                                                                             str(int(dictTrend['tempLo'])), 
                                                                                                                                             clr['Gray'],
                                                                                                                                             clr['B'],
                                                                                                                                             str(int(dictTrend['recLo'])),
                                                                                                                                             clr['Gray'],
                                                                                                                                             clr['Y'],
                                                                                                                                             str(dictTrend['loDate'])[:4])
            self['day_length_summary'].text = summaryDayInfo
        except Exception as e:
            self.DEBUG('\t', 'Exception: %s' % str(e))

        try: #dicthourly
            self.DEBUG('\t', 'pobieram dicthourly')
            dicthourly = self.hourlyTrendDict['value'][0]['responses'][0]['weather'][0]['days'][self.dayIDX]['hourly']
            self.Hours = len(dicthourly)
            self.DEBUG('\t ', '%s rekordów' % self.Hours)
            self.DEBUG('\t', 'czyszczenie danych godzinowych')
            hIDX = 0
            while hIDX < self.Hours and hIDX < 6:
                listName = 'h%s_infoList' % hIDX
                self[listName].list = []
                hIDX += 1

        except Exception as e:
            self.DEBUG('\t EXCEPTION: ', str(e))

        try: #tworzenie tablic godzinowych
            self.DEBUG('\t', 'aktualizuje dane godzinowe')
            hIDX = 0
            while hIDX < self.Hours and hIDX < 6:
                listName = 'h%s_infoList' % hIDX
                WeatherPixmapName = 'h%s_WeatherPixmap' % hIDX
                hourIDX = self.hourIDX + hIDX
                self.DEBUG('\thIDX = ', str(hIDX))
                hourDict = dicthourly[hourIDX]
                skytext = str(hourDict['cap'])
                self.DEBUG('\tskytext = ', skytext)
                #weatherIcon = self.getIcon(skytext, hourDict['urlIcon'], hourIDX, int(dailyDict['almanac']['sunset'][11:13]), int(dailyDict['almanac']['sunrise'][11:13]) )
                #if os.path.exists(weatherIcon):
                #    imgWeather = weatherIcon
                #    weatherIcon = LoadPixmap(cached=False, path=imgWeather)
                #else:
                #    weatherIcon = None
                windIcon = self.getWindIcon(str(hourDict['windDir']))
                self.DEBUG('\ttime = ', str(hourDict['valid'][11:16]))
                self.DEBUG('\ttemperature = ', str(int(hourDict['temp'])) + '°C')
                self.DEBUG('\tprecipitation = ', str(int(hourDict['precip'])) + '%')
                self.DEBUG('\twind = ', str(int(hourDict['windSpd'])) + 'km/h')
                self[listName].list = [
                    (
                        str(hourDict['valid'][11:16]),
                        self.temperature_icon, str(int(hourDict['temp'])) + '°C',
                        self.rain, str(int(hourDict['precip'])) + '%',
                        windIcon, str(int(hourDict['windSpd'])) + 'km/h',
                        skytext)]
                self[WeatherPixmapName].text = self.getIcon(skytext, hourDict['urlIcon'], int(hourDict['valid'][11:13]), int(dailyDict['almanac']['sunset'][11:13]), int(dailyDict['almanac']['sunrise'][11:13]))
                self.DEBUG('\t', '<<<')
                hIDX += 1

        except Exception as e:
            self.DEBUG('updateInfo Exception updating hourly data: ', str(e))

        return

    def keyOk(self):
        self.close()

    def cancel(self):
        self.close()
