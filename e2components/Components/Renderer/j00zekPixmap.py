# -*- coding: utf-8 -*-
#

from __future__ import absolute_import #zmiana strategii ladowanie modulow w py2 z relative na absolute jak w py3
from Components.Renderer.Renderer import Renderer #ATV7.0,EGAMI10
from enigma import ePixmap
from Components.AVSwitch import AVSwitch
from Components.config import config
from Tools.Directories import resolveFilename
try:
    from Tools.Directories import SCOPE_CURRENT_SKIN
except Exception:
    from Tools.Directories import SCOPE_ACTIVE_SKIN as SCOPE_CURRENT_SKIN
 
from enigma import eEnv, ePicLoad, eRect, eSize, gPixmapPtr

DBG = False
try:
    if DBG: from Components.j00zekComponents import j00zekDEBUG
except Exception:
    DBG = False

class j00zekPixmap(Renderer):
    def __init__(self):
        Renderer.__init__(self)
        self.picload = ePicLoad()
        self.picload.PictureData.get().append(self.paintIconPixmapCB)
        self.iconFileName = ""
        self.iconPath = ""
        self.currIcon = ''

    GUI_WIDGET = ePixmap

    def postWidgetCreate(self, instance):
        for (attrib, value) in self.skinAttributes:
            if attrib == "size":
                x, y = value.split(',')
                self._scaleSize = eSize(int(x), int(y))
            elif attrib == "pixmap":
                if attrib.endswith('/*'):
                    if attrib.startswith('/'):
                        self.iconFileName = resolveFilename(SCOPE_CURRENT_SKIN, attrib[:-1])
                    else:
                        self.iconPath = attrib[:-1]
                else:
                    self.iconFileName = value
                    if not self.iconFileName.startswith('/'):
                        self.iconFileName = resolveFilename(SCOPE_CURRENT_SKIN, self.iconFileName)
        sc = AVSwitch().getFramebufferScale()
        self._aspectRatio = eSize(sc[0], sc[1])
        self.picload.setPara((self._scaleSize.width(), self._scaleSize.height(), sc[0], sc[1], True, 2, '#ff000000'))
        
    def disconnectAll(self):
        self.picload.PictureData.get().remove(self.paintIconPixmapCB)
        self.picload = None
        Renderer.disconnectAll(self)
        
    def paintIconPixmapCB(self, picInfo=None):
        ptr = self.picload.getData()
        if ptr is not None:
            pic_scale_size = eSize()
            # To be added in the future:
            if 'scale' in eSize.__dict__ and self._scaleSize.isValid() and self._aspectRatio.isValid():
                pic_scale_size = ptr.size().scale(self._scaleSize, self._aspectRatio)
            # To be removed in the future:
            elif 'scaleSize' in gPixmapPtr.__dict__:
                pic_scale_size = ptr.scaleSize()
            if pic_scale_size.isValid():
                pic_scale_width = pic_scale_size.width()
                pic_scale_height = pic_scale_size.height()
                dest_rect = eRect(0, 0, pic_scale_width, pic_scale_height)
                self.instance.setScale(1)
                self.instance.setScaleDest(dest_rect)
            else:
                self.instance.setScale(0)
            self.instance.setPixmap(ptr)
        else:
            self.instance.setPixmap(None)
        
    def doSuspend(self, suspended):
        if suspended:
            self.changed((self.CHANGED_CLEAR,))
        else:
            self.changed((self.CHANGED_DEFAULT,))
            
    def changed(self, what):
        if what[0] != self.CHANGED_CLEAR:
            if self.instance:
                if self.iconFileName == "":
                    if DBG: j00zekDEBUG("[j00zekPixmap:changed] dynamic mode, self.source.text='%s'" % str(self.source.text))
                    if self.source.text is not None and self.source.text != '':
                        if self.source.text.startswith('/'):
                            self.picload.startDecode(self.source.text)
                        else:
                            self.picload.startDecode(resolveFilename(SCOPE_CURRENT_SKIN, self.source.text))
                    else:
                        self.instance.setPixmap(None)
                else:
                    self.picload.startDecode(self.iconFileName)
