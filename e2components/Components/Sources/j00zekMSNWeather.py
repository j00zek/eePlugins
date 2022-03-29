# -*- coding: utf-8 -*-
#
# j00zek: this file is just to avoid GS-es, when msn weather plugin not installed 
# 
from __future__ import absolute_import #zmiana strategii ladowania modulow w py2 z relative na absolute jak w py3

import time
from Components.Sources.Source import Source 

class fakeSourcesMSNWaether(Source):
    def __init__(self): Source.__init__(self)
    def callbackAllIconsDownloaded(self): pass
    def getCity(self): return _("n/a")
    def getThingSpeakItems(self): return {}
    def getWebhourlyItems(self): return {}
    def getWebDailyItems(self): return {}
    def getObservationPoint(self): return _("n/a")
    def getObservationTime(self): return _("n/a")
    def getTemperature_Heigh(self, key): return _("n/a")
    def getTemperature_Low(self, key): return _("n/a")
    def getTemperature_Heigh_Low(self, key): return _("n/a")        
    def getTemperature_Text(self, key): return _("n/a")
    def getTemperature_Current(self): return _("n/a")
    def getFeelslike(self): return _("n/a")
    def getHumidity(self): return _("n/a")
    def getWinddisplay(self): return _("n/a")
    def getWeekday(self, key, short): return _("n/a")
    def getDate(self, key): return _("n/a")
    def getWeatherIconFilename(self, key): return ""
    def getCode(self, key): return ""
    def destroy(self): Source.destroy(self)
    def getWebCurrentItems(self): return {}
    def getIconPath(self): return ''
    def dictWeather(self, treePath = None): return {}
    
try:
    from Components.Sources.MSNWeatherNP import MSNWeatherNP as j00zekMSNWeather
    open("/tmp/j00zekMSNWeather.log", "w").write('j00zekMSNWeather imported')
except Exception as e:
    j00zekMSNWeather = fakeSourcesMSNWaether
    open("/tmp/j00zekMSNWeather.txt", "w").write('%s\n' % str(e))
