# -*- coding: utf-8 -*-
#######################################################################
#
#    Plugin for Enigma2
#    Coded by j00zek (c)2018
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
from Components.config import config, getConfigListEntry, ConfigSubsection, ConfigIP, ConfigNumber
from Components.ConfigList import ConfigListScreen
from Components.Label import Label
#from Components.Sources.StaticText import StaticText
from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Screens.Setup import SetupSummary

config.plugins.ShareLCDwithKODI = ConfigSubsection()
config.plugins.ShareLCDwithKODI.IP = ConfigIP(default = [192,168,1,8], auto_jump = True) 
config.plugins.ShareLCDwithKODI.PORT = ConfigNumber(default = 8123)
######################################################################################################
def main(session, **kwargs):
    session.open(ShareLCDwithKODIconfig)

def Plugins(**kwargs):
    return [(  PluginDescriptor(name=_("Share LCD with KODI"), description=_("To show KODI state on LCD"),
                where=PluginDescriptor.WHERE_PLUGINMENU, icon="logo.png", fnc=main))]
######################################################################################################
class ShareLCDwithKODIconfig(Screen, ConfigListScreen):
        
    def __init__(self, session):
        with open('/usr/lib/enigma2/python/Plugins/Extensions/ShareLCDwithKODI/skin.xml','r') as f:
            self.skin = f.read()
            f.close
        Screen.__init__(self, session)
        # Summary
        self.setup_title = _("Share LCD with KODI %s" % Info )
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
                getConfigListEntry(_("Kodi address:"), config.plugins.ShareLCDwithKODI.IP),
                getConfigListEntry(_("Kodi port:"), config.plugins.ShareLCDwithKODI.PORT)
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
        return SetupSummary
 