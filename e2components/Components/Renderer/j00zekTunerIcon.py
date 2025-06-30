#######################################################################
#
#    Renderer for Enigma2
#    Coded by j00zek (c)2020
#
#    Uszanuj moja prace i nie kasuj/zmieniaj informacji kto jest autorem renderera
#    Please respect my work and don't delete/change name of the renderer author
#
#    Nie zgadzam sie na wykorzystywanie tego renderera w projektach platnych jak np. Graterlia!!!
#
# Prosze NIE dystrybuowac tego skryptu w formie archwum zip, czy tar.gz
# Zgadzam sie jedynie na dystrybucje z repozytorium opkg
#    
#    <widget source="session.CurrentService" render="j00zekTunerIcon" iconspath="/usr/share/enigma2/HomarLCDskins/Homar" position="10,15" size="480,320" zPosition="-1" alphatest="blend" /> 

from __future__ import absolute_import #zmiana strategii ladowanie modulow w py2 z relative na absolute jak w py3
from Components.Renderer.Renderer import Renderer #ATV7.0,EGAMI10
from Components.config import config
from enigma import ePixmap
from Tools.Directories import SCOPE_CURRENT_SKIN, resolveFilename
import os

    
class j00zekTunerIcon(Renderer):
   
    def __init__(self):
        Renderer.__init__(self)
        self.iconPath = resolveFilename(SCOPE_CURRENT_SKIN, 'icons')
        #tuner icon
        self.tunerIcon = 'unknown.png'
        if os.path.exists('/proc/stb/info/vumodel') and not os.path.exists('/proc/stb/info/boxtype'):
            with open('/proc/stb/info/vumodel', 'r') as file:
                self.tunerIcon = 'vu' + file.readline().strip().lower() + '.png'
                file.close()
        self.currIcon = os.path.join(self.iconPath, self.tunerIcon)

    def applySkin(self, desktop, parent):
        attribs = self.skinAttributes[:]
        for attrib, value in self.skinAttributes:
            if attrib == 'iconspath':
                if value[:1] == '/':
                    self.iconPath = value
                else:
                    self.iconPath = resolveFilename(SCOPE_CURRENT_SKIN, value)
                attribs.remove((attrib, value))
                
                self.currIcon = os.path.join(self.iconPath, self.tunerIcon)
                try: self.changed((self.CHANGED_DEFAULT,))
                except Exception: pass

        self.skinAttributes = attribs
        
        return Renderer.applySkin(self, desktop, parent)

    GUI_WIDGET = ePixmap

    def postWidgetCreate(self, instance):
        self.changed((self.CHANGED_DEFAULT,))

    def changed(self, what):
        if what[0] != self.CHANGED_CLEAR:
            if self.source:
                if self.instance:
                    self.instance.setPixmapFromFile(self.currIcon)
                    self.instance.show()
