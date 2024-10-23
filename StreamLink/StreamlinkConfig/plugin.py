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
        wrapperInfo = '[SLK] system NIE wspiera wrapperów'
    else:
        wrapperInfo = '[SLK] system wspiera wrappery'
        if os.path.exists('/usr/lib/enigma2/python/Plugins/Extensions/YTDLPWrapper'):
            wrapperInfo += ', YTDLPWrapper zainstalowany'
        else:
            wrapperInfo += ', YTDLPWrapper nie zainstalowany'
        if os.path.exists('/usr/lib/enigma2/python/Plugins/Extensions/YTDLWrapper'):
            wrapperInfo += ', YTDLWrapper zainstalowany'
        else:
            wrapperInfo += ', YTDLWrapper nie zainstalowany'
        if os.path.exists('/usr/lib/enigma2/python/Plugins/Extensions/StreamlinkWrapper'):
            wrapperInfo += ', StreamlinkWrapper zainstalowany'
        else:
            wrapperInfo += ', StreamlinkWrapper nie zainstalowany'
    print(wrapperInfo)
    wrapperInfo = None
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

############################################# SLeventsWrapper #################################
SLeventsWrapperInstance = None

from Components.ServiceEventTracker import ServiceEventTracker#, InfoBarBase
from enigma import iPlayableService#, eServiceCenter, iServiceInformation
#import ServiceReference
from enigma import eTimer

