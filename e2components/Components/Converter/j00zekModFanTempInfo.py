# BlackHarmonyFanTempInfo Converter  v.0.4
#

from __future__ import absolute_import #zmiana strategii ladowanie modulow w py2 z relative na absolute jak w py3
from Components.Converter.Poll import Poll
from Components.Converter.Converter import Converter
from Components.Language import language
from Components.Element import cached
from Tools.Directories import fileExists

DBG = False
try:
    if DBG: from Components.j00zekComponents import j00zekDEBUG
except Exception:
    DBG = False 
    
class j00zekModFanTempInfo(Poll, Converter, object):
    FanInfo = 0
    TempInfo = 1
    TempInfoHeader = 3
    FanInfoHeader = 4
    
    def __init__(self, type):
        Converter.__init__(self, type)
        Poll.__init__(self)
        if type == "FanInfo":
            self.type = self.FanInfo
        elif type == "FanInfoHeader":
            self.type = self.FanInfoHeader
        elif type == "TempInfo":
            self.type = self.TempInfo
        elif type == "TempInfoHeader":
            self.type = self.TempInfoHeader
        self.poll_interval = 2000
        self.poll_enabled = True
        
        if fileExists("/proc/stb/fp/fan_speed"):
            self.FanHeader = 'FAN:'
        else:
            self.FanHeader = ''
            
        self.TempPath = ''
        self.TempHeader = ''
        self.TempUnit = 'C'
        for myPath in ( '/proc/stb/sensors/temp0/value',
                        '/sys/devices/virtual/thermal/thermal_zone0/temp',
                        '/proc/stb/fp/temp_sensor',
                        '/proc/stb/fp/temp_sensor_avs'):
            if fileExists(myPath):
                try:
                    open(myPath).read() #check if it can be read
                    self.TempPath = myPath
                except Exception as e:
                    if DBG: j00zekDEBUG("[BlackHarmonyFanTempInfo:__init__] Exception '%s'" % str(e))
                break
        
        if self.TempPath != '': self.TempHeader = 'TMP:'
        else: self.poll_enabled = False
        if DBG: j00zekDEBUG("[BlackHarmonyFanTempInfo:__init__]TempPath='%s', TempHeader='%s', FanHeader='%s'" % (self.TempPath, self.TempHeader, self.FanHeader))
        
    @cached
    def getText(self):
        if language.getLanguage()[:2] == 'pl': retText = 'Brak sensora'
        else: retText = _('No sensor')
        try:
            if self.type == self.FanInfoHeader:
                    retText = self.FanHeader
            elif self.type == self.FanInfo and self.FanHeader != '':
                retText = open("/proc/stb/fp/fan_speed").read().strip('\n')
            elif self.type == self.TempInfoHeader:
                    retText = self.TempHeader
            elif self.type == self.TempInfo and self.TempHeader != '':
                retText = "%s%s%s" % (open(self.TempPath).read().strip()[:2], unichr(176).encode("latin-1"), self.TempUnit )
            if DBG: j00zekDEBUG("[BlackHarmonyFanTempInfo:getText] type(%s)='%s'" % (self.type,retText))
        except Exception as e:
            if DBG: j00zekDEBUG("[BlackHarmonyFanTempInfo:getText] Exception '%s' for type(%s)" % (str(e),self.type))
        return retText
    
    text = property(getText)
    
    def changed(self, what):
        if what[0] == self.CHANGED_POLL:
            self.downstream_elements.changed(what)
            
    def doSuspend(self, suspended): 
        if suspended: 
            self.poll_enabled = False 
        elif self.TempHeader != '': 
            self.poll_enabled = True 
