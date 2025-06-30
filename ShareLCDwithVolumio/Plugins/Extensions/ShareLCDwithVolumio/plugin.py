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
from Components.config import config, getConfigListEntry, ConfigSubsection, ConfigIP, ConfigNumber, ConfigYesNo
from Components.ConfigList import ConfigListScreen
from Components.Label import Label
#from Components.Sources.StaticText import StaticText
from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Screens.Setup import SetupSummary

config.plugins.ShareLCDwithVolumio = ConfigSubsection()
config.plugins.ShareLCDwithVolumio.IP = ConfigIP(default = [192,168,178,101], auto_jump = True) 
config.plugins.ShareLCDwithVolumio.PORT = ConfigNumber(default = 80)
config.plugins.ShareLCDwithVolumio.getAlbumArt = ConfigYesNo(default = True)
######################################################################################################
def main(session, **kwargs):
    import setup
    reload(setup)
    session.open(setup.ShareLCDwithVolumioConfig)

def Plugins(**kwargs):
    return [(  PluginDescriptor(name=_("Share LCD with Volumio"), description=_("To show Volumio state on LCD"),
                where=PluginDescriptor.WHERE_PLUGINMENU, icon="logo.png", fnc=main))]
 