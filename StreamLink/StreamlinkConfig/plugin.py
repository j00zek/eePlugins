from Components.config import config
from importlib import reload
from Plugins.Plugin import PluginDescriptor
from . import mygettext as _ , DBGlog

import os, sys, subprocess


import Screens.Standby

DBG = True

def safeSubprocessCMD(myCommand):
    if DBG: DBGlog('safeSubprocessCMD(%s)' % myCommand)
    with open("/proc/sys/vm/drop_caches", "w") as f: f.write("1\n") #for safety to not get GS due to lack of memory
    subprocess.Popen(myCommand, shell=True)
    with open("/proc/sys/vm/drop_caches", "w") as f: f.write("1\n") #for safety to not get GS due to lack of memory

def SLconfigLeaveStandbyInitDaemon():
    DBGlog('LeaveStandbyInitDaemon() >>>')
    safeSubprocessCMD('%s restart' % config.plugins.streamlinkSRV.binName.value)
    if os.path.exists('/usr/sbin/emukodiSRV'): safeSubprocessCMD('emukodiSRV restart')

def SLconfigStandbyCounterChanged(configElement):
    DBGlog('standbyCounterChanged() >>>')
    if config.plugins.streamlinkSRV.StandbyMode.value == True:
        safeSubprocessCMD('streamlinkproxySRV stop;streamlinkproxySRV stop')
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
    #cmds.append("[ `grep -c 'WHERE_CHANNEL_ZAP' < /usr/lib/enigma2/python/Plugins/Plugin.pyc` -eq 0 ] && touch /usr/lib/enigma2/python/Plugins/Extensions/StreamlinkConfig/NoZapWrappers")
    cmds.append("[ `ps -ef|grep -v grep|grep -c streamlinkproxy` -gt 0 ] && killall streamlinkproxy >/dev/null")
    #cmds.append("/usr/lib/enigma2/python/Plugins/Extensions/StreamlinkConfig/bin/re-initiate.sh")
    cmds.append("[ `ps -ef|grep -v grep|grep -c streamlinkproxySRV` -gt 0 ] && streamlinkproxySRV stop")
    cmds.append("[ `ps -ef|grep -v grep|grep -c streamlinkSRV` -gt 0 ] && streamlinkSRV stop")
    if config.plugins.streamlinkSRV.enabled.value:
        cmds.append("%s restart" % config.plugins.streamlinkSRV.binName.value)
    safeSubprocessCMD(';'.join(cmds))
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
    #import Plugins.Extensions.StreamlinkConfig.StreamlinkConfiguration
    #reload(Plugins.Extensions.StreamlinkConfig.StreamlinkConfiguration)
    session.open(SLK_Menu)

def Plugins(path, **kwargs):
    myList = [PluginDescriptor(name=_("Streamlink Configuration"), where = PluginDescriptor.WHERE_PLUGINMENU, icon="logo.png", fnc = main, needsRestart = False),
            PluginDescriptor(name="StreamlinkConfig", where = PluginDescriptor.WHERE_SESSIONSTART, fnc = sessionstart, needsRestart = False, weight = -1)
           ]
    if os.path.exists('/usr/lib/enigma2/python/Plugins/Extensions/StreamlinkConfig/NoZapWrappers'):
        print('[SLK] system NIE wspiera wrapperów :)')
    else:
        print('[SLK] system wspiera wrappery :)')
        myList.append(PluginDescriptor(name="StreamlinkZapWrapper", description="StreamlinkZapWrapper", where=PluginDescriptor.WHERE_CHANNEL_ZAP, needsRestart = False, fnc=SLzapWrapper))
    if config.plugins.streamlinkSRV.Recorder.value == True:
        myList.append(PluginDescriptor(name="StreamlinkRecorder", description="StreamlinkRecorder", where = [PluginDescriptor.WHERE_MENU], fnc=timermenu))
    return myList

####MENU
from Screens.Screen import Screen
from Components.Pixmap import Pixmap
from Components.Sources.List import List
from Components.ActionMap import ActionMap
from Plugins.Extensions.StreamlinkConfig.version import Version
from Components.MenuList import MenuList
from Tools.LoadPixmap import LoadPixmap

