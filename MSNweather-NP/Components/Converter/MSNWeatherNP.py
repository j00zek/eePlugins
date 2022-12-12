# -*- coding: utf-8 -*-
#
# WeatherPlugin E2
#
# Coded by Dr.Best (c) 2012-2013, mod j00zek 2020-2021
# Support: www.dreambox-tools.info
# E-Mail: dr.best@dreambox-tools.info
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

from __future__ import absolute_import #zmiana strategii ladowanie modulow w py2 z relative na absolute jak w py3
from Components.config import config
from Components.Converter.Converter import Converter
from Components.Element import cached
from Components.j00zekModHex2strColor import Hex2strColor
from Plugins.Extensions.MSNweather.__init__ import _
from os import path
import datetime

DBG=False # for quick debugs

class MSNWeatherNP(Converter, object):

    CURRENT = -1
    DAY1 = 1
    DAY2 = 2
    DAY3 = 3
    DAY4 = 4
    DAY5 = 5    
    DAY6 = 6
    DAY7 = 7
    DAY8 = 8
    DAY9 = 9
    DAY10 = 10
    DAY11 = 11
    DAY12 = 12
    DAY13 = 13
    DAY14 = 14
    CITY = 15
    TEMPERATURE_HEIGH = 16
    TEMPERATURE_LOW = 17
    TEMPERATURE_TEXT = 18
    TEMPERATURE_CURRENT = 19
    WEEKDAY = 20
    WEEKSHORTDAY = 21
    DATE = 22
    OBSERVATIONTIME = 23
    OBSERVATIONPOINT = 24
    FEELSLIKE = 25
    HUMIDITY = 26
    WINDDISPLAY = 27
    ICON = 28
    TEMPERATURE_HEIGH_LOW = 29
    CODE = 30
    PATH = 31
    FULLDATE = 32
    WEATHERDICT = 33
    DAILYDICT = 34
    HOURLYDICT = 35
    CURRENTDICT = 36
    METEOGRAM = 37

    def __init__(self, type):
        Converter.__init__(self, type)
        self.index = None
        self.mode = None
        self.mode2 = ''
        self.path = None
        self.extension = None
        self.indexTXT = None
        self.dictWeather = {}
        self.dictWeatherRUNs = []
        if type == "city": self.mode = self.CITY
        elif type == "observationtime": self.mode = self.OBSERVATIONTIME
        elif type == "observationpoint": self.mode = self.OBSERVATIONPOINT
        elif type == "temperature_current": self.mode = self.TEMPERATURE_CURRENT
        elif type == "feelslike": self.mode = self.FEELSLIKE
        elif type == "humidity": self.mode = self.HUMIDITY
        elif type == "winddisplay": self.mode = self.WINDDISPLAY
        elif type.startswith("METEOGRAM"):
            self.mode = self.METEOGRAM
        elif type.startswith("DailyRecord="):
            self.mode = self.DAILYDICT
            self.mode2 = type.replace('Daily','')
        elif type.startswith("HourlyRecord="):
            self.mode = self.HOURLYDICT
            self.mode2 = type.replace('Hourly','')
        elif type.startswith("Current"):
            self.mode = self.CURRENTDICT
            self.mode2 = type.replace('Current','')
        elif type.startswith("RUN|") or type.startswith("GET|"):
            try:
                self.dictWeatherRUNs = type.split('|')
                self.dictWeatherRUNs.pop(0)
                if len(self.dictWeatherRUNs) > 0:
                    self.mode = self.WEATHERDICT
                    for n, cmd in enumerate(self.dictWeatherRUNs):
                        #self.EXCEPTIONDEBUG('cmd= |%s|' % cmd)
                        if cmd.startswith("0x"):
                            self.dictWeatherRUNs[n] = Hex2strColor(int(cmd, 16))
            except Exception as e:
                self.EXCEPTIONDEBUG('__init__ Exception enumarating RUN|GET %s' % str(e))
        else:
            if type.find("weathericon") != -1: self.mode = self.ICON
            elif type.find("temperature_high") != -1: self.mode = self.TEMPERATURE_HEIGH
            elif type.find("temperature_low") != -1: self.mode = self.TEMPERATURE_LOW
            elif type.find("temperature_heigh_low") != -1: self.mode = self.TEMPERATURE_HEIGH_LOW
            elif type.find("temperature_text") != -1: self.mode = self.TEMPERATURE_TEXT
            elif type.find("weekday") != -1: self.mode = self.WEEKDAY
            elif type.find("weekshortday") != -1: self.mode = self.WEEKSHORTDAY
            elif type.find("date") != -1: self.mode = self.DATE
            elif type.find("fulldate") != -1: self.mode = self.FULLDATE
            if self.mode is not None:
                dd = type.split(",")
                if len(dd) >= 2:
                    self.indexTXT = dd[1]
                    self.index = self.getIndex(self.indexTXT)
                if self.mode == self.ICON and len(dd) == 4:
                    self.path = dd[2]
                    self.extension = dd[3]
                    
    def EXCEPTIONDEBUG(self, myFUNC = '' , myText = '' ):
        from Plugins.Extensions.MSNweather.debug import printDEBUG
        printDEBUG( myFUNC , myText , 'MSNWeatherConverter.log' )
            
    def DEBUG(self, myFUNC = '' , myText = '' ):
        try:
            if DBG or config.plugins.MSNweatherNP.DebugEnabled.value:
                from Plugins.Extensions.MSNweather.debug import printDEBUG
                printDEBUG( myFUNC , myText , 'MSNWeatherConverter.log' )
        except Exception:
            pass

    def getIndex(self, key):
        self.DEBUG('getIndex key="%s"' % key) 
        if key == "current": return self.CURRENT
        elif key == "day1": return self.DAY1
        elif key == "day2": return self.DAY2
        elif key == "day3": return self.DAY3
        elif key == "day4": return self.DAY4
        elif key == "day5": return self.DAY5
        elif key == "day6": return self.DAY6
        elif key == "day7": return self.DAY7
        elif key == "day8": return self.DAY8
        elif key == "day9": return self.DAY9
        elif key == "day10": return self.DAY10
        elif key == "day11": return self.DAY11
        elif key == "day12": return self.DAY12
        elif key == "day13": return self.DAY13
        elif key == "day14": return self.DAY14
        return None

    @cached
    def getText(self):
        self.DEBUG('getText self.mode=%s, self.index=%s (%s)' %( self.mode, self.index, str(self.indexTXT))) 
        retText = ''
        if self.mode == self.CITY:
            retText = self.source.getCity()
        elif self.mode == self.OBSERVATIONPOINT:
            retText = self.source.getObservationPoint()
        elif self.mode == self.OBSERVATIONTIME:
            retText = self.source.getObservationTime()
        elif self.mode == self.TEMPERATURE_CURRENT:
            retText = self.source.getTemperature_Current()
        elif self.mode == self.FEELSLIKE:
            retText = self.source.getFeelslike()
        elif self.mode == self.HUMIDITY:
            retText = self.source.getHumidity()
        elif self.mode == self.WINDDISPLAY:
            retText = self.source.getWinddisplay()
        elif self.mode == self.TEMPERATURE_HEIGH and self.index is not None:
            retText = self.source.getTemperature_Heigh(self.index)
        elif self.mode == self.TEMPERATURE_LOW and self.index is not None:
            retText = self.source.getTemperature_Low(self.index)
        elif self.mode == self.TEMPERATURE_HEIGH_LOW and self.index is not None:
            retText = self.source.getTemperature_Heigh_Low(self.index)
        elif self.mode == self.TEMPERATURE_TEXT and self.index is not None:
            retText = self.source.getTemperature_Text(self.index)
        elif self.mode == self.WEEKDAY and self.index is not None:
            retText = self.source.getWeekday(self.index, False)
        elif self.mode == self.WEEKSHORTDAY and self.index is not None:
            retText = self.source.getWeekday(self.index, True)
        elif self.mode == self.DATE and self.index is not None:
            retText = self.source.getDate(self.index)
        elif self.mode == self.FULLDATE and self.index is not None:
            retText = self.source.getFullDate(self.index)
        elif self.mode == self.WEATHERDICT:
            try:
                for cmd in self.dictWeatherRUNs:
                    #self.DEBUG('cmd= ,%s,' % cmd)
                    if cmd.startswith("['"):
                        #self.DEBUG('running: %s' % cmd)
                        retText += self.source.dictWeather(cmd)
                    else:
                        retText += cmd
            except Exception as e:
                self.EXCEPTIONDEBUG('getText(WEATHERDICT) ','Exception %s running cmd %s' % (str(e), cmd))
        elif self.mode == self.DAILYDICT:
            try:
                mode2 = self.mode2.split(',')
                self.DEBUG('DAILYDICT','len(mode) =%s' % str(len(mode2)))
                if len(mode2) >= 2:
                    dictTree = "['dailyData']"
                    record = mode2[0]
                    #self.DEBUG('DAILYDICT ','record: %s' % str(record))
                    item =  mode2[1]
                    #self.DEBUG('DAILYDICT ','item: %s' % str(item))
                    day = int(record.split('=')[1])
                    Month = _((datetime.date.today() + datetime.timedelta(days=day)).strftime("%b"))
                    dictTree += "['%s']" % record
                    recordDict = self.source.dictWeather(dictTree)
                    #self.DEBUG('DAILYDICT ','recordDict:%s' % str(recordDict))
                    if item ==  'date':
                        weekday = recordDict['weekday']
                        monthday = recordDict['monthday']
                        retText = str('%s. %s %s' % (weekday, monthday, Month))
                    elif item ==  'info':
                        temp_high = recordDict['temp_high']
                        temp_low = recordDict['temp_low']
                        rainprecip = recordDict['rainprecip']
                        skytext = recordDict['skytext']
                        retText = str('%s/ %s/ %s\n%s' % (temp_high, temp_low, rainprecip, skytext))
                    elif item in ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9'):
                        retText = str('%s' % recordDict[int(item)].strip())
            except Exception as e:
                self.EXCEPTIONDEBUG('getText(DAILYDICT) ','Exception %s' % str(e))
        elif self.mode == self.HOURLYDICT:
            try:
                mode2 =  self.mode2.split(',')
                self.DEBUG('getText(HOURLYDICT)','mode:%s, len(%s)' % (str(mode2),len(mode2)))
                dictTree = "['hourlyData']"
                record = mode2[0]
                self.DEBUG('getText(HOURLYDICT) ','record: %s' % str(record))
                dictTree += "['%s']" % record
                recordDict = self.source.dictWeather(dictTree)
                self.DEBUG('getText(HOURLYDICT) ','recordDict:%s' % str(recordDict))
                if len(mode2) == 1:
                    time = recordDict['time']
                    skytext = recordDict['skytext']
                    temperature = recordDict['temperature']
                    rainprecip = recordDict['rainprecip']
                    retText = str('%s\n\n\n%s\nTemp. %s\nOpady %s' % (time, skytext, temperature, rainprecip))
                else:
                    item =  mode2[1]
                    if item in ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9'):
                        retText = str('%s' % recordDict[int(item)].strip())
            except Exception as e:
                self.EXCEPTIONDEBUG('getText(HOURLYDICT) ','Exception %s' % str(e))
        
        return str(retText)
    
    text = property(getText)
    
    @cached
    def getIconFilename(self):
        self.DEBUG('getIconFilename >>> self.mode = %s , self.index = %s (%s)' % (self.ICON,self.index, str(self.indexTXT)) )
        retVal = ''
        if self.mode == self.ICON and self.index in (self.CURRENT, self.DAY1, self.DAY2, self.DAY3, self.DAY4, self.DAY5):
            self.DEBUG('\t self.mode = self.ICON')
            if self.path is not None and self.extension is not None:
                self.DEBUG('\t self.path is not None and self.extension is not None')
                retVal = self.path + self.source.getCode(self.index) + "." + self.extension
            else:
                self.DEBUG('\t self.path is None and self.extension is None')
                retVal = self.source.getWeatherIconFilename(self.index)
                self.DEBUG('\t getWeatherIconFilename(%s) returned %s' % (self.index,retVal))
                if not retVal.endswith('.png'):
                    retVal = retVal + ".png"
                if len(retVal) <= 6:
                    retVal = self.source.getIconPath() + retVal
        elif self.mode == self.DAILYDICT:
            try:
                mode2 = self.mode2
                #self.DEBUG('DAILYDICT','mode2: %s' % str(mode2))
                dictTree = "['dailyData']"
                dictTree += "['%s']" % mode2
                recordDict = self.source.dictWeather(dictTree)
                #self.DEBUG('DAILYDICT ','recordDict:%s' % str(recordDict))
                if config.plugins.MSNweatherNP.IconsType.value != "serviceIcons":
                    iconFileName = recordDict['iconfilename'].strip()
                    #self.DEBUG('DAILYDICT ','iconFileName:%s' % str(iconFileName))
                    if iconFileName.endswith('.png') and path.exists(iconFileName):
                        return str(iconFileName)
                #service icons or not found
                return str(recordDict['imgfilename'].strip())
            except Exception as e:
                self.EXCEPTIONDEBUG('getIconFilename(DAILYDICT) ','Exception %s' % str(e))
        elif self.mode == self.HOURLYDICT:
            try:
                mode2 = self.mode2
                self.DEBUG('HOURLYDICT','mode2: %s' % str(mode2))
                dictTree = "['hourlyData']"
                dictTree += "['%s']" % mode2
                recordDict = self.source.dictWeather(dictTree)
                self.DEBUG('HOURLYDICT ','recordDict:%s' % str(recordDict))
                if config.plugins.MSNweatherNP.IconsType.value != "serviceIcons":
                    iconFileName = recordDict['iconfilename'].strip()
                    self.DEBUG('HOURLYDICT ','iconFileName:%s' % str(iconFileName))
                    if iconFileName.endswith('.png') and path.exists(iconFileName):
                        return str(iconFileName)
                #service icons or not found
                return str(recordDict['imgfilename'].strip())
            except Exception as e:
                self.EXCEPTIONDEBUG('getIconFilename(HOURLYDICT) ','Exception %s' % str(e))
        elif self.mode == self.METEOGRAM:
            retVal = '/usr/lib/enigma2/python/Plugins/Extensions/MSNweather/icons/meteogram.png'
        elif self.mode == self.WEATHERDICT:
            try:
                for cmd in self.dictWeatherRUNs:
                    self.DEBUG('cmd= |%s|' % str(cmd))
                    if cmd.startswith("['"):
                        if config.plugins.MSNweatherNP.hIconsType.value == 'weatherIcons' and cmd.startswith("['hourlyData']['Record=") and cmd.endswith("['imgfilename']"):
                            cmd = cmd.replace("'imgfilename'","'iconfilename'")
                        self.DEBUG('running: |%s|' % str(cmd))
                        retVal = str(self.source.dictWeather(cmd))
                        self.DEBUG('received: |%s|' % retVal)
            except Exception as e:
                self.EXCEPTIONDEBUG('getIconFilename(WEATHERDICT) ' , 'Exception %s running cmd %s' % (str(e), cmd))
        self.DEBUG('\t Finally converter returns for index "%s" than icon is "%s"' % (self.index,retVal))
        return str(retVal)
            
    iconfilename = property(getIconFilename)
