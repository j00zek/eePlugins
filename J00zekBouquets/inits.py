# -*- coding: utf-8 -*-
from __future__ import absolute_import #zmiana strategii ladowanie modulow w py2 z relative na absolute jak w py3

from Plugins.Extensions.J00zekBouquets.version import Version
Info='@j00zek %s' % Version

#stale
PluginName = 'J00zekBouquets'
PluginGroup = 'Extensions'

#Paths
import os
from Tools.Directories import fileExists,resolveFilename, SCOPE_CURRENT_SKIN, SCOPE_PLUGINS
PluginFolder = PluginName
PluginPath = resolveFilename(SCOPE_PLUGINS, '%s/%s/' %(PluginGroup,PluginFolder))
SkinPath = resolveFilename(SCOPE_CURRENT_SKIN, '')

def getMultiFramework():
    if fileExists("/usr/lib/enigma2/python/Plugins/SystemPlugins/ServiceApp/serviceapp.so"):
        return [("4097", "standardowy gstreamer (root 4097)"),("5001", "ServiceApp gstreamer (root 5001)"), ("5002", "ServiceApp ffmpeg (root 5002)"),("1", "sprzętowy, jak SAT (root 1)")]
    else:
        return [("4097", "standardowy gstreamer (root 4097)"),("1", "sprzętowy, jak SAT (root 1)")]

def printDBG(tekst, tryb = 'a'):
    with open("/tmp/JB.log", tryb) as f:
        f.write(tekst)
        if tekst[-1] != '\n':
            f.write('\n')
        f.close()
