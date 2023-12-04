# Embedded file name: /usr/lib/enigma2/python/Components/Renderer/darkAnimatedMoon.py
from Tools.LoadPixmap import LoadPixmap
from Components.Renderer.Renderer import Renderer
from enigma import ePixmap, eTimer
from Tools.Directories import fileExists
from Components.config import config
import os
from Plugins.Extensions.DGWeather.components.utils import *

DBG = True

class dgWeatherAnimatedMoon(Renderer):
    def __init__(self):
        if DBG: write_log('Renderer.dgWeatherAnimatedMoon().__init__() >>>')
        Renderer.__init__(self)
        self.path = '/usr/lib/enigma2/python/Plugins/Extensions/DGWeather/weather/animatedmoon'
        self.pixdelay = 350
        self.control = 1
        self.slideicon = None
        return

    def applySkin(self, desktop, parent):
        attribs = []
        for attrib, value in self.skinAttributes:
            if attrib == 'path':
                self.path = value
            elif attrib == 'pixdelay':
                self.pixdelay = int(value)
            elif attrib == 'control':
                self.control = int(value)
            else:
                attribs.append((attrib, value))

        self.skinAttributes = attribs
        return Renderer.applySkin(self, desktop, parent)

    GUI_WIDGET = ePixmap

    def changed(self, what):
        if DBG: write_log('Renderer.dgWeatherAnimatedMoon().changed() >>>')
        if self.instance:
            if what[0] != self.CHANGED_CLEAR:
                sname = self.source.iconfilename
                if DBG: write_log('Renderer.dgWeatherAnimatedMoon().changed() sname = "%s"' % sname)
                self.runAnim(sname)

    def runAnim(self, id):
        global total
        animokicon = False
        if fileExists('%s/%s' % (self.path, id)):
            pathanimicon = '%s/%s/a' % (self.path, id)
            path = '%s/%s' % (self.path, id)
            dir_work = os.listdir(path)
            if config.plugins.dgWeather.animatedWeather.value == 'animated':
                total = len(dir_work)
            else:
                total = 1
            self.slideicon = total
            animokicon = True
        elif fileExists('%s/NA' % self.path):
            pathanimicon = '%s/NA/a' % self.path
            path = '%s/NA' % self.path
            dir_work = os.listdir(path)
            if config.plugins.dgWeather.animatedWeather.value == 'animated':
                total = len(dir_work)
            else:
                total = 1
            self.slideicon = total
            animokicon = True
        if animokicon == True:
            self.picsicon = []
            for x in range(self.slideicon):
                self.picsicon.append(LoadPixmap(pathanimicon + str(x) + '.png'))

            self.timericon = eTimer()
            self.timericon.callback.append(self.timerEvent)
            self.timericon.start(400, True)

    def timerEvent(self):
        if self.slideicon == 0:
            self.slideicon = total
        self.timericon.stop()
        self.instance.setScale(1)
        try:
            self.instance.setPixmap(self.picsicon[self.slideicon - 1])
        except:
            pass

        self.slideicon = self.slideicon - 1
        self.timericon.start(self.pixdelay, True)