class SLK_Menu(Screen):
    skin = """
<screen position="center,center" size="880,500">
        <widget source="list" render="Listbox" position="0,0" size="880,500" scrollbarMode="showOnDemand">
                <convert type="TemplatedMultiContent">
                        {"template": [
                                MultiContentEntryPixmapAlphaTest(pos = (12, 2), size = (120, 40), png = 0),
                                MultiContentEntryText(pos = (138, 2), size = (760, 40), font=0, flags = RT_HALIGN_LEFT|RT_VALIGN_CENTER, text = 1),
                                ],
                                "fonts": [gFont("Regular", 24)],
                                "itemHeight": 44
                        }
                </convert>
        </widget>
</screen>"""

    def __init__(self, session):
        Screen.__init__(self, session)
        self.setup_title = "SLK menu v. %s" % Version
        Screen.setTitle(self, self.setup_title)
        self["list"] = List()
        self["setupActions"] = ActionMap(["SetupActions", "MenuActions"],
            {
                    "cancel": self.quit,
                    "ok": self.openSelected,
                    "menu": self.quit,
                    #"down": self.down,
                    #"up": self.up
            }, -2)
        self.setTitle("SLK menu v. %s" % Version)
        self["list"].list = []
        self.createsetup()

    def createsetup(self):
        Mlist = []
        if not os.path.exists('/usr/sbin/streamlinkSRV'):
            Mlist.append(self.buildListEntry("Demon nie zainstalowany", "info.png",'doNothing'))
        elif os.path.exists('/usr/sbin/streamlinkproxy'):
            Mlist.append(self.buildListEntry("streamlinkproxy nie wspierany", "info.png",'doNothing'))
        elif not os.path.exists("/usr/lib/enigma2/python/Plugins/SystemPlugins/ServiceApp/serviceapp.so"):
            Mlist.append(self.buildListEntry("Brak zainstalowanego serviceapp", "info.png",'doNothing'))
        else:
            Mlist.append(self.buildListEntry("Zaprogramuj nagranie", "config.png",'menuRecorderConfig'))
            Mlist.append(self.buildListEntry("Konfiguracja demona", "config.png",'menuDaemonConfig'))
            Mlist.append(self.buildListEntry("Dodaj/Usuń bukiet IPTV", "iptv.png",'menuAvailableIPTVbouquets'))
            Mlist.append(self.buildListEntry("Pobierz/Usuń bukiet IPTV kolegi Azman", "azman.png",'menuIPTVazman'))
            Mlist.append(self.buildListEntry("Zmień framework w serwisach IPTV", "folder.png",'menuIPTVframework'))
            Mlist.append(self.buildListEntry("Zmień wrapper na serwer 127.0.0.1 w serwisach IPTV", "folder.png",'menuIPTVwrappersrv'))
            Mlist.append(self.buildListEntry("Konfiguacja pilot.wp.pl", "wptv.png",'menuPilotWPpl'))
            if not os.path.exists('/usr/lib/python3.12/site-packages/'):
                Mlist.append(self.buildListEntry('\c00981111' + "*** Brak wsparcia DRM dla tej wersji pythona ***", "remove.png",'doNothing'))
            elif not os.path.exists('/usr/lib/python3.12/site-packages/emukodi/'):
                Mlist.append(self.buildListEntry('\c00981111' + "*** Brak wsparcia DRM, moduł streamlink-cdm nie zainstalowany ***", "remove.png",'doNothing'))
            else:
                #if os.path.exists('/usr/lib/enigma2/python/Plugins/Extensions/IPTVPlayer/plugin.pe2i'):
                #    Mlist.append(self.buildListEntry(r'\c00ffff00' + 'Zalecane korzystanie z e2iplayer-a SSS do oglądania materiałów DRM !!!!', "info.png",'doNothing'))
                cdmStatus = None
                try:
                    from  pywidevine.cdmdevice.checkCDMvalidity import testDevice
                    cdmStatus = testDevice()
                    print('cdmStatus = "%s"' % cdmStatus)
                except Exception as e: 
                    print(str(e))
                    Mlist.append(self.buildListEntry('\c00981111' + "*** Błąd ładowania modułu urządzenia cdm ***", "info.png",'doNothing'))
                open('/etc/streamlink/cdmStatus','w').write(str(cdmStatus))
                if cdmStatus is None:
                    Mlist.append(self.buildListEntry('\c00981111' + "*** Błąd sprawdzania urządzenia cdm ***", "info.png",'doNothing'))
                elif not cdmStatus:
                    Mlist.append(self.buildListEntry('\c00ff9400' + "*** Limitowane wsparcie KODI>DRM ***", "info.png",'doNothing'))
                else:
                    Mlist.append(self.buildListEntry('\c00289496' + "*** Pełne wsparcie KODI>DRM ***", "info.png",'doNothing'))

                if not cdmStatus is None:
                    for cfgFile in ['playermb', 'canalplusvod', 'pgobox', 'cdaplMB']:
                        if not os.path.exists('/etc/streamlink/%s' % cfgFile):
                            os.system('mkdir -p /etc/streamlink/%s' % cfgFile)
                    Mlist.append(self.buildListEntry("Konfiguacja player.pl", "playerpl.png",'menuDRMplayerpl'))
                    Mlist.append(self.buildListEntry("Konfiguacja cda", "cdapl.png",'menuDRMcda'))
                    Mlist.append(self.buildListEntry("Konfiguacja posatbox", "polsatboxgo.png",'menuDRMpolsatbox'))

        self["list"].list = Mlist

    def buildListEntry(self, description, image, optionname):
            image = '/usr/lib/enigma2/python/Plugins/Extensions/StreamlinkConfig/pic/%s' % image
            if os.path.exists(image):
                pixmap = LoadPixmap(image)
            else:
                pixmap = LoadPixmap('/usr/lib/enigma2/python/Plugins/Extensions/StreamlinkConfig/pic/config.png')
            return((pixmap, description, optionname))

    def openSelected(self):
        selected = str(self["list"].getCurrent()[2])
        if selected == 'menuDaemonConfig':
            import Plugins.Extensions.StreamlinkConfig.menuDaemonConfig
            reload(Plugins.Extensions.StreamlinkConfig.menuDaemonConfig)
            self.session.openWithCallback(self.doNothing,Plugins.Extensions.StreamlinkConfig.menuDaemonConfig.StreamlinkConfiguration)
            return
        elif selected == 'menuAvailableIPTVbouquets':
            import Plugins.Extensions.StreamlinkConfig.menuAvailableIPTVbouquets
            reload(Plugins.Extensions.StreamlinkConfig.menuAvailableIPTVbouquets)
            self.session.openWithCallback(self.doNothing,Plugins.Extensions.StreamlinkConfig.menuAvailableIPTVbouquets.StreamlinkConfiguration)
            return
        elif selected == 'menuIPTVazman':
            import Plugins.Extensions.StreamlinkConfig.menuIPTVazman
            reload(Plugins.Extensions.StreamlinkConfig.menuIPTVazman)
            self.session.openWithCallback(self.doNothing,Plugins.Extensions.StreamlinkConfig.menuIPTVazman.StreamlinkConfiguration)
            return
        elif selected == 'menuIPTVframework':
            import Plugins.Extensions.StreamlinkConfig.menuIPTVframework
            reload(Plugins.Extensions.StreamlinkConfig.menuIPTVframework)
            self.session.openWithCallback(self.doNothing,Plugins.Extensions.StreamlinkConfig.menuIPTVframework.StreamlinkConfiguration)
            return
        elif selected == 'menuIPTVwrappersrv':
            import Plugins.Extensions.StreamlinkConfig.menuIPTVwrappersrv
            reload(Plugins.Extensions.StreamlinkConfig.menuIPTVwrappersrv)
            self.session.openWithCallback(self.doNothing,Plugins.Extensions.StreamlinkConfig.menuIPTVwrappersrv.StreamlinkConfiguration)
            return
        elif selected == 'menuPilotWPpl':
            import Plugins.Extensions.StreamlinkConfig.menuPilotWPpl
            reload(Plugins.Extensions.StreamlinkConfig.menuPilotWPpl)
            self.session.openWithCallback(self.doNothing,Plugins.Extensions.StreamlinkConfig.menuPilotWPpl.StreamlinkConfiguration)
            return
        elif selected == 'menuDRMplayerpl':
            import Plugins.Extensions.StreamlinkConfig.menuDRMplayerpl
            reload(Plugins.Extensions.StreamlinkConfig.menuDRMplayerpl)
            self.session.openWithCallback(self.doNothing,Plugins.Extensions.StreamlinkConfig.menuDRMplayerpl.StreamlinkConfiguration)
            return
        elif selected == 'menuDRMcda':
            import Plugins.Extensions.StreamlinkConfig.menuDRMcda
            reload(Plugins.Extensions.StreamlinkConfig.menuDRMcda)
            self.session.openWithCallback(self.doNothing,Plugins.Extensions.StreamlinkConfig.menuDRMcda.StreamlinkConfiguration)
            return
        elif selected == 'menuDRMpolsatbox':
            import Plugins.Extensions.StreamlinkConfig.menuDRMpolsatbox
            reload(Plugins.Extensions.StreamlinkConfig.menuDRMpolsatbox)
            self.session.openWithCallback(self.doNothing,Plugins.Extensions.StreamlinkConfig.menuDRMpolsatbox.StreamlinkConfiguration)
            return

    def doNothing(self, retVal = None):
        return
                
    def quit(self):
        self.close()

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
            if url == '' or len(url) < 11:
                killExternalPlayer()
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
    
