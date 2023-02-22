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

DBG = True
if DBG: from Components.j00zekComponents import j00zekDEBUG

class j00zekRefreshBingPicOfTheDay(Converter, object):
    def __init__(self, arg):
        Converter.__init__(self, arg)
        if DBG: j00zekDEBUG('j00zekRefreshBingPicOfTheDay(Converter).__init__ >>>')
        self.AlternatePicPath = str(arg)
        self.BingPic = self.AlternatePicPath.replace('.png','-Bing.png').replace('.jpg','-Bing.jpg')
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
        if self.AlternatePicPath == '':
            cmd = '/usr/bin/python /usr/lib/enigma2/python/Components/j00zekBING.py'
        else:
            cmd = '/usr/bin/python /usr/lib/enigma2/python/Components/j00zekBING.py "mergePic=%s"' % self.AlternatePicPath
        if DBG: j00zekDEBUG('j00zekRefreshBingPicOfTheDay(Converter).__init__  > Console().ePopen(%s)' % cmd)
        with open("/proc/sys/vm/drop_caches", "w") as f: f.write("1\n")
        Console().ePopen(cmd)
        
    @cached
    def getText(self):
        if DBG: j00zekDEBUG("j00zekRefreshBingPicOfTheDay(Converter).getText j00zekCC.PiPbackground.value == '%s', AlternatePicPath='%s', BingPic='%s'" % (config.plugins.j00zekCC.PiPbackground.value,self.AlternatePicPath,self.BingPic))
        if config.plugins.j00zekCC.PiPbackground.value == 'n' or not os.path.exists(self.BingPic):
            return self.AlternatePicPath
        else:
            return self.BingPic

    text = property(getText)
