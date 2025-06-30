# renderer for Video resolution icons @j00zek 2017
# purpose:
#       -smaller and more ellegant xml
#       -should work quicker as no multiple checks necessary
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
except Exception: DBG = False
    
class j00zekVideoResolutionIcon(Renderer):
   
    def __init__(self):
        Renderer.__init__(self)
        #self.picload = ePicLoad()
        self.iconPath = resolveFilename(SCOPE_CURRENT_SKIN, 'icons')
        self.iconUHD = 'ico_uhd_on.png'
        self.iconHD = 'ico_hd_on_1080.png'
        self.iconHDready = 'ico_hd_on_720.png'
        self.icon960 = 'ico_hd_on_960.png'
        self.iconSD = 'ico_sd_on_576.png'
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
                        x = info.getInfo(iServiceInformation.sVideoWidth)
                        y = info.getInfo(iServiceInformation.sVideoHeight)
                        if x > 1920 and y > 1080:
                            tmpIcon = self.iconUHD      #UHD - 3840x2160
                        elif x > 1280 and y > 720:
                            tmpIcon = self.iconHD       #HD  - 1920x1080
                        elif x == 960 and y == 540: 
                            tmpIcon = self.icon960      #        960x540
                        elif x > 720 and y > 576:
                            tmpIcon = self.iconHDready #HDready - 1280x720
                        elif x > 0 and y > 0:
                            tmpIcon = self.iconSD       #SD - 720 x 576 / 768 x 576 / 720 x 480

                        if tmpIcon != '':
                            tmpPathIcon = os.path.join(config.plugins.j00zekCC.AlternateUserIconsPath.value, tmpIcon)
                            if not pathExists(tmpPathIcon):
                                if DBG: j00zekDEBUG("[j00zekVRicon:changed] AlternateUserIconsPath='%s' does not exist" % tmpPathIcon)
                                tmpPathIcon = os.path.join(self.iconPath, tmpIcon)

                            if not pathExists(tmpPathIcon):
                                self.instance.hide()
                                if DBG: j00zekDEBUG("[j00zekVRicon:changed] Icon '%s' not found" % tmpPathIcon)
                            elif tmpIcon != self.currIcon:
                                if DBG: j00zekDEBUG("[j00zekVRicon:changed] displaying icon '%s'" % tmpPathIcon)
                                self.currIcon = tmpPathIcon
                                self.instance.setScale(1)
                                self.instance.setPixmapFromFile(self.currIcon)
                                self.instance.show()
                        else:
                          self.instance.hide()
                          if DBG: j00zekDEBUG("[j00zekVRicon:changed] Icon '%s' not found" % tmpPathIcon)
