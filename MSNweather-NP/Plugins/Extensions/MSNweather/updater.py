# -*- coding: utf-8 -*-
#
# WeatherPlugin E2
#
# Coded by Dr.Best (c) 2012-2013
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

from __future__ import absolute_import #zmiana strategii ladowania modulow w py2 z relative na absolute jak w py3
from Components.config import config
from enigma import eEnv, eTimer
from Plugins.Extensions.MSNweather.getWeather import getWeather

class WeatherMSN:
    TIMER_INTERVAL = 1200
    def __init__(self):
        self.weatherData = getWeather()
        self.callbacks = [ ]
        self.callbacksAllIconsDownloaded = []
        self.timer = eTimer()
        self.timer.callback.append(self.getData)
        self.DEBUG('WeatherMSN __init__')    
        
    def EXCEPTIONDEBUG(self, myFUNC = '' , myText = '' ):
        from Plugins.Extensions.MSNweather.debug import printDEBUG
        printDEBUG( myFUNC , myText )
            
    def DEBUG(self, myFUNC = '' , myText = '' ):
        if config.plugins.MSNweatherNP.DebugEnabled.value:
            from Plugins.Extensions.MSNweather.debug import printDEBUG
            printDEBUG( myFUNC , myText )
    
    def getData(self):
        self.DEBUG('WeatherMSN.getData')
        self.timer.stop()
        self.weatherData.getDefaultWeatherData(self.callback, self.callbackAllIconsDownloaded)
        self.timer.startLongTimer(self.TIMER_INTERVAL)
        
    def updateWeather(self, weather, result, errortext):
        self.DEBUG('WeatherMSN.updateWeather')
        if result == getWeather.OK:
            self.timer.stop()
            self.weatherData = weather
            self.weatherData.callback = None
            self.weatherData.callbackShowIcon = None
            self.weatherData.callbackAllIconsDownloaded = None
            self.callback(result, errortext)
            self.callbackAllIconsDownloaded()
            self.timer.startLongTimer(self.TIMER_INTERVAL)

    def callbackAllIconsDownloaded(self):
        self.DEBUG('WeatherMSN.callbackAllIconsDownloaded callbacksCount=%s' % len(self.callbacksAllIconsDownloaded))
        for x in self.callbacksAllIconsDownloaded:
            x()

    def callback(self, result, errortext):
        self.DEBUG('WeatherMSN.callback callbacksCount=%s' % len(self.callbacks))
        for x in self.callbacks:
            x(result, errortext)
    
weathermsn = WeatherMSN()
