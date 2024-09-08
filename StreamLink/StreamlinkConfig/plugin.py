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

def SLconfigLeaveStandbyInitDaemon():
    DBGlog('LeaveStandbyInitDaemon() >>>')
    runCMD('%s restart' % config.plugins.streamlinkSRV.binName.value)
    if os.path.exists('/usr/sbin/emukodiSRV'): runCMD('emukodiSRV restart')

def SLconfigStandbyCounterChanged(configElement):
    DBGlog('standbyCounterChanged() >>>')
    if config.plugins.streamlinkSRV.StandbyMode.value == True:
        runCMD('%s stop;killall -9 streamlinkProxy.py' % config.plugins.streamlinkSRV.binName.value)
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
    cmds = []
    cmds.append("[ `grep -c 'WHERE_CHANNEL_ZAP' < /usr/lib/enigma2/python/Plugins/Plugin.pyc` -eq 0 ] && touch /usr/lib/enigma2/python/Plugins/Extensions/StreamlinkConfig/NoZapWrappers")
    cmds.append("/usr/lib/enigma2/python/Plugins/Extensions/StreamlinkConfig/bin/re-initiate.sh")
    cmds.append("killall -9 streamlinkProxy.py")
    cmds.append("%s restart" % config.plugins.streamlinkSRV.binName.value)
    runCMD(';'.join(cmds))
    from Screens.Standby import inStandby
    if reason == 0 and config.plugins.streamlinkSRV.StandbyMode.value == True:
        DBGlog('reason == 0 and StandbyMode enabled')
        config.misc.standbyCounter.addNotifier(SLconfigStandbyCounterChanged, initial_call=False)
    global SLeventsWrapperInstance
    if SLeventsWrapperInstance is None:
        SLeventsWrapperInstance = SLeventsWrapper(session)

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
    if not os.path.exists('/usr/lib/enigma2/python/Plugins/Extensions/StreamlinkConfig/NoZapWrappers'):
        print('system wspiera wrappery :)')
        myList.append(PluginDescriptor(name="StreamlinkZapWrapper", description="StreamlinkZapWrapper", where=PluginDescriptor.WHERE_CHANNEL_ZAP, needsRestart = False, fnc=SLzapWrapper))
    if config.plugins.streamlinkSRV.Recorder.value == True:
        myList.append(PluginDescriptor(name="StreamlinkRecorder", description=_("StreamlinkRecorder"), where = [PluginDescriptor.WHERE_MENU], fnc=timermenu))
    return myList
############################################# SLzapWrapper #################################
####### logika E2: zap(tylko na kanałach iptv?) > __evEnd > __evStart

#jest zainstalowane oryginalne, olewamy
if os.path.exists('/usr/lib/enigma2/python/Plugins/Extensions/YTDLPWrapper'):
    SLzapWrapper_YT_DLP = False
else:
    SLzapWrapper_YT_DLP = None

if os.path.exists('/usr/lib/enigma2/python/Plugins/Extensions/YTDLWrapper'):
    SLzapWrapper_YT_DL = False
else:
    SLzapWrapper_YT_DL = None

if os.path.exists('/usr/lib/enigma2/python/Plugins/Extensions/StreamlinkWrapper'):
    SLzapWrapper_Streamlink = False
else:
    SLzapWrapper_Streamlink = None

