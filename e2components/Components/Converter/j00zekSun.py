#
# j00zek 2018 
#
from __future__ import absolute_import #zmiana strategii ladowanie modulow w py2 z relative na absolute jak w py3
from Components.config import config
from Components.Converter.Converter import Converter
from Components.Element import cached
from Components.j00zekSunCalculations import Sun

DBG = False
if DBG: from Components.j00zekComponents import j00zekDEBUG

Position = {}
        
class j00zekSun(Converter, object):
    UNKNOWN = 0
    SUNSET = 1
    SUNRISE = 2

    def __init__(self, arg):
        Converter.__init__(self, arg)
        if DBG: j00zekDEBUG('[j00zekSun:__init__] >>> arg="%s"' % arg)
        global TWISTED, Position
        if arg in ('wschod', 'sunset'):
            self.type = self.SUNRISE
        elif arg in ('zachod', 'sunrise'):
            self.type = self.SUNSET
        else:
            self.type = self.UNKNOWN
        try:
            config.plugins.MSNweatherNP.currEntry.addNotifier(self.setLocation, initial_call=True) 
        except Exception as e:
            if DBG: j00zekDEBUG("[j00zekSun:__init__] >>> Exception: '%s'" % str(e))

    def setLocation(self, configElement = None): 
        global Position
        if DBG: j00zekDEBUG("[j00zekSun:setLocation]")
        try:
            currEntry = int(config.plugins.MSNweatherNP.currEntry.value)
            Position['latitude'] = float(config.plugins.MSNweatherNP.Entry[currEntry].geolatitude.value)
            Position['longitude'] = float(config.plugins.MSNweatherNP.Entry[currEntry].geolongitude.value)
        except Exception as e:
            if DBG: j00zekDEBUG("[j00zekSun:setLocation] >>> Exception: '%s'" % str(e))
        if DBG: j00zekDEBUG("[j00zekSun:setLocation] latitude='%s' , longitude='%s'" % (Position['latitude'],Position['longitude']))
   
    @cached
    def getText(self):
        global Position
        try:
            if self.type == self.SUNSET:
                retTXT = str(sun.getSunsetTime(Position['longitude'], Position['latitude'] )['TZtime'])
            elif self.type == self.SUNRISE:
                retTXT = str(sun.getSunriseTime( Position['longitude'], Position['latitude'] )['TZtime'])
            else:
                retTXT = "---"
        except Exception:
                retTXT = "-?-"
        if DBG: j00zekDEBUG('[j00zekSun:getText] retTXT="%s"' % retTXT)
        return str(retTXT)

    text = property(getText)
    
sun = Sun()