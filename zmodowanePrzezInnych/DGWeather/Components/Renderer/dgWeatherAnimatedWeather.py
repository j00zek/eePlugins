# Embedded file name: /usr/lib/enigma2/python/Components/Renderer/darkAnimatedWeather.py
from Components.Renderer.Renderer import Renderer
from Tools.LoadPixmap import LoadPixmap
from Tools.Directories import SCOPE_SKIN_IMAGE, SCOPE_CURRENT_SKIN, fileExists, resolveFilename
from enigma import ePixmap, eTimer
from Components.config import config
import os
# >>> musismy ladowac z pelnej sciezki bo konwerter jet uruchamany z innego kataouog mimo ze jest tutaj
from Plugins.Extensions.DGWeather.components.utils import *

class dgWeatherAnimatedWeather(Renderer):
    __module__ = __name__

    def __init__(self):
        write_log('Renderer.dgWeatherAnimatedWeather().__init__() >>>')
        Renderer.__init__(self)
        self.path = '/usr/lib/enigma2/python/Plugins/Extensions/DGWeather/weather/AnimatedWeatherPixmap'
        self.pixdelay = 100
        self.control = 1
        self.ftpcontrol = 0
        self.slideicon = None
        self.txt_naim = {'17': '0',
         '35': '0',
         '16': '14',
         '42': '14',
         '43': '14',
         '40': '18',
         '24': '23',
         '29': '27',
         '33': '27',
         '30': '28',
         '34': '28',
         '38': '37',
         '25': '44'}
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
        #write_log('Renderer.dgWeatherAnimatedWeather().changed() >>>')
        if self.instance:
            sname = ''
            ext = ''
            name = ''
            if what[0] != self.CHANGED_CLEAR:
                try:
                    ext = self.source.iconfilename
                    if ext != '':
                        sname = os.path.split(ext)[1]
                        sname = sname.replace('.gif', '')
                except:
                    sname = self.source.text

            if sname == '1' or sname == '2' or sname == '3' or sname == '4':
                name = '0'
            elif sname == '9':
                name = '8'
            else:
                name = self.txt_naim.get(sname, sname)
            write_log('Renderer.dgWeatherAnimatedWeather().changed() name = "%s"' % name)
            self.runAnim(name)

    def runAnim(self, id):
        global total
        animokicon = False
        if fileExists('%s/%s' % (self.path, id)):
            pathanimicon = '%s/%s/a' % (self.path, id)
            path = '%s/%s' % (self.path, id)
            dir_work = os.listdir(path)
            if config.plugins.visual.animatedWeather.value == 'animated':
                total = len(dir_work)
            else:
                total = 1
            self.slideicon = total
            animokicon = True
        elif fileExists('%s/NA' % self.path):
            pathanimicon = '%s/NA/a' % self.path
            path = '%s/NA' % self.path
            dir_work = os.listdir(path)
            if config.plugins.visual.animatedWeather.value == 'animated':
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
            self.timericon.start(100, True)

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