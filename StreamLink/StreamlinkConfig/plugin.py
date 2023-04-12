from __future__ import absolute_import #zmiana strategii ladowanie modulow w py2 z relative na absolute jak w py3
from Components.config import config
from Components.Console import Console
from Plugins.Plugin import PluginDescriptor
from . import mygettext as _ , DBGlog

import os, sys

if sys.version_info.major > 2: #PyMajorVersion
    from importlib import reload

import Screens.Standby

DBG = True

def runCMD(myCMD):
    DBGlog('CMD: %s' % myCMD)
    with open("/proc/sys/vm/drop_caches", "w") as f: f.write("1\n")
    if ';' in myCMD:
        myCMDs = myCMD.split(';')
        CMDsCount = len(myCMDs)
        curCount = 1
        for curCMD in myCMDs:
            if curCount == CMDsCount:
                Console().ePopen(curCMD + " &")
            else:
                Console().ePopen(curCMD)
            curCount += 1
    else:
        Console().ePopen(myCMD + " &")

def initProxy():
    if config.plugins.streamlinkSRV.streamlinkProxy1.value != '':
        _cmd = []
        _cmd.append('/usr/lib/enigma2/python/Plugins/Extensions/StreamlinkConfig/bin/streamlinkProxy.py')
        _cmd.append(' -l %s ' % config.plugins.streamlinkSRV.logLevel.value)
        _cmd.append('--player-external-http --player-external-http-port 8818')
        _cmd.append(config.plugins.streamlinkSRV.streamlinkProxy1.value)
        _cmd.append('best')
        DBGlog('runCMD(%s)' % " ".join(_cmd))
        runCMD(" ".join(_cmd))

def SLconfigLeaveStandbyInitDaemon():
    DBGlog('LeaveStandbyInitDaemon() >>>')
    runCMD('streamlinkSRV restart')
    initProxy()

def SLconfigStandbyCounterChanged(configElement):
    DBGlog('standbyCounterChanged() >>>')
    runCMD('streamlinkSRV stop;killall -9 streamlinkProxy.py')
    try:
        if SLconfigLeaveStandbyInitDaemon not in Screens.Standby.inStandby.onClose:
            Screens.Standby.inStandby.onClose.append(SLconfigLeaveStandbyInitDaemon)
    except Exception as e:
        DBGlog('standbyCounterChanged EXCEPTION: %s' % str(e))

# sessionstart
def sessionstart(reason, session = None):
    if os.path.exists("/tmp/StreamlinkConfig.log"):
        os.remove("/tmp/StreamlinkConfig.log")
    DBGlog("autostart")
    runCMD('/usr/lib/enigma2/python/Plugins/Extensions/StreamlinkConfig/bin/re-initiate.sh;streamlinkSRV restart;killall -9 streamlinkProxy.py')
    from Screens.Standby import inStandby
    if reason == 0 and config.plugins.streamlinkSRV.StandbyMode.value == True:
        DBGlog('reason == 0 and StandbyMode enabled')
        config.misc.standbyCounter.addNotifier(SLconfigStandbyCounterChanged, initial_call=False)
        initProxy()

def timermenu(menuid, **kwargs):
    DBGlog("timermenu(%s)" % str(menuid))
    if menuid == "timermenu":
        return [(_("Streamlink Timers"), mainRecorder, "streamlinktimer", None)]
    else:
        return []

def mainRecorder(session, **kwargs):
    DBGlog("mainRecorder()")
    import Plugins.Extensions.StreamlinkConfig.StreamlinkRecorder
    reload(Plugins.Extensions.StreamlinkConfig.StreamlinkRecorder)
    session.open(Plugins.Extensions.StreamlinkConfig.StreamlinkRecorder.StreamlinkRecorderScreen)

def main(session, **kwargs):
    DBGlog("main")
    import Plugins.Extensions.StreamlinkConfig.StreamlinkConfiguration
    reload(Plugins.Extensions.StreamlinkConfig.StreamlinkConfiguration)
    session.open(Plugins.Extensions.StreamlinkConfig.StreamlinkConfiguration.StreamlinkConfiguration)

def Plugins(path, **kwargs):
    myList = [PluginDescriptor(name=_("Streamlink Configuration"), where = PluginDescriptor.WHERE_PLUGINMENU, icon="logo.png", fnc = main, needsRestart = False),
            PluginDescriptor(name="StreamlinkConfig", where = PluginDescriptor.WHERE_SESSIONSTART, fnc = sessionstart, needsRestart = False, weight = -1)
           ]
    if config.plugins.streamlinkSRV.Recorder.value == True:
        myList.append(PluginDescriptor(name="StreamlinkRecorder", description=_("StreamlinkRecorder"), where = [PluginDescriptor.WHERE_MENU], fnc=timermenu))
    return myList
