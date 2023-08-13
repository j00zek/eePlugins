# -*- coding: utf-8 -*-
#
# WeatherPlugin E2
#
# Coded by Dr.Best (c) 2012-2013
# modified by j00zek 2018-2021
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

from Components.config import config
from Components.Sources.Source import Source
from Plugins.Extensions.MSNweather.__init__ import _
from Plugins.Extensions.MSNweather.updater import weathermsn
import time

DBG=False # for quick debugs

class MSNWeatherNP(Source):

    def __init__(self):
        self.DEBUG( '__init__')
        Source.__init__(self)
        #weathermsn.callbacksAllIconsDownloaded.append(self.callbackAllIconsDownloaded)
        weathermsn.callbacks.append(self.refreshCallback)
        weathermsn.getData()

    def EXCEPTIONDEBUG(self, myFUNC = '' , myText = '' ):
        from Plugins.Extensions.MSNweather.debug import printDEBUG
        printDEBUG( myFUNC , myText , 'MSNWeatherSource.log')
            
    def DEBUG(self, myFUNC = '' , myText = '' ):
        if DBG or config.plugins.MSNweatherNP.DebugEnabled.value:
            from Plugins.Extensions.MSNweather.debug import printDEBUG
            printDEBUG( myFUNC , myText , 'MSNWeatherSource.log')
    
    def decodeSTR(self, defVal):
        retVal = defVal
        if retVal.startswith("b'"):
            retVal = retVal[2:]
            if retVal.endswith("'"):
                retVal = retVal[:-1]
        return retVal
        
    def getIconPath(self):
        #self.DEBUG( 'getThingSpeakItems')
        return weathermsn.weatherData.iconpath
    
    def refreshCallback(self, result = None, errortext=None):
        self.DEBUG( 'refreshCallback')
        self.changed((self.CHANGED_ALL,))
            
    def callbackAllIconsDownloaded(self, result = None, errortext=None):
        self.DEBUG( 'callbackAllIconsDownloaded')
        self.changed((self.CHANGED_ALL,))
    
    def getCity(self):
        return weathermsn.weatherData.city
        
    def getObservationPoint(self):
        skey = "-1"
        if skey in weathermsn.weatherData.weatherItems:
            retVal = weathermsn.weatherData.weatherItems[skey].observationpoint
        else:
            retVal = ''
        self.DEBUG( 'getObservationPoint = "%s"' % retVal)
        return retVal
        
    def getObservationTime(self):
        skey = "-1"
        retVal = ''
        if skey in weathermsn.weatherData.weatherItems:
            item = weathermsn.weatherData.weatherItems[skey]
            if item.observationtime != "":
                retVal = item.observationtime
                if len(retVal) > 5:
                    try:
                        c =  time.strptime(retVal, "%H:%M:%S")
                        retVal = time.strftime("%H:%M",c)
                    except Exception:
                        pass
        self.DEBUG( 'getObservationTime = "%s"' % retVal)
        return retVal
        
    def dictWeather(self, treePath = None):
        skey = "-1"
        retVal = ''
        if skey in weathermsn.weatherData.weatherItems and not treePath is None and treePath.startswith("['"):
            try:
              retVal = eval('weathermsn.weatherData.weatherItems["-1"].dictWeather%s' % treePath)
            except Exception as e:
                self.DEBUG('dictWeather(%s)' % treePath,'EXCEPTION: %s' % str(e))
        return retVal
        
    def getTemperature_Heigh(self, key):
        retVal = ''
        skey = str(key)
        if skey in weathermsn.weatherData.weatherItems:
            item = weathermsn.weatherData.weatherItems[skey]
            highTemp = item.high
            if highTemp != '':
                retVal = "%s°%s" % (highTemp, weathermsn.weatherData.degreetype)
        if retVal == '':
            try:
                if skey == '-1': skey = "0"
                else: skey = str( int(skey) - 1)
                retVal = self.dictWeather("['dailyData']['Record=%s']['temp_high']"  % skey)
                self.DEBUG( 'getTemperature_Heigh "Record=%s" = "%s"' % (skey,retVal))
                retVal = "%s%s" % (retVal, weathermsn.weatherData.degreetype)
            except Exception as e:
                self.EXCEPTIONDEBUG( 'Exception %s' % str(e) )
        self.DEBUG( 'getTemperature_Heigh(%s) = "%s"' % (str(key),retVal))
        return retVal
    
    def getTemperature_Low(self, key):
        retVal = ''
        skey = str(key)
        if skey in weathermsn.weatherData.weatherItems:
            item = weathermsn.weatherData.weatherItems[skey]
            lowTemp = item.low
            if lowTemp != '':
                retVal = "%s°%s" % (lowTemp, weathermsn.weatherData.degreetype)
        if retVal == '':
            try:
                if skey == '-1': skey = "0"
                else: skey = str( int(skey) - 1)
                skey = str( int(key) - 1)
                retVal = self.dictWeather("['dailyData']['Record=%s']['temp_low']"  % skey)
                self.DEBUG( 'getTemperature_Low "Record=%s" = "%s"' % (skey,retVal))
                retVal = "%s%s" % (retVal, weathermsn.weatherData.degreetype)
            except Exception as e:
                self.EXCEPTIONDEBUG( 'getTemperature_Low Exception %s' % str(e) )
        self.DEBUG( 'getTemperature_Low(%s) = "%s"' % (str(key),retVal))
        return retVal
            
    def getTemperature_Heigh_Low(self, key):
        retVal = ''
        skey = str(key)
        if skey in weathermsn.weatherData.weatherItems:
            item = weathermsn.weatherData.weatherItems[skey]
            highTemp = item.high
            lowTemp = item.low
            if highTemp != '' and lowTemp != '':
                retVal = "%s°%s | %s°%s" % (highTemp, weathermsn.weatherData.degreetype, lowTemp, weathermsn.weatherData.degreetype)
        if retVal == '':
            try:
                if skey == '-1': skey = "0"
                else: skey = str( int(skey) - 1)
                retValh = self.dictWeather("['dailyData']['Record=%s']['temp_high']"  % skey)
                retVall = self.dictWeather("['dailyData']['Record=%s']['temp_low']"  % skey)
                self.DEBUG( 'getTemperature_Heigh_Low "Record=%s" = "%s"' % (skey,str(line)))
                retVal = "%s%s | %s%s" % (retValh, weathermsn.weatherData.degreetype, retVall, weathermsn.weatherData.degreetype)
            except Exception as e:
                self.EXCEPTIONDEBUG( 'getTemperature_Heigh_Low Exception %s' % str(e) )
        self.DEBUG( 'getTemperature_Heigh_Low(%s) = "%s"' % (str(key),retVal))
        return retVal
    
    def getTemperature_Text(self, key):
        retVal = '-?-'
        skey = str(key)
        if skey in weathermsn.weatherData.weatherItems:
            item = weathermsn.weatherData.weatherItems[skey]
            if skey == "-1":
                retVal = self.decodeSTR(item.skytext)
            else:
                retVal = self.decodeSTR(item.skytextday)
        self.DEBUG( 'getTemperature_Text(%s) = "%s"' % (str(key),retVal))
        return retVal
            
    def getTemperature_Current(self):
        retVal = '-?-'
        skey = "-1"
        if skey in weathermsn.weatherData.weatherItems:
            retVal = "%s°%s" % (weathermsn.weatherData.weatherItems[skey].temperature, weathermsn.weatherData.degreetype)
        self.DEBUG( 'getTemperature_Current() = "%s"' % (retVal))
        return retVal
            
    def getFeelslike(self):
        retVal = '-?-'
        skey = "-1"
        if skey in weathermsn.weatherData.weatherItems:
            retVal = "%s°%s" % (weathermsn.weatherData.weatherItems[skey].feelslike, weathermsn.weatherData.degreetype)
        self.DEBUG( 'getFeelslike(%s) = "%s"' % (skey,retVal))
        return retVal
    
    def getHumidity(self):
        retVal = ''
        skey = "-1"
        if skey in weathermsn.weatherData.weatherItems:
            return weathermsn.weatherData.weatherItems[skey].humidity
        else:
            return '-?-'
            
    def getWinddisplay(self):
        retVal = ''
        skey = "-1"
        if skey in weathermsn.weatherData.weatherItems:
            return weathermsn.weatherData.weatherItems[skey].winddisplay
        else:
            return '-?-'
    
    def getWeekday(self, key, short):
        retVal = ''
        skey = str(key)
        if skey in weathermsn.weatherData.weatherItems:
            item = weathermsn.weatherData.weatherItems[skey]
            if short:
                return item.shortday
            else:
                return item.day
        else:
            return '-?-'
            
    def getDate(self, key):
        retVal = ''
        skey = str(key)
        if skey in weathermsn.weatherData.weatherItems:
            item = weathermsn.weatherData.weatherItems[skey]
            c = time.strptime(item.date,"%Y-%m-%d")
            return time.strftime("%d. %b",c)
        else:
            return '-?-'
            
    def getFullDate(self, key):
        self.DEBUG("MSNWeather(Source).getFullDate(key=%s)" % key)
        retVal = ''
        skey = str(key)
        if skey in weathermsn.weatherData.weatherItems:
            item = weathermsn.weatherData.weatherItems[skey]
            c = time.strptime(item.date,"%Y-%m-%d")
            Day = time.strftime("%d",c)
            weekday = _(item.day)
            Month = _(time.strftime("%b",c)) 
            return str('%s. %s %s' % (weekday, Day, Month))
        else:
            return '-?-'
            
    def getWeatherIconFilename(self, key):
        self.DEBUG( 'getWeatherIconFilename(%s) >>>' % str(key))
        retVal = ''
        skey = str(key)
        if skey in weathermsn.weatherData.weatherItems:
            self.DEBUG('\t "%s" in weathermsn.weatherData.weatherItems' % skey)
            retVal = self.decodeSTR(weathermsn.weatherData.weatherItems[skey].iconFilename)
        if retVal == '':
            try:
                if skey == '-1': skey = "0"
                else: skey = str( int(skey) - 1)
                retVal = self.dictWeather("['dailyData']['Record=%s']['iconfilename']"  % skey)
                if retVal == '':
                    retVal = self.dictWeather("['dailyData']['Record=%s']['imgfilename']"  % skey)
                self.DEBUG('\t getWebDailyItems(Record=%s) returned "%s"' % (skey,retVal))
            except Exception as e:
                self.EXCEPTIONDEBUG('\t Exception in getWeatherIconFilename: %s' % str(e) )
        self.DEBUG('\t IconFilename(%s) = "%s"' % (str(key),retVal))
        return retVal
            
    def getCode(self, key):
        #self.DEBUG( 'getCode(%s) >>>' % str(key))
        retVal = ''
        skey = str(key)
        if skey in weathermsn.weatherData.weatherItems:
            retVal = weathermsn.weatherData.weatherItems[skey].code
        if retVal == '':
            try:
                if skey == '-1': skey = "0"
                else: skey = str( int(skey) - 1)
                #self.DEBUG( 'getCode skey = "%s"' % skey)
                retVal = self.dictWeather("['dailyData']['Record=%s']['skycode']"  % skey)
                self.DEBUG( 'getCode "Record=%s" = "%s"' % (skey,retVal))
            except Exception as e:
                self.EXCEPTIONDEBUG( 'getCode Exception %s' % str(e) )
        self.DEBUG( 'getCode(%s) = "%s"' % (str(key),retVal))
        return retVal

    def destroy(self):
        weathermsn.callbacksAllIconsDownloaded.remove(self.callbackAllIconsDownloaded)
        Source.destroy(self)