class SLeventsWrapper:
    def __init__(self, session):
        print("[SLeventsWrapper.__init__] >>>")
        self.session = session
        self.service = None
        self.onClose = []
        self.myCDM = None
        self.deviceCDM = None
        self.ActiveExternalPlayer = ''
        self.skipKillAt__evEnd = False
        self.LastServiceString = ""
        self.RestartServiceTimer = eTimer()
        self.RestartServiceTimer.callback.append(self.__restartServiceTimerCB)
        self.LastPlayedService = None
        self.__event_tracker = ServiceEventTracker(screen=self, eventmap={iPlayableService.evStart: self.__evStart, iPlayableService.evEnd: self.__evEnd})
        return
    
    def __killExternalPlayer(self, ExternalPlayerToKill = ''):
        cmd = ''
        if ExternalPlayerToKill == '': 
            try:
                for proc in os.listdir('/proc'):
                    procExe = os.path.join('/proc', proc, 'exe')
                    if os.path.exists(procExe):
                        procRealPath = os.path.realpath(procExe)
                        if 'exteplayer3' in procRealPath:
                            safeSubprocessCMD('/usr/bin/killall -q exteplayer3')
                            break
            except Exception:
                pass
        else:
            safeSubprocessCMD('/usr/bin/killall -q %s' % ExternalPlayerToKill)
            self.ActiveExternalPlayer = ''

    def __restartServiceTimerCB(self):
        #print("[SLeventsWrapper.__restartServiceTimerCB] >>>")
        self.RestartServiceTimer.stop()
        if self.LastPlayedService is None:
            print("[SLeventsWrapper.__restartServiceTimerCB] self.LastPlayedService is None, stopping currently playing service")
            self.skipKillAt__evEnd = True
            self.LastPlayedService = self.session.nav.getCurrentlyPlayingServiceReference()
            self.session.nav.stopService()
            self.restartServiceTimerCBCounter = 0
            self.ExtPlayerStarted = False
            self.RestartServiceTimer.start(1000, True)
        else:
            #print("[SLeventsWrapper.__restartServiceTimerCB] self.LastPlayedService is NOT None")
            #waiting for exteplayer3 to start
            for proc in os.listdir('/proc'):
                try:
                    procExe = os.path.join('/proc', proc, 'exe')
                    if os.path.exists(procExe):
                        procRealPath = os.path.realpath(procExe)
                        #print("[SLeventsWrapper.__restartServiceTimerCB]", procRealPath)
                        if 'exteplayer3' in procRealPath:
                            self.ExtPlayerStarted = True
                            #print('[SLeventsWrapper.__restartServiceTimerCB] Found in',procRealPath)
                            break
                except Exception as e:
                    print("[SLeventsWrapper.__restartServiceTimerCB]  exception", str(e))
            if self.ExtPlayerStarted == False and self.restartServiceTimerCBCounter < 21:
                print("[SLeventsWrapper.__restartServiceTimerCB] waiting %s seconds for %s to start" % (self.restartServiceTimerCBCounter, self.ActiveExternalPlayer))
                self.restartServiceTimerCBCounter += 1
                self.RestartServiceTimer.start(1000, True)
            elif self.ExtPlayerStarted == True and self.restartServiceTimerCBCounter < 21:
                print("[SLeventsWrapper.__restartServiceTimerCB] %s started, waiting another second to enable E2 player to see EPG data" % self.ActiveExternalPlayer)
                self.restartServiceTimerCBCounter += 222
                self.RestartServiceTimer.start(1000, True)
            else:
                print("[SLeventsWrapper.__restartServiceTimerCB] %s started, enabling E2 player to see EPG data" % self.ActiveExternalPlayer)
                self.session.nav.playService(self.LastPlayedService)
                self.LastPlayedService = None
    
    def __evStart(self):
        print("[SLeventsWrapper.__evStart] >>>")
        if self.myCDM is None:
            try:
                import pywidevine.cdmdevice.privatecdm
                self.myCDM = pywidevine.cdmdevice.privatecdm.privatecdm()
            except ImportError:
                self.myCDM = False
        
        try:
            service = self.session.nav.getCurrentlyPlayingServiceReference()
            if not service is None:
                CurrentserviceString = service.toString()
                #print("[SLeventsWrapper]__evStart CurrentserviceString=", CurrentserviceString)
                serviceList = CurrentserviceString.split(":")
                print("[SLeventsWrapper.__evStart] serviceList=", serviceList)
                if len(serviceList) > 10:
                    url = serviceList[10].strip().lower()
                    if url == '':
                        self.__killExternalPlayer(self.ActiveExternalPlayer)
                        self.LastServiceString = ''
                    else:
                        if self.LastServiceString == CurrentserviceString:
                            print('[SLeventsWrapper.__evStart] LastServiceString = CurrentserviceString, nothing to do')
                            return
                        self.LastServiceString = CurrentserviceString
                        if url.startswith('http%3a//127.0.0.1'):
                            print('[SLeventsWrapper.__evStart] local URL (127.0.0.1), nothing to do')
                            return
                        elif self.myCDM != False and self.myCDM.doWhatYouMustDo(url):
                                self.ActiveExternalPlayer = 'exteplayer3'
                                return
                        elif url.startswith('http%3a//cdmplayer/'):
                            if self.deviceCDM is None: #tutaj, zeby bez sensu nie ladować jak ktos nie uzywa
                                try:
                                    import pywidevine.cdmdevice.cdmDevice
                                    self.deviceCDM = pywidevine.cdmdevice.cdmDevice.cdmDevice()
                                except ImportError:
                                    self.deviceCDM = False
                            if self.deviceCDM != False and self.deviceCDM.tryToDoSomething(url):
                                self.ActiveExternalPlayer = 'cdmeplayer3'
                                #tryToDoSomething take time to proceed and initiate player.
                                # so we need to ...
                                #   - mark this to properly manage __evEnd eventmap (if not managed, killed process & black screen)
                                #   - stop enigma player (if not stopped only back screen)
                                self.RestartServiceTimer.start(100, True)
                            return
                        elif url.startswith('http%3a//slplayer/'):
                            self.ActiveExternalPlayer = 'exteplayer3'
                            cmd2run = []
                            cmd2run.extend(['/usr/bin/killall -q cdmeplayer3;'])
                            cmd2run.extend(['/usr/bin/killall -q exteplayer3;'])
                            cmd2run.extend(['/usr/sbin/streamlink'])
                            cmd2run.extend(['-l','none'])
                            if os.path.exists('/iptvplayer_rootfs/usr/bin/exteplayer3'): #wersja sss jest chyba lepsza, jak mamy to ją użyjmy
                                cmd2run.extend(['-p','/iptvplayer_rootfs/usr/bin/exteplayer3'])
                            else:
                                cmd2run.extend(['-p','/usr/bin/exteplayer3'])
                            cmd2run.extend(['--player-http','--verbose-player',"'%s'" % url.replace('http%3a//slplayer/',''), 'best'])
                            safeSubprocessCMD(' '.join(cmd2run))
                            self.RestartServiceTimer.start(100, True)
                            return
                        else:
                            self.__killExternalPlayer(self.ActiveExternalPlayer)
        except Exception as e:
            print('[SLeventsWrapper.__evStart] exception:', str(e))

    def __evEnd(self):
        if 0:
            print("[SLeventsWrapper.__evEnd] >>> self.skipKillAt__evEnd=%s" % str(self.skipKillAt__evEnd))
            if not self.skipKillAt__evEnd:
                print("[SLeventsWrapper.__evEnd] >>> __killExternalPlayer run")
                self.RestartServiceTimer.stop()
                self.__killExternalPlayer(self.ActiveExternalPlayer)
                self.skipKillAt__evEnd = False
        return
