#
# j00zek 2018-2023
#
from __future__ import absolute_import #zmiana strategii ladowanie modulow w py2 z relative na absolute jak w py3
from Components.Converter.Converter import Converter
from enigma import eTimer
from Components.Element import cached
from Components.config import config
from Components.Console import Console
import os

DBG = False
if DBG: from Components.j00zekComponents import j00zekDEBUG

class j00zekRefreshBingPicOfTheDay(Converter, object):
    def __init__(self, arg):
        Converter.__init__(self, arg)
        if DBG: j00zekDEBUG('j00zekRefreshBingPicOfTheDay(Converter).__init__ >>>')
        self.AlternatePicPath = arg
        self.BingPic = '/usr/share/enigma2/BlackHarmony/icons/BingPicOfTheDay.jpg'
        self.Init = True
        self.checkTimer = eTimer()
        self.checkTimer.callback.append(self.refreshPic)
        self.checkTimer.start(10000, True)

    def refreshPic(self):
        if DBG: j00zekDEBUG('j00zekRefreshBingPicOfTheDay(Converter).refreshPic >>>')
        if self.Init == True:
            self.checkTimer.stop()
            self.Init = False
            self.checkTimer.start(86400000) #check once a day 86400000 = 1000ms * 60 * 60 * 24
        with open("/proc/sys/vm/drop_caches", "w") as f: f.write("1\n")
        Console().ePopen('/usr/bin/python /usr/lib/enigma2/python/Components/j00zekBING.py')
        
    @cached
    def getText(self):
        if config.plugins.j00zekCC.PiPbackground.value == 'n':
            return '/usr/share/enigma2/BlackHarmony/bg_design/bg_pure_black_1920x1080.png'
        elif config.plugins.j00zekCC.PiPbackground.value == 'b' and os.path.exists(self.BingPic):
            return self.BingPic
        else:
            return self.AlternatePicPath
        
    text = property(getText)
