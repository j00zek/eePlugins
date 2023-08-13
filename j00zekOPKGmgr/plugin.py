# -*- coding: utf-8 -*-
#
# maintainer: j00zek 2016-2022
#

#This plugin is free software, you are allowed to
#modify it (if you keep the license),
#but you are not allowed to distribute/publish
#it without source code (this version and your modifications).
#This means you also have to distribute
#source code of your modifications.
from __future__ import absolute_import #zmiana strategii ladowania modulow w py2 z relative na absolute jak w py3

from enigma import eTimer
from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from . import *
_ = mygettext

class AutoUpdate(Screen):
    def __init__(self, session):
        self.session = session
        Screen.__init__(self, session)
        AutoUpdate.AutoUpdateTimer = eTimer()
        AutoUpdate.AutoUpdateTimer.callback.append(self.checkANDrefresh)
        AutoUpdate.AutoUpdateTimer.start(1000*60*60*24*7) # raz na tydzień

    def checkANDrefresh(self):
        from Tools.Directories import SCOPE_PLUGINS, resolveFilename
        from os import path as os_path
        from Components.Console import Console
        CMDs=[]
        CMDs.append('rm -f /tmp/.opkg.status')
        CMDs.append('killall -9 opkg 2>/dev/null')
        CMDs.append('killall -9 wget 2>/dev/null')
        CMDs.append('opkg update')
        CMDs.append('sleep 2')
        CMDs.append('killall -9 opkg 2>/dev/null')
        CMDs.append('killall -9 wget 2>/dev/null')
        #CMDs.append('opkg list-upgradable>>/tmp/.opkg.status')
        CMDs.append('opkg list-upgradable>>/tmp/.opkg.status')
        with open("/proc/sys/vm/drop_caches", "w") as f: f.write("1\n")
        Console().eBatch(CMDs,self.checkANDrefreshCB)
        return

    def checkANDrefreshCB(self, ConsoleOutput=None, ExitCode=None, retUnknown=None):
        if ExitCode is not None and ExitCode == 99 and ConsoleOutput is not None:
            #print("Files updated, reboot needed")
            from Screens.Standby import inStandby
            if inStandby is None:
                def ExitRet(ret):
                    if ret:
                        from enigma import quitMainloop
                        quitMainloop(3)
                    return
                    
                def ExitRetopkg(ret):
                    if ret:
                        from Jopkg import Jopkg
                        session.open(Jopkg)
                from Screens.MessageBox import MessageBox
                self.session.openWithCallback(ExitRetopkg, MessageBox, "New actualization ready to install\nStart OPKG manager?", timeout=10, default=False)

######################################################################################################
######################################################################################################
def main(session, **kwargs):
    from Plugins.Extensions.j00zekOPKGmgr.Jopkg import Jopkg
    session.open(Jopkg)

def sessionstart(reason, **kwargs):
        session = kwargs["session"]
        AutoUpdate(session)

def Plugins(**kwargs):
    myPlugs=[PluginDescriptor(where = PluginDescriptor.WHERE_SESSIONSTART, fnc = sessionstart)]
    myPlugs.append( (PluginDescriptor(name=_("Alternate OPKG manager"), description=_("Install, update, upgade all ipk packages from GUI"), where=PluginDescriptor.WHERE_PLUGINMENU, icon="logo.png", fnc=main)) )
    return myPlugs

            