from Components.Renderer.Renderer import Renderer
from Tools.LoadPixmap import LoadPixmap
from Tools.Directories import SCOPE_SKIN_IMAGE, SCOPE_CURRENT_SKIN, fileExists, resolveFilename
from enigma import ePixmap, eTimer
from Components.config import config
import os
from Plugins.Extensions.DGWeather.components.utils import *

DBG = False

class dgWeatherAnimatedWeather(Renderer):
    def __init__(self):
        if DBG: write_log('Renderer.dgWeatherAnimatedWeather().__init__() >>>')
        Renderer.__init__(self)
        self.path = '/usr/lib/enigma2/python/Plugins/Extensions/DGWeather/weather/AnimatedWeatherPixmap'
        self.pixdelay = 100
        self.control = 1
        self.ftpcontrol = 0
        self.slideicon = None
        self.txt_naim = {'1':  '0',
                         '2':  '0',
                         '3':  '0',
                         '4':  '0',
                         '9':  '8',
                         '16': '14',
                         '17': '0',
                         '24': '23',
                         '25': '44',
                         '29': '27',
                         '30': '28',
                         '33': '27',
                         '34': '28',
                         '35': '0',
                         '38': '37',
                         '40': '18',
                         '42': '14',
                         '43': '14',
                        }
        return

    def applySkin(self, desktop, parent):
        attribs = []
        for attrib, value in self.skinAttributes:
            if attrib == 'path':
                self.path = value
            elif attrib == 'pixdelay':
                self.pixdelay = int(value)
            elif attrib == 'ftpcontrol':
                self.ftpcontrol = int(value)
            elif attrib == 'control':
                self.control = int(value)
            else:
                attribs.append((attrib, value))

        self.skinAttributes = attribs
        return Renderer.applySkin(self, desktop, parent)

    GUI_WIDGET = ePixmap

    def changed(self, what):
        if what[0] == self.CHANGED_CLEAR:
            if DBG: write_log('Renderer.dgWeatherAnimatedWeather().changed(self.CHANGED_CLEAR)')
        else:
            if self.instance:
                if DBG: write_log('Renderer.dgWeatherAnimatedWeather().changed() self.instance')
                sname = self.source.iconfilename
                name = self.txt_naim.get(sname, sname)
                if DBG: write_log('Renderer.dgWeatherAnimatedWeather().changed() name = "%s"' % name)
                self.runAnim(name)

    def runAnim(self, id):
        global total
        animokicon = False
        if fileExists('%s/%s' % (self.path, id)):
            if DBG: write_log('Renderer.dgWeatherAnimatedWeather().runAnim() fileExists(%s/%s)' % (self.path, id))
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
                if DBG: write_log('Renderer.dgWeatherAnimatedWeather().runAnim() self.picsicon.append(%s%s.png)' % (pathanimicon, str(x)))

            self.timericon = eTimer()
            self.timericon.callback.append(self.timerEvent)
            self.timericon.start(100, True)

    def timerEvent(self):
        if self.slideicon == 0:
            self.slideicon = total
        self.timericon.stop()
        self.instance.setScale(1)
        try:
            self.instance.setPixmap(self.picsicon[self.slideicon - 1])
        except:
            Exc_log()

        self.slideicon = self.slideicon - 1
        self.timericon.start(self.pixdelay, True)