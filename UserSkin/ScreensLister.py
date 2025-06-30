# -*- coding: utf-8 -*-
from __future__ import absolute_import #zmiana strategii ladowanie modulow w py2 z relative na absolute jak w py3
from Plugins.Extensions.UserSkin.inits import *
from Plugins.Extensions.UserSkin.translate import _

from Components.Label import Label
from Components.Sources.List import List

from Screens.Screen import Screen
from enigma import getDesktop, gFont, RT_HALIGN_LEFT, RT_HALIGN_RIGHT, RT_HALIGN_CENTER, RT_VALIGN_CENTER
from Tools.LoadPixmap import LoadPixmap
from Tools.Directories import fileExists, resolveFilename, SCOPE_SKIN
from Components.ActionMap import ActionMap
from Components.MenuList import MenuList
import skin #we use dom_screens

class ScreensLister(Screen):
    skin = """
<screen name="ScreensLister" position="center,center" size="960,655">
    <widget name="ScreenName" position="35,0" size="790,25" zPosition="10" font="Regular;21" noWrap="1" halign="left" valign="center" transparent="1"/>
    <widget name="ScreenSource" position="35,0" size="790,25" zPosition="10" font="Regular;21" noWrap="1" halign="right" valign="center" transparent="1"/>
    <widget source="list" render="Listbox" position="0,30" size="950,590" scrollbarMode="showOnDemand">
        <convert type="TemplatedMultiContent">
            {"template": [
                MultiContentEntryPixmapAlphaTest(pos = (12, 2), size = (40, 40), png = 1),
                MultiContentEntryText(pos = (58, 2), size = (865, 40), font=0, flags = RT_HALIGN_LEFT|RT_VALIGN_CENTER, text = 0),
                MultiContentEntryText(pos = (58, 2), size = (865, 40), font=0, flags = RT_HALIGN_RIGHT|RT_VALIGN_CENTER, text = 2),
                ],
                "fonts": [gFont("Regular", 24)],
                "itemHeight": 44
            }
        </convert>
    </widget>
    <widget name="FooterText" position="35,630" size="890,25" zPosition="10" font="Regular;21" noWrap="1" halign="center" valign="center" transparent="1"/>
</screen>"""

    def __init__(self, session):
        Screen.__init__(self, session)
        #self.setup_title = _("ScreensLister")
        #Screen.setTitle(self, self.setup_title)
        self["list"] = List()
        self["setupActions"] = ActionMap(["SetupActions", "MenuActions"],
        {
            "cancel": self.quit,
            "ok": self.openSelected,
            "menu": self.quit,
        }, -2)
        self.setTitle(_("Loaded screens %s") % UserSkinInfo)
        self["list"].list = []
        self['ScreenName'] = Label(_("Screen"))
        self['ScreenSource'] = Label(_("Source"))
        self['FooterText'] = Label(_("NOTE: System uses definition from plugin when screen is not listed above."))
        self.onLayoutFinish.append(self.createsetup)

    def createsetup(self):
        l = []
        for key, value in skin.dom_screens.iteritems():
            print(key, value)
            sourceName = value[1].replace(resolveFilename(SCOPE_SKIN, ''),'')
            if sourceName == '' and key.lower().endswith('summary'):
                pic = 'lcd.png'
                sourceName = _('default skin_display.xml')
            elif sourceName == '':
                pic = 'config.png'
                sourceName = _('default skin.xml')
            elif key.lower().find('summary') != -1:
                pic = 'lcd.png'
                sourceName += 'skin.xml'
            else:
                pic = 'import.png'
                sourceName += 'skin.xml'
            l.append(self.buildListEntry(key , pic , sourceName))
            
        l.sort()
        self["list"].list = l

    def buildListEntry(self, description, image, optionname):
        pixmap = LoadPixmap(getPixmapPath(image))
        return((description, pixmap, optionname))

    def refresh(self):
        index = self["list"].getIndex()
        self.createsetup()
        if index is not None and len(self["list"].list) > index:
          self["list"].setIndex(index)
        else:
          self["list"].setIndex(0)

    def openSelected(self):
        return
          
    def doNothing(self):
        pass
        
    def quit(self):
        self.close()