def killExternalPlayer(isExternalPlayerRunning, forceKill = False):
    cmd = ''
    try:
        for proc in os.listdir('/proc'):
            procExe = os.path.join('/proc', proc, 'exe')
            if os.path.exists(procExe):
                procRealPath = os.path.realpath(procExe)
                if 'exteplayer3' in procRealPath:
                    cmd = '/usr/bin/killall exteplayer3;'
                #elif 'cdmeplayer3' in procRealPath:
                #    cmd = '/usr/bin/killall cdmeplayer3;'
    except Exception:
        pass
    if isExternalPlayerRunning or forceKill:
        cmd += '/usr/bin/killall -q cdmeplayer3'
        isExternalPlayerRunning = False
    if cmd != '':
        safeSubprocessCMD(cmd)

class SLeventsWrapper:
    def __init__(self, session):
        print("[SLeventsWrapper.__init__] >>>")
        self.session = session
        self.service = None
        self.onClose = []
        self.myCDM = None
        self.deviceCDM = None
        self.isExternalPlayerRunning = False
        self.skipKillAt__evEnd = False
        self.__event_tracker = ServiceEventTracker(screen=self, eventmap={iPlayableService.evStart: self.__evStart, iPlayableService.evEnd: self.__evEnd})
        return

    def __evStart(self):
        print("[SLeventsWrapper.__evStart] >>>")
        #killExternalPlayer(self.isExternalPlayerRunning)
        if self.myCDM is None:
            try:
                import pywidevine.cdmdevice.privatecdm
                self.myCDM = pywidevine.cdmdevice.privatecdm.privatecdm()
            except ImportError:
                self.myCDM = False
        
        self.serviceName = ""
        try:
            service = self.session.nav.getCurrentlyPlayingServiceReference()
            if self.isExternalPlayerRunning:
                killExternalPlayer(self.isExternalPlayerRunning)
            if not service is None:
                serviceString = service.toString()
                #print("[SLeventsWrapper]__evStart serviceString=", serviceString)
                serviceList = serviceString.split(":")
                print("[SLeventsWrapper]__evStart serviceList=", serviceList)
                if len(serviceList) > 10:
                    url = serviceList[10].strip().lower()
                    if url != '':
                        if self.myCDM != False and self.myCDM.doWhatYouMustDo(url):
                            self.isExternalPlayerRunning = True
                        elif url.startswith('http%3a//cdmplayer/'):
                            if self.deviceCDM is None: #tutaj, zeby bez sensu nie ladować jak ktos nie uzywa
                                try:
                                    import pywidevine.cdmdevice.cdmDevice
                                    self.deviceCDM = pywidevine.cdmdevice.cdmDevice.cdmDevice()
                                except ImportError:
                                    self.deviceCDM = False
                            if self.deviceCDM != False and self.deviceCDM.tryToDoSomething(url):
                                self.isExternalPlayerRunning = True
                                #tryToDoSomething take time to proceed and initiate player.
                                # so we need to ...
                                #   - mark this to properly manage __evEnd eventmap (if not managed, killed process & black screen)
                                #   - stop enigma player (if not stopped only back screen)
                                if 1:
                                    self.skipKillAt__evEnd = True #tryToDoSomethingbelow is delayed, we need skip it
                                    self.session.nav.stopService() #this initiates false/positive __evEnd
                        elif url.startswith('http%3a//slplayer/'):
                            cmd2run = []
                            cmd2run.extend(['/usr/bin/killall -q cdmeplayer3;'])
                            cmd2run.extend(['/usr/bin/killall -q exteplayer3;'])
                            cmd2run.extend(['/usr/sbin/streamlink'])
                            cmd2run.extend(['-l','none','-p','/usr/bin/exteplayer3','--player-http','--verbose-player',"'%s'" % url.replace('http%3a//slplayer/',''), 'best'])
                            safeSubprocessCMD(' '.join(cmd2run))
                            if 1: # see comments above
                                self.skipKillAt__evEnd = True
                                self.session.nav.stopService()
                        else:
                            killExternalPlayer(self.isExternalPlayerRunning, True)
        except Exception as e:
            print('[SLeventsWrapper] __evStart() exception:', str(e))

    def __evEnd(self):
        print("[SLeventsWrapper.__evEnd] >>> self.isExternalPlayerRunning=%s" % str(self.isExternalPlayerRunning))
        print("[SLeventsWrapper.__evEnd] >>> self.skipKillAt__evEnd=%s" % str(self.skipKillAt__evEnd))
        if not self.skipKillAt__evEnd and self.isExternalPlayerRunning:
            print("[SLeventsWrapper.__evEnd] >>> killExternalPlayer run")
            killExternalPlayer(self.isExternalPlayerRunning)
            self.isExternalPlayerRunning = False
            self.skipKillAt__evEnd = False