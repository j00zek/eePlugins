# -*- coding: utf-8 -*-
#
#  j00zekModRollerCharVFD based on ModRollerCharVFD
#
# j00zek: this file has changed name just to avoid errors using opkg (situation when file was installed by different package)
# it also contains changes to correctly use it in other than ATV images
#

from __future__ import absolute_import #zmiana strategii ladowanie modulow w py2 z relative na absolute jak w py3
from Components.Renderer.Renderer import Renderer #ATV7.0,EGAMI10
from Components.config import config
from Components.VariableText import VariableText
from enigma import eLabel, eTimer

try:
    from boxbranding import getBoxType
except Exception:
    def getBoxType():
        return 'unknown'

class j00zekModRollerCharVFD(VariableText, Renderer):

    def __init__(self):
        Renderer.__init__(self)
        VariableText.__init__(self)
        self.moveTimerText = None
        self.delayTimer = None
        if getBoxType() in ('ax51', 'vuduo', 'sf3038', 'sf4008', 'beyonwizu4', 'unknown'):
            self.stringlength = 16
        else:
            self.stringlength = 12
        return

    GUI_WIDGET = eLabel

    def connect(self, source):
        Renderer.connect(self, source)
        self.changed((self.CHANGED_DEFAULT,))

    def changed(self, what):
        if what[0] == self.CHANGED_CLEAR:
            if self.moveTimerText:
                self.moveTimerText.stop()
            if self.delayTimer:
                self.delayTimer.stop()
            self.text = ''
        else:
            self.text = self.source.text
            self.text = self.text.replace('ą','a').replace('ć','c').replace('ę','e').replace('ł','l').replace('ń','n').replace('ó','o').replace('ś','s').replace('ź','z').replace('ż','z')
            self.text = self.text.replace('Ą','A').replace('Ć','C').replace('Ę','E').replace('Ł','L').replace('Ń','N').replace('Ó','O').replace('Ś','S').replace('Ź','Z').replace('Ż','Z')
        if len(self.text) > self.stringlength:
            self.text = self.text + ' ' * self.stringlength + self.text[:self.stringlength + 1]
            self.x = len(self.text) - self.stringlength
            self.idx = 0
            self.backtext = self.text
            self.status = 'start'
            self.moveTimerText = eTimer()
            self.moveTimerText.timeout.get().append(self.moveTimerTextRun)
            self.moveTimerText.start(2000)
        else:
            self.x = len(self.text)
            self.idx = 0
            self.backtext = self.text

    def moveTimerTextRun(self):
        self.moveTimerText.stop()
        try: #exists on openATV only
            self.scrollspeed = int(config.lcd.scroll_speed.value)
            self.delayvalue = config.lcd.scroll_delay.value
        except Exception:
            self.scrollspeed = int(config.j00zekCC.scroll_speed.value)
            self.delayvalue = config.j00zekCC.scroll_delay.value
            
        if self.x > 0:
            txttmp = self.backtext[self.idx:]
            self.text = txttmp[:self.stringlength]
            str_length = 1
            accents = self.text[:2]
            if accents in ('\xc3\xbc', '\xc3\xa4', '\xc3\xb6', '\xc3\x84', '\xc3\x9c', '\xc3\x96', '\xc3\x9f'):
                str_length = 2
            self.idx = self.idx + str_length
            self.x = self.x - str_length
        if self.x == 0:
            self.status = 'end'
            self.text = self.backtext
        if self.status != 'end':
            self.moveTimerText.start(self.scrollspeed)
        if self.delayvalue != 'noscrolling':
            self.scrolldelay = int(self.delayvalue)
            self.delayTimer = eTimer()
            self.delayTimer.timeout.get().append(self.delayTimergo)
            self.delayTimer.start(self.scrolldelay)

    def delayTimergo(self):
        self.delayTimer.stop()
        self.changed((self.CHANGED_DEFAULT,))