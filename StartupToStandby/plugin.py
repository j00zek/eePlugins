# -*- coding: iso-8859-1 -*-
from __future__ import absolute_import #zmiana strategii ladowanie modulow w py2 z relative na absolute jak w py3
from enigma import eTimer
from Plugins.Plugin import PluginDescriptor
from Components.config import config, ConfigSubsection, ConfigEnableDisable
from Plugins.Extensions.StartupToStandby.StartupToStandbyConfiguration import StartupToStandbyConfiguration
from Tools import Notifications
from datetime import datetime
from .__init__ import mygettext as _

import os
import Screens.Standby

config.plugins.startuptostandby = ConfigSubsection()
config.plugins.startuptostandby.enabled = ConfigEnableDisable(default = False)
config.plugins.startuptostandby.WhenWasInStandbyOnly = ConfigEnableDisable(default = True)

statusFile='/etc/enigma2/inStandby'

#DEBUG
DBG=False
append2file=False
if DBG:
    def printDEBUG( myText):
        global append2file
        try:
            if append2file == False:
                append2file = True
                f = open('/tmp/S-2-S.log', 'w')
            else:
                f = open('/tmp/S-2-S.log', 'a')
            f.write('%s %s\n' %(str(datetime.now()), myText))
            f.close
        except: pass

def leaveStandby():
    if DBG: printDEBUG('leaveStandby')
    try:
        if os.path.exists(statusFile):
            os.remove(statusFile) 
    except Exception: pass

def standbyCounterChanged(configElement):
    if DBG: printDEBUG('standbyCounterChanged')
    with open(statusFile, 'w') as f:
        f.write('\n')
        f.close()
    try:
        if leaveStandby not in Screens.Standby.inStandby.onClose:
            Screens.Standby.inStandby.onClose.append(leaveStandby)
    except Exception as e:
        if DBG: printDEBUG('standbyCounterChanged %s' % str(e))

def main(session, **kwargs):
    if DBG: printDEBUG("[StartupToStandby] Open Config Screen")
    session.open(StartupToStandbyConfiguration)

def delayedStandby():
    if DBG: printDEBUG("[StartupToStandby] delayedStandby")
    global MyDelayTimer
    try:
        MyDelayTimer.stop()
        MyDelayTimer = None
    except Exception: pass
    if config.plugins.startuptostandby.enabled.value:
        if DBG: printDEBUG('is enabled')
        Notifications.AddNotificationWithID("goStandby", Screens.Standby.Standby)
    elif config.plugins.startuptostandby.WhenWasInStandbyOnly.value and os.path.exists(statusFile):
        if DBG: printDEBUG('WhenWasInStandbyOnly')
        Notifications.AddNotificationWithID("goStandby", Screens.Standby.Standby)
        # from autoshutdown session.open(Screens.Standby.Standby)
    else:
        if DBG: printDEBUG('not enabled or was not in standby before')
        
MyDelayTimer = eTimer()
MyDelayTimer.callback.append(delayedStandby)
# sessionstart
def sessionstart(reason, session = None):
    if DBG: printDEBUG("[StartupToStandby] autostart")
    # from autoshutdown global session
    from Screens.Standby import inStandby
    if reason == 0 and not inStandby:
        if DBG: printDEBUG('reason == 0 and not inStandby')
        config.misc.standbyCounter.addNotifier(standbyCounterChanged, initial_call=False)
        MyDelayTimer.start(2000,True)

def Plugins(path, **kwargs):
    return [PluginDescriptor(name=_("Startup To Standby"), where = PluginDescriptor.WHERE_PLUGINMENU, fnc = main, needsRestart = False),
            PluginDescriptor(name="StartupToStandby", where = PluginDescriptor.WHERE_SESSIONSTART, fnc = sessionstart, needsRestart = False, weight = -1)]
