# -*- coding: utf-8 -*-
#
#    j00zekBlinkingClock
#
#    Coded by j00zek (c)2019-2020
#
#    Uszanuj moja prace i nie kasuj/zmieniaj informacji kto jest autorem konwertera
#    Please respect my work and don't delete/change name of the renderer author
#
#    Nie zgadzam sie na wykorzystywanie tego skryptu w projektach platnych jak np. Graterlia!!!
#
#    Prosze NIE dystrybuowac tego skryptu w formie archwum zip, czy tar.gz
#    Zgadzam sie jedynie na dystrybucje z repozytorium opkg
#    

from __future__ import absolute_import #zmiana strategii ladowanie modulow w py2 z relative na absolute jak w py3
from Components.Converter.Converter import Converter
from Components.config import config
from Components.Element import cached
from enigma import eTimer
from time import localtime, strftime

try:
    from boxbranding import getBoxType
except Exception:
    def getBoxType():
        return 'unknown'

DBG = False
if DBG: 
    try: from Components.j00zekComponents import j00zekDEBUG
    except Exception: DBG = False

class j00zekBlinkingClock(Converter, object):
    LEFT   = 0
    CENTER = 1
    RIGHT  = 2
    TVcfg  = 4
    VFDstdby = 5
    FMT = 6
    
    def __init__(self, type):
        Converter.__init__(self, type)
        self.BlinkTimer = eTimer()
        self.BlinkTimer.callback.append(self.blinkFunc)     
        self.BlinkTimer.start(1000)         
        self.CHAR = ":"
        if getBoxType() in ('ax51', 'vuduo', 'sf3038', 'sf4008', 'beyonwizu4', 'unknown'):
            self.VFDsize = 16
        else:
            self.VFDsize = 12
        if type == "clockVFDstdby":
            self.TYPE = self.VFDstdby
        else:
            self.TYPE = self.FMT
            self.fmt_string = type.replace('Format:','')
        if DBG: j00zekDEBUG('[j00zekBlinkingClock:__init__] type=%s, VFDsize = %s' % (type, self.VFDsize) ) 

    def blinkFunc(self):
        if self.CHAR == ":" and self.TYPE == self.VFDstdby:
            self.CHAR = " "
        else:
            self.CHAR = ":"
        
    def doSuspend(self, suspended): 
        if suspended == 1: 
            self.BlinkTimer.stop()
        else: 
            self.BlinkTimer.start(1000)
            
    @cached
    def getText(self):
        time = self.source.time
        if time is None:
            return ""
        t = localtime(time)
        position = int(config.plugins.j00zekCC.clockVFDpos.value)
        if self.TYPE == self.VFDstdby:
            self.fmt_string = config.plugins.j00zekCC.clockVFDstdby.value

        ClockText = strftime(self.fmt_string, t).replace('ą','a').replace('Ś','S').replace('ś','s').replace('ź','z')
        ClockTextLen = len(ClockText)
        if DBG: j00zekDEBUG('[j00zekBlinkingClock:getText] len(%s) = %s' % (ClockText, ClockTextLen) ) 
        
        if self.TYPE == self.VFDstdby and ClockTextLen <= self.VFDsize:
            ClockText = ClockText.replace(":", self.CHAR)
        if position == 2 or position == 3:
            Spaces = self.VFDsize - ClockTextLen
            if Spaces > 0:
                if position == 2: #center
                    ClockText = " " * int(Spaces/2) + ClockText
                elif position == 3: #right
                    ClockText = " " * Spaces + ClockText
        
        return ClockText

    text = property(getText)
