# -*- coding: utf-8 -*-
#######################################################################
#
#    Plugin for Enigma2
#    Coded by j00zek (c)2021
#
#    Uszanuj moja prace i nie kasuj/zmieniaj informacji kto jest autorem konwertera
#    Please respect my work and don't delete/change name of the converter author
#
#    This program is free software; you can redistribute it and/or
#    modify it under the terms of the GNU General Public License
#    as published by the Free Software Foundation; either version 2
#    of the License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#     
#######################################################################
 
from __init__ import *
_ = mygettext

from Components.ActionMap import ActionMap
from Components.config import config, getConfigListEntry
from Components.ConfigList import ConfigListScreen
from Components.Label import Label
#from Components.Sources.StaticText import StaticText
from Screens.Screen import Screen
#from Screens.Setup import SetupSummary

######################################################################################################
class ShareLCDwithVolumioConfig(Screen, ConfigListScreen):
        
    def __init__(self, session):
        with open('/usr/lib/enigma2/python/Plugins/Extensions/ShareLCDwithVolumio/skin.xml','r') as f:
            self.skin = f.read()
            f.close
        Screen.__init__(self, session)
        # Summary
        self.setup_title = _("Share LCD with VOLUMIO %s" % Info )
        self.onChangedEntry = []

        # Buttons
        self["key_red"] = Label(_("Cancel"))
        self["key_green"] = Label("OK")

        # Define Actions
        self["actions"] = ActionMap(["SetupActions"],
            {
                "cancel": self.keyCancel,
                "save": self.keySave,
            }
        )

        ConfigListScreen.__init__(
            self,
            [
                getConfigListEntry(_("Volumio address:"), config.plugins.ShareLCDwithVolumio.IP),
                getConfigListEntry(_("Volumio port:"), config.plugins.ShareLCDwithVolumio.PORT),
                getConfigListEntry(_("Download album art:"), config.plugins.ShareLCDwithVolumio.getAlbumArt)
            ],
            session = session,
            on_change = self.changed
        )

        # Trigger change
        self.changed()

        self.onLayoutFinish.append(self.layoutFinished)

    def layoutFinished(self):
        self.setTitle(self.setup_title)

    def changed(self):
        for x in self.onChangedEntry:
            x()

    def getCurrentEntry(self):
        return self["config"].getCurrent()[0]

    def getCurrentValue(self):
        return str(self["config"].getCurrent()[1].getText())

    def createSummary(self):
        return ShareLCDwithVolumioConfigLCD
 
class ShareLCDwithVolumioConfigLCD(Screen):
    def __init__(self, session, parent):
        with open('/usr/lib/enigma2/python/Plugins/Extensions/ShareLCDwithVolumio/skinLCD.xml','r') as f:
            self.skin = f.read()
            f.close
        Screen.__init__(self, session)
