# j00zek: this file has changed name just to avoid errors using opkg (situation when file was installed by different pockage)
#
from __future__ import absolute_import #zmiana strategii ladowanie modulow w py2 z relative na absolute jak w py3

from Tools.LoadPixmap import LoadPixmap
from Components.Pixmap import Pixmap

from Components.Renderer.Renderer import Renderer #ATV7.0,EGAMI10
    
from enigma import ePixmap, eTimer
from Tools.Directories import fileExists, SCOPE_SKIN_IMAGE, SCOPE_CURRENT_SKIN, resolveFilename
from Components.config import config
from Components.Converter.Poll import Poll
import os

class j00zekModAnimatedPicsmap(Renderer, Poll):
    __module__ = __name__

    def __init__(self):
        Poll.__init__(self)
        Renderer.__init__(self)
        self.pngname = ''
        self.pixmaps = 'picon'
        self.pixdelay = 300
        self.control = 0
        self.count = 5
        self.pics = []

    def applySkin(self, desktop, parent):
        attribs = []
        for attrib, value in self.skinAttributes:
            if attrib == 'pixmaps':
                self.pixmaps = value
            elif attrib == 'pixdelay':
                self.pixdelay = int(value)
            elif attrib == 'count':
                self.count = int(value)
            elif attrib == 'control':
                self.control = int(value)
            else:
                attribs.append((attrib, value))

        self.skinAttributes = attribs
        return Renderer.applySkin(self, desktop, parent)

    GUI_WIDGET = ePixmap

    def changed(self, what):
        self.poll_interval = 2000
        self.poll_enabled = True
        if self.instance:
            pngname = ''
            if what[0] != self.CHANGED_CLEAR:
                self.runAnim()

    def runAnim(self):
        wai = resolveFilename(SCOPE_SKIN_IMAGE, self.pixmaps)
        anim = False
        if fileExists('%s' % wai):
            pathanimicon = '%s/a' % wai
            anim = True
        else:
            pathanimicon = '/usr/share/enigma2/skin_default/spinner/wait'
            anim = True
        if anim == True:
            self.slideicon = self.count
            self.picsicon = []
            for x in range(self.slideicon):
                self.picsicon.append(LoadPixmap(pathanimicon + str(x) + '.png'))

            self.timer = eTimer()
            self.timer.callback.append(self.timerEvent)
            self.timer.start(self.pixdelay, True)

    def timerEvent(self):
        if self.control > 0:
            if self.slideicon == 0:
                self.slideicon = self.count
            self.timer.stop()
            self.instance.setPixmap(self.picsicon[self.slideicon - 1])
            self.slideicon = self.slideicon - 1
            self.timer.start(self.pixdelay, True)
        elif self.control == 0:
            if self.slideicon > 0:
                self.timer.stop()
                self.instance.setPixmap(self.picsicon[self.slideicon - 1])
                self.slideicon = self.slideicon - 1
                self.timer.start(self.pixdelay, True)
            else:
                self.timer.stop()
        else:
            self.timer.stop()