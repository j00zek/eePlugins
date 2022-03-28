# -*- coding: utf-8 -*-
from . import _
from Plugins.Extensions.MSNweather.MSNcomponents.GetAsyncWebDataNP import IMGtoICON
from Plugins.Extensions.MSNweather.MSNcomponents.mappings import getWindIconName

from Components.j00zekModHex2strColor import Hex2strColor as h2c, clr
from Components.j00zekAccellPixmap import j00zekAccellPixmap
from Components.j00zekSunCalculations import Sun
from Components.ActionMap import ActionMap
from datetime import datetime, timedelta
from enigma import getDesktop, ePoint, eSize, eTimer, ePicLoad
from Components.config import config
from Components.Label import Label
from Components.Pixmap import Pixmap
from Components.Sources.List import List
from Components.Sources.StaticText import StaticText
from os import path
from Screens.Screen import Screen
from Tools.LoadPixmap import LoadPixmap
import os, time

DBG = True

class MSNweatherDailyDetails(Screen):
    def __init__(self, session, weatherItems):
        self.session = session
        self.item = weatherItems
        self.skin = open('/usr/lib/enigma2/python/Plugins/Extensions/MSNweather/skins/skin_MSNweatherDailyDetails.xml', 'r').read()
        Screen.__init__(self, session)
        self['setupActions'] = ActionMap(['MSNweatherDailyDetails'], {'keyCancel': self.cancel, 
           'keyNextDay': self.NextDay, 
           'keyPreviousDay': self.PreviousDay, 
           'keyHourLeft': self.HourLeft, 
           'keyHourRight': self.HourRight}, -2)
        self.DEBUG('INIT', 'MSNweatherDailyDetails(Screen).__init__ >>>')
        self.dayIDX = 0
        self.Days = 0
        self.hourIDX = 0
        self.Hours = 0
        self.MaxHours = 6
        self['day_icon'] = j00zekAccellPixmap()
        self['day_skytext'] = StaticText()
        self['day_date'] = StaticText()
        self['day_infoList'] = List([])
        self['Day_Forecast'] = StaticText()
        self['details_List'] = List([])
        self['hourlyData_title'] = StaticText()
        self['h0_infoList'] = List([])
        self['h1_infoList'] = List([])
        self['h2_infoList'] = List([])
        self['h3_infoList'] = List([])
        self['h4_infoList'] = List([])
        self['h5_infoList'] = List([])
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
        if DBG:
            from Plugins.Extensions.MSNweather.MSNcomponents.debug import printDEBUG
            printDEBUG(myFUNC, myText, logFileName='MSNweatherDailyDetails.log')

    def __onShown(self):
        self.DEBUG('__onShown', ' >>>')
        self.setTitle(_('Detailed forecast'))
        self.title = _('Detailed forecast')
        self.Days = len(self.item.dictWeather['dailyData']) - 1
        self.DEBUG('__onShown', 'self.Days = %s' % self.Days)
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

    def loadIcon(self, iconName=None, dayDetails={}, hourlyIDX=0):
        retPNG = None
        if iconName is None or iconName == '' or dayDetails == {}:
            return retPNG
        if iconName == 'dailyIcon':
            if config.plugins.MSNweatherNP.IconsType.value == 'serviceIcons':
                iconsList = (
                 str(dayDetails['imgfilename']), str(dayDetails['iconfilename']))
            else:
                iconsList = (
                 str(dayDetails['iconfilename']), str(dayDetails['imgfilename']))
            for tmpIcon in iconsList:
                if tmpIcon.endswith('.png') and os.path.exists(tmpIcon):
                    retPNG = tmpIcon
                    break

        self.DEBUG('loadIcon', 'retPNG: %s ' % str(retPNG))
        return retPNG

    def getWindIcon(self, iconName=None):
        retPNG = None
        self.DEBUG('icons.getWindIcon', 'iconName: %s ' % iconName)
        if iconName is None or iconName == '':
            return
        retPNG = getWindIconName(iconName)
        if retPNG is not None and os.path.exists(retPNG):
            self.DEBUG('icons.getWindIcon ', 'retPNG: %s ' % retPNG)
            return LoadPixmap(cached=False, path=retPNG)
        else:
            return
            return

    def updateInfo(self):
        try:
            dayDetails = self.item.dictWeather['dailyData'][('Record=%s' % self.dayIDX)]
            dictdetails = dayDetails['dictdetalis']
            nowDate = datetime.now()
            dayDate = nowDate + timedelta(days=self.dayIDX)
            dayName = str(dayDetails.get('day', '?'))
            self['day_date'].text = '%s, %s' % (self.WeekDays.get(dayName, dayName), datetime.strftime(dayDate, '%d.%m.%Y'))
            self['day_icon'].updateIcon(self.loadIcon('dailyIcon', dayDetails))
            self['day_skytext'].text = str(dictdetails.get('skytext', '?' ))
            windIcon = self.getWindIcon(str(dictdetails.get('windDir', str(dictdetails.get('winddir', '?')) )))
            uvindex = str(dictdetails.get('uvindex', ''))
            if uvindex == '':
                self['day_infoList'].list = [
                    (
                        self.tempHigh_icon, str(dayDetails.get('temp_high', '?')),
                        self.tempLow_icon, str(dayDetails.get('temp_low', '?')),
                        self.rain, str(dayDetails.get('rainprecip', '?')),
                        windIcon, str(dictdetails.get('windSpeed', '?')),
                        self.no_icon, ' '
                    )]
            else:
                self['day_infoList'].list = [
                    (
                        self.tempHigh_icon, str(dayDetails.get('temp_high', '?')),
                        self.tempLow_icon, str(dayDetails.get('temp_low', '?')),
                        self.rain, str(dayDetails.get('rainprecip', '?')),
                        self.uv, str(dictdetails.get('uvindex', '?')),
                        windIcon, str(dictdetails.get('windSpeed', '?'))
                    )]
            self.DEBUG('updateInfo ', 'top middle...')
            self['Day_Forecast'].text = str(dayDetails.get('forecast', ''))
            longitude = self.item.dictWeather['currentData']['geo']['longitude']
            latitude = self.item.dictWeather['currentData']['geo']['latitude']
            sun = Sun()
            dayLengthDict = sun.getDayLength(longitude, latitude, year=dayDate.year, month=dayDate.month, day=dayDate.day)
            DayDiffTimesDict = sun.getDayDiffTimes(longitude, latitude, year=dayDate.year, month=dayDate.month, day=dayDate.day)
            if self.dayIDX == 0:
                sunrise = str(self.item.dictWeather['currentData']['sun']['sunrise']['TZtime'])
                sunset = str(self.item.dictWeather['currentData']['sun']['sunset']['TZtime'])
            else:
                sunrise = str(dictdetails['sunrise'])
                sunset = str(dictdetails['sunset'])
            sunriseMins = int(sunrise.split(':')[0]) * 60 + int(sunrise.split(':')[1])
            sunsetMins = int(sunset.split(':')[0]) * 60 + int(sunset.split(':')[1])
            dayLenghtMins = sunsetMins - sunriseMins
            textMainColor = h2c(16777062)
            dayLength = clr['B'] + '%s godzin i %s minut' % (int(dayLenghtMins / 60.0), dayLenghtMins - int(dayLenghtMins / 60.0) * 60)
            diffToShortest = textMainColor + 'będzie dłuższy od najkrótszego o ' + clr['G']
            if DayDiffTimesDict['diffToShortesttHours'] != 0:
                diffToShortest += '%s godzin i ' % DayDiffTimesDict['diffToShortesttHours']
            diffToShortest += '%s minut' % DayDiffTimesDict['diffToShortestMinutes']
            if DayDiffTimesDict['diffToShortesttHours'] == 0:
                diffToShortest += ' i %s sekund' % DayDiffTimesDict['diffToShortestSeconds']
            diffToLongest = textMainColor + '\ni krótszy od najdłuższego o ' + clr['R']
            if DayDiffTimesDict['diffToLongestHours'] != 0:
                diffToLongest += '%s godzin i ' % DayDiffTimesDict['diffToLongestHours']
            diffToLongest += '%s minut' % DayDiffTimesDict['diffToLongestMinutes']
            if DayDiffTimesDict['diffToLongestHours'] == 0:
                diffToLongest += ' i %s sekund' % DayDiffTimesDict['diffToLongestSeconds']
            
            #ustawienie tekstow w tablicy detali
            details_List = []
            #avgHi
            currVal = str(dictdetails.get('avgHi',''))
            if currVal == '':
                details_List.append('')
                details_List.append('')
            else:
                details_List.append('Średnia temperatura maksymalna')
                details_List.append(clr['R'] + currVal)
            #recHi
            currVal = str(dictdetails.get('avgHi',''))
            if currVal == '':
                details_List.append('')
                details_List.append('')
            else:
                details_List.append('Najwyższa zanotowana')
                details_List.append('%s%s %s(%s)' % (clr['R'], currVal, clr['Gray'], str(dictdetails.get('recHiYr','-'))))
            #avgLo
            currVal = str(dictdetails.get('avgLo',''))
            if currVal == '':
                details_List.append('')
                details_List.append('')
            else:
                details_List.append('Średnia temperatura minimalna')
                details_List.append(clr['B'] + currVal)
            #recLo
            currVal = str(dictdetails.get('recLo',''))
            if currVal == '':
                details_List.append('')
                details_List.append('')
            else:
                details_List.append('Najniższa zanotowana')
                details_List.append('%s%s %s(%s)' % (clr['B'], currVal, clr['Gray'], str(dictdetails.get('recLoYr','-'))))
            #avgRain
            currVal = str(dictdetails.get('avgRain',''))
            if currVal == '':
                details_List.append('')
                details_List.append('')
            else:
                details_List.append('Średnie opady')
                details_List.append(currVal)
            #recRain
            currVal = str(dictdetails.get('recRain',''))
            if currVal == '':
                details_List.append('')
                details_List.append('')
            else:
                details_List.append('Najwyższe zanotowane')
                details_List.append('%s %s(%s)' % (currVal, clr['Gray'], str(dictdetails.get('recRainYr','-'))))
            #sunrise
            details_List.append('Wschód słońca')
            details_List.append(sunrise)
            #sunset
            details_List.append('Zachód słońca')
            details_List.append(sunset)
            #info
            details_List.append('Dzień będzie trwał %s, %s %s' % (dayLength, diffToShortest, diffToLongest))
            #moonrise
            currVal = str(dictdetails.get('moonrise',''))
            if currVal == '':
                details_List.append('')
                details_List.append('')
            else:
                details_List.append('Wschód księżyca')
                details_List.append(currVal)
            #moonset
            currVal = str(dictdetails.get('moonset',''))
            if currVal == '':
                details_List.append('')
                details_List.append('')
            else:
                details_List.append('Zachód księżyca')
                details_List.append(currVal)
            #moon
            details_List.append(str(dictdetails.get('moon','')))
            
            self['details_List'].list = [tuple(details_List)]
            #self.DEBUG(str(tuple(details_List)))

        except Exception as e:
            self.DEBUG('updateInfo Exception: ', str(e))

        try:
            dicthourly = dayDetails['dicthourly']
            self.Hours = len(dicthourly['times'])
            precipitationsList = dicthourly.get('precipitations', [])
            skyCodesList = dicthourly.get('skyCodes', [])
            skyImagesList = dicthourly.get('skyImages', [])
            skyTextsList = dicthourly.get('skyTexts', [])
            temperaturesList = dicthourly.get('temperatures', [])
            timesList = dicthourly.get('times', [])
            windList = dicthourly.get('wind', [])
            windDirList = dicthourly.get('windDir', [])
            self.DEBUG('updateInfo ', 'cleaning hourly data...')
            hIDX = 0
            while hIDX < self.Hours and hIDX < 6:
                listName = 'h%s_infoList' % hIDX
                self[listName].list = []
                hIDX += 1

        except Exception as e:
            self.DEBUG('updateInfo Exception cleaning hourly data: ', str(e))
            self.DEBUG('\t self.Hours = ', str(self.Hours))

        try:
            self.DEBUG('updateInfo ', 'updating hourly data for %s hours...' % self.Hours)
            hIDX = 0
            while hIDX < self.Hours and hIDX < 6:
                listName = 'h%s_infoList' % hIDX
                hourIDX = self.hourIDX + hIDX
                self.DEBUG('hIDX = ', str(hIDX))
                skytext = str(skyTextsList[hourIDX])
                #self.DEBUG('skytext = ', str(skytext))
                weatherIcon = str(skyImagesList[hourIDX])
                if 'entityid/' in weatherIcon:
                    weatherIcon = weatherIcon.split('entityid/')[1].split('.img?')[0]
                self.DEBUG('weatherIcon = ', str(weatherIcon))
                if os.path.exists(weatherIcon):
                    imgWeather = weatherIcon
                    weatherIcon = LoadPixmap(cached=False, path=imgWeather)
                else:
                    imgWeather = '/usr/lib/enigma2/python/Plugins/Extensions/MSNweather/icons/%s.png' % weatherIcon
                    self.DEBUG('imgWeather = ', str(imgWeather))
                    iconWeather = IMGtoICON(imgWeather, skytext, int(timesList[hourIDX]), int(dictdetails['sunset'][:2]), int(dictdetails['sunrise'][:2]))
                    self.DEBUG('iconWeather = ', str(iconWeather))
                    if iconWeather != '' and config.plugins.MSNweatherNP.IconsType.value != 'serviceIcons' and os.path.exists(self.CurrentSkinPath + iconWeather):
                        weatherIcon = LoadPixmap(cached=False, path=self.CurrentSkinPath + iconWeather)
                    elif os.path.exists(imgWeather):
                        weatherIcon = LoadPixmap(cached=False, path=imgWeather)
                    else:
                        weatherIcon = None
                windIcon = self.getWindIcon(str(windDirList[hourIDX]))
                self.DEBUG('time = ', str(timesList[hourIDX]) + ':00')
                self.DEBUG('temperature = ', str(temperaturesList[hourIDX]) + '°C')
                self.DEBUG('precipitation = ', str(precipitationsList[hourIDX]) + '%')
                self.DEBUG('wind = ', str(windList[hourIDX]) + 'km/h')
                self[listName].list = [
                    (
                        str(timesList[hourIDX]) + ':00',
                        weatherIcon,
                        self.temperature_icon, str(temperaturesList[hourIDX]) + '°C',
                        self.rain, str(precipitationsList[hourIDX]) + '%',
                        windIcon, str(windList[hourIDX]) + 'km/h',
                        skytext)]
                self.DEBUG('updateInfo ', 'end')
                hIDX += 1

        except Exception as e:
            self.DEBUG('updateInfo Exception updating hourly data: ', str(e))

        return

    def keyOk(self):
        self.close()

    def cancel(self):
        self.close()