from __future__ import absolute_import #zmiana strategii ladowanie modulow w py2 z relative na absolute jak w py3
from Components.config import config
from Components.Console import Console
from Plugins.Plugin import PluginDescriptor
from . import mygettext as _ , DBGlog

import os, sys
if sys.version_info.major > 2: #PyMajorVersion
    from importlib import reload

import Screens.Standby

def runCMD(myCMD):
    DBGlog('CMD: %s' % myCMD)
    with open("/proc/sys/vm/drop_caches", "w") as f: f.write("1\n")
    Console().ePopen(myCMD) #safer than os.system and asynchronous
    
def SLconfigLeaveStandbyInitDaemon():
    DBGlog('LeaveStandbyInitDaemon() >>>')
    runCMD('streamlinksrv restart')
    if config.plugins.streamlinksrv.streamlinkProxy1.value != '':
        _cmd = []
        _cmd.append('/usr/lib/enigma2/python/Plugins/Extensions/StreamlinkConfig/bin/streamlinkProxy.py')
        _cmd.append(' -l %s ' % config.plugins.streamlinksrv.logLevel.value)
        _cmd.append('--player-external-http --player-external-http-port 8818')
        _cmd.append(config.plugins.streamlinksrv.streamlinkProxy1.value)
        _cmd.append('best')
        runCMD(" ".join(_cmd))
      

def SLconfigStandbyCounterChanged(configElement):
    DBGlog('standbyCounterChanged() >>>')
    runCMD('streamlinksrv stop;killall -9 streamlinkProxy.py')
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
    from Screens.Standby import inStandby
    if reason == 0 and config.plugins.streamlinksrv.StandbyMode.value == True:
        DBGlog('reason == 0 and StandbyMode enabled')
        config.misc.standbyCounter.addNotifier(SLconfigStandbyCounterChanged, initial_call=False)



def main(session, **kwargs):
    import Plugins.Extensions.StreamlinkConfig.StreamlinkConfiguration
    reload(Plugins.Extensions.StreamlinkConfig.StreamlinkConfiguration)
    session.open(Plugins.Extensions.StreamlinkConfig.StreamlinkConfiguration.StreamlinkConfiguration)

def Plugins(path, **kwargs):
    return [PluginDescriptor(name=_("Streamlink Configuration"), where = PluginDescriptor.WHERE_PLUGINMENU, fnc = main, needsRestart = False),
            PluginDescriptor(name="StreamlinkConfig", where = PluginDescriptor.WHERE_SESSIONSTART, fnc = sessionstart, needsRestart = False, weight = -1)
           ]
