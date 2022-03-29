#######################################################################
#
#    Renderer for Enigma2
#    Coded by j00zek (c)2018
#
#    Uszanuj moja prace i nie kasuj/zmieniaj informacji kto jest autorem renderera
#    Please respect my work and don't delete/change name of the renderer author
#
#    Nie zgadzam sie na wykorzystywanie tego renderera w projektach platnych jak np. Graterlia!!!
#
# Prosze NIE dystrybuowac tego skryptu w formie archwum zip, czy tar.gz
# Zgadzam sie jedynie na dystrybucje z repozytorium opkg
#    

from __future__ import absolute_import #zmiana strategii ladowanie modulow w py2 z relative na absolute jak w py3
from Components.Renderer.Renderer import Renderer #ATV7.0,EGAMI10

from Components.config import config
from enigma import ePixmap, ePicLoad, eSize, iServiceInformation
from Tools.Directories import pathExists, SCOPE_SKIN_IMAGE, SCOPE_CURRENT_SKIN, resolveFilename
import os

DBG = False
try:
    if DBG: from Components.j00zekComponents import j00zekDEBUG
except Exception:
    DBG = False
    
class j00zekFrontEndIcon(Renderer):
   
    def __init__(self):
        Renderer.__init__(self)
        #self.picload = ePicLoad()
        self.iconPath = resolveFilename(SCOPE_CURRENT_SKIN, 'icons')
        self.currIcon = ''

    def applySkin(self, desktop, parent):
        attribs = self.skinAttributes[:]
        for attrib, value in self.skinAttributes:
            if attrib == 'iconspath':
                if value[:1] == '/':
                    self.iconPath = value
                else:
                    self.iconPath = resolveFilename(SCOPE_CURRENT_SKIN, value)
                attribs.remove((attrib, value))

        self.skinAttributes = attribs
        
        return Renderer.applySkin(self, desktop, parent)

    GUI_WIDGET = ePixmap

    def postWidgetCreate(self, instance):
        self.changed((self.CHANGED_DEFAULT,))

    def changed(self, what):
        if what[0] != self.CHANGED_CLEAR:
            if self.source:
                if self.instance:
                    service = self.source.service
                    info = service and service.info()
                    if info:
                        tmpIcon = ''
                        tpdata = info.getInfoObject(iServiceInformation.sTransponderData)
                        if tpdata:
                            if not service.streamed() is None:
                                tmpIcon = 'ico_iptv.png'
                            else:
                                if tpdata.get('system', 0) is 0:
                                    tmpIcon = 'ico_%s.png' % tpdata.get('tuner_type', '').lower()
                                else:
                                    tmpIcon = 'ico_%s2.png' % tpdata.get('tuner_type', '').lower()
                        
                        if tmpIcon != '':
                            tmpPathIcon = os.path.join(config.plugins.j00zekCC.AlternateUserIconsPath.value, tmpIcon)
                            if not pathExists(tmpPathIcon):
                                if DBG: j00zekDEBUG("[j00zekFrontEndIcon:changed] AlternateUserIconsPath='%s' does not exist" % tmpPathIcon)
                                tmpPathIcon = os.path.join(self.iconPath, tmpIcon)

                            if not pathExists(tmpPathIcon):
                                self.instance.hide()
                                if DBG: j00zekDEBUG("[j00zekFrontEndIcon:changed] Icon '%s' not found" % tmpPathIcon)
                            elif tmpIcon != self.currIcon:
                                if DBG: j00zekDEBUG("[j00zekFrontEndIcon:changed] displaying icon '%s'" % tmpPathIcon)
                                self.currIcon = tmpPathIcon
                                self.instance.setScale(1)
                                self.instance.setPixmapFromFile(self.currIcon)
                                self.instance.show()
                        else:
                          self.instance.hide()
                          if DBG: j00zekDEBUG("[j00zekFrontEndIcon:changed] Icon '%s' not found" % tmpPathIcon)