def SLzapWrapper(session, service, **kwargs):
    print("[SLzapWrapper] >>>")
    global SLzapWrapper_YT_DLP, SLzapWrapper_YT_DL, SLzapWrapper_Streamlink
    errormsg = None
    if service:
        try:
            serviceString = service.toString()
            print("[SLzapWrapper] serviceString = %s" % serviceString)
            url = serviceString.split(":")
            print("[SLzapWrapper] urlparts = %s" % len(url))
            url = url[10].strip()
            print("[SLzapWrapper] url='%s'" % url)
            if url == '':
                return (None, errormsg)
            elif len(url) < 11:
                return (None, errormsg)
            #YT-DLP
            elif url.startswith("YT-DLP%3a//"): #YT-DLP
                if SLzapWrapper_YT_DLP is None:
                    try:
                        from yt_dlp import YoutubeDL as SLzapWrapper_YT_DLP
                    except ImportError:
                        SLzapWrapper_YT_DLP = False
                if SLzapWrapper_YT_DLP == False:
                    return (None, errormsg)
                url = url.replace("YT-DLP%3a//", "").replace("%3a", ":")
                try:
                    ydl = SLzapWrapper_YT_DLP({"format": "b", "no_color": True, "usenetrc": True})
                    result = ydl.extract_info(url, download=False)
                    result = ydl.sanitize_info(result)
                    if result and result.get("url"):
                        url = result["url"]
                        print("[SLzapWrapper] SLzapWrapper_YT_DLP result url %s" % url)
                        return (url, errormsg)
                    else:
                        errormsg = "No Link found!"
                        print("[SLzapWrapper] SLzapWrapper_YT_DLP no streams")
                except Exception as e:
                    errormsg = str(e)
                    print("[SLzapWrapper] SLzapWrapper_YT_DLP failed %s" % str(e))
            #YT-DL
            elif url.startswith("YT-DL%3a//"):#YT-DL
                if SLzapWrapper_YT_DL is None:
                    try:
                        from youtube_dl import YoutubeDL as SLzapWrapper_YT_DL
                    except ImportError:
                        SLzapWrapper_YT_DL = False
                if SLzapWrapper_YT_DL == False:
                    return (None, errormsg)
                url = url.replace("YT-DL%3a//", "").replace("%3a", ":")
                try:
                    ydl = SLzapWrapper_YT_DL({'format': 'best'})
                    result = ydl.extract_info(url, download=False)
                    if result and hasattr(result, "url"):
                        url = result['url']
                        print("[SLzapWrapper] SLzapWrapper_YT_DL result url %s" % url)
                        return (url, errormsg)
                    else:
                        errormsg = "No Link found!"
                        print("[SLzapWrapper] SLzapWrapper_YT_DL no streams")
                except Exception as e:
                    errormsg = str(e)
                    print("[SLzapWrapper] SLzapWrapper_YT_DL failed %s" % str(e))
            #streamlink
            elif url.startswith("streamlink%3a//"):# or url.startswith("http%3a//127.0.0.1%3a8088/"):#streamlink
                if SLzapWrapper_Streamlink is None:
                    try:
                        import streamlink as SLzapWrapper_Streamlink
                    except ImportError:
                        SLzapWrapper_Streamlink = False
                if SLzapWrapper_Streamlink == False:
                    return (None, errormsg)
                url = url.replace("streamlink%3a//", "").replace('http%3a//127.0.0.1%3a8088/','').replace("%3a", ":")
                print("[SLzapWrapper] streamlink calling url %s" % url)
                try:
                    streams = SLzapWrapper_Streamlink.streams(url)
                    if streams:
                        url = streams["best"].to_url()
                        print("[SLzapWrapper] streamlink result url %s" % url)
                        return (url, errormsg)
                    else:
                        errormsg = "No Link found!"
                        print("[SLzapWrapper] streamlink no streams")
                except Exception as e:
                    errormsg = str(e)
                    print("[SLzapWrapper] streamlink failed %s" % str(e))
        except Exception as e:
            errormsg = str(e)
            print("[SLzapWrapper] exception %s" % str(e))
    return (None, errormsg)

############################################# SLeventsWrapper #################################
SLeventsWrapperInstance = None

from Components.ServiceEventTracker import ServiceEventTracker#, InfoBarBase
from enigma import iPlayableService#, eServiceCenter, iServiceInformation
#import ServiceReference
import subprocess

def safeSubprocessCMD(myCommand):
    with open("/proc/sys/vm/drop_caches", "w") as f: f.write("1\n") #for safety to not get GS due to lack of memory
    subprocess.Popen(myCommand, shell=True)
    
class SLeventsWrapper:
    def __init__(self, session):
        print("[SLeventsWrapper.__init__] >>>")
        self.session = session
        self.service = None
        self.onClose = []
        self.myCDM = None
        self.isExternalPlayerRunning = False
        self.__event_tracker = ServiceEventTracker(screen=self, eventmap={iPlayableService.evStart: self.__evStart, iPlayableService.evEnd: self.__evEnd})
        return
    def __evStart(self):
        print("[SLeventsWrapper.__evStart] >>>")
        if self.myCDM is None:
            try:
                import pywidevine.cdmdevice.privatecdm
                self.myCDM = pywidevine.cdmdevice.privatecdm.privatecdm()
            except ImportError:
                self.myCDM = False
        if self.myCDM != False:
            self.serviceName = ""
            try:
                service = self.session.nav.getCurrentlyPlayingServiceReference()
                if not service is None:
                    serviceString = service.toString()
                    #print("[SLeventsWrapper]__evStart serviceString=", serviceString)
                    serviceList = serviceString.split(":")
                    print("[SLeventsWrapper]__evStart serviceList=", serviceList)
                    if len(serviceList) > 10:
                        url = serviceList[10].strip().lower()
                        if url != '' and self.myCDM.doWhatYouMustDo(url):
                            self.isExternalPlayerRunning = True
            except Exception as e:
                print('[SLeventsWrapper] __evStart() exception:', str(e))

    def __evEnd(self):
        print("[SLeventsWrapper.__evEnd] >>>")
        print("[SLzapWrapper] self.isExternalPlayerRunning=%s" % str(self.isExternalPlayerRunning))
        if self.isExternalPlayerRunning:
            safeSubprocessCMD('/usr/bin/killall exteplayer3;/usr/bin/killall -9 exteplayer3')
