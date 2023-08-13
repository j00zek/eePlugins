# -*- coding: utf-8 -*-
#
# j00zek 2018-2022
#
from __future__ import absolute_import #zmiana strategii ladowanie modulow w py2 z relative na absolute jak w py3
from Components.Converter.Converter import Converter
from Components.Element import cached
from Components.j00zekMoonCalculations import phase, get_julian_datetime, phase_string
from Components.Language import language
#from decimal import Decimal as dec
import math, datetime

DBG = False
if DBG: from Components.j00zekComponents import j00zekDEBUG

#simple and dirty translation
if language.getLanguage() == 'pl_PL':
    MoonPhasesDict = {  "New Moon": "Nów", "Waxing Crescent": "Sierp przybywający", "First Quarter": "I kwadra",
                        "Waxing Gibbous": "Przybywający księżyc garbaty", "Full Moon": "Pełnia",
                        "Waning Gibbous": "Ubywający księżyc garbaty", "Last Quarter": "III kwadra",
                        "Waning Crescent": "Sierp ubywający"}
else:
    MoonPhasesDict = { "New Moon": "New Moon", "Waxing Crescent": "Waxing Crescent", "First Quarter": "First Quarter",
                        "Waxing Gibbous": "Waxing Gibbous", "Full Moon": "Full Moon",
                        "Waning Gibbous": "Waning Gibbous", "Last Quarter": "Last Quarter",
                        "Waning Crescent": "Waning Crescent"}


class j00zekMoon(Converter, object):
    PHASE = 0
    ICON = 1
    LUMINATION = 2
    LUMINATION3 = 3
    
    def __init__(self, arg):
        Converter.__init__(self, arg)
        if DBG: j00zekDEBUG('[j00zekMoon:__init__] >>> arg="%s"' % arg)
        if arg in ('faza', 'phase'):
            self.type = self.PHASE
        elif arg in ('obraz', 'icon'):
            self.type = self.ICON
        elif arg in ('lumination', 'oswietlenie'):
            self.type = self.LUMINATION
        elif arg in ('lumination3', 'oswietlenie3'):
            self.type = self.LUMINATION3
        else:
            self.type = 'unknown'
            
    def myRound(self, x, base=5):
        return int(base * round(float(x)/base))
        
    @cached
    def getText(self):
        phaseDict = phase(get_julian_datetime(datetime.datetime.now()))
        if self.type == self.PHASE:
            retTXT = MoonPhasesDict[phase_string(phaseDict['phase'])]
            if DBG: j00zekDEBUG("[j00zekMoon:getText] currentPhase: %s" % (retTXT))
        elif self.type == self.ICON:
            retTXT = self.myRound(phaseDict['phase'] * 100, 5)
            if DBG: j00zekDEBUG("[j00zekMoon:getText] phaseIcon: %s" % (retTXT))
        elif self.type == self.LUMINATION:
            retTXT = phaseDict['illuminated'] * 100
            retTXT = str(round(retTXT,1)) + '%'
            if DBG: j00zekDEBUG("[j00zekMoon:getText] moon Lumination: %s" % (retTXT))
        elif self.type == self.LUMINATION3:
            retTXT = phaseDict['illuminated'] * 100
            retTXT = str(round(retTXT,3)) + '%'
            if DBG: j00zekDEBUG("[j00zekMoon:getText] moon Lumination3: %s" % (retTXT))
        else:
            if DBG: j00zekDEBUG("[j00zekMoon:getText] Unknown type requested")
            retTXT = "---"
        return str(retTXT)

    @cached
    def getIconFilename(self):
        phaseDict = phase(get_julian_datetime(datetime.datetime.now()))
        retTXT = self.myRound(phaseDict['phase'] * 100, 5)
        if DBG: j00zekDEBUG("[j00zekMoon:getIconFilename] phaseIcon: %s" % (retTXT))
        return '%s.png' % str(retTXT)

    text = property(getText)
    iconfilename = property(getIconFilename)