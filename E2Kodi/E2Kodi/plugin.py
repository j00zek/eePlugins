from Components.config import config
from importlib import reload
from Plugins.Plugin import PluginDescriptor
from Plugins.Extensions.E2Kodi.version import Version
import os, subprocess
import Screens.Standby

print("[E2Kodi.plugin] v:", Version )

def safeSubprocessCMD(myCommand):
    with open("/proc/sys/vm/drop_caches", "w") as f: f.write("1\n") #for safety to not get GS due to lack of memory
    subprocess.Popen(myCommand, shell=True)

E2KodiLeaveStandbyEvent = False

def E2KodiLeaveStandbyActions():
    print('[E2KodiLeaveStandbyActions] >>>')
    global E2KodiLeaveStandbyEvent
    E2KodiLeaveStandbyEvent = True

def E2KodiConfigStandbyCounterChanged(configElement):
    #print('[E2KodiConfigStandbyCounterChanged] >>>')
    killCdmDevicePlayer()
    try:
        if E2KodiLeaveStandbyActions not in Screens.Standby.inStandby.onClose:
            Screens.Standby.inStandby.onClose.append(E2KodiLeaveStandbyActions)
    except Exception as e:
        print('[E2KodiConfigStandbyCounterChanged] EXCEPTION: %s' % str(e))

def killCdmDevicePlayer():
    print('[E2Kodi.killCdmDevicePlayer] >>>')
    retVal = False
    for pidFile in ['/var/run/cdmDevicePlayer.pid', '/var/run/emukodiCLI.pid', '/var/run/exteplayer3.pid']:
        if os.path.exists(pidFile):
            retVal = True
            pid = open(pidFile, 'r').readline().strip()
            try:
                if os.path.exists('/proc/%s' % pid):
                    os.kill(int(pid), signal.SIGTERM) #or signal.SIGKILL
                os.remove(pidFile)
            except Exception:
                safeSubprocessCMD('kill %s' % str(pid))
    return retVal

# sessionstart
def sessionstart(reason, session = None):
    from Screens.Standby import inStandby
    if reason == 0:
        config.misc.standbyCounter.addNotifier(E2KodiConfigStandbyCounterChanged, initial_call=False)
        killCdmDevicePlayer()
        cmds = ''
        #if os.path.exists('/usr/sbin/emukodiSRV'): cmds = 'emukodiSRV restart;\n'
        cmds += 'wget -q https://raw.githubusercontent.com/azman26/EPGazman/main/azman_channels_mappings.py -O /usr/lib/enigma2/python/Plugins/Extensions/E2Kodi/azman_channels_mappings.py'
        safeSubprocessCMD(cmds)
    global E2KodiEventsInstance
    if E2KodiEventsInstance is None:
        E2KodiEventsInstance = E2KodiEvents(session)

def main(session, **kwargs):
    import Plugins.Extensions.E2Kodi.addons
    reload(Plugins.Extensions.E2Kodi.addons)
    session.open(Plugins.Extensions.E2Kodi.addons.E2Kodi_Menu)

def Plugins(path, **kwargs):
    myList = [PluginDescriptor(name="E2Kodi", where = PluginDescriptor.WHERE_PLUGINMENU, icon="logo.png", fnc = main, needsRestart = False),
              PluginDescriptor(name="E2Kodi", where = PluginDescriptor.WHERE_EXTENSIONSMENU, icon="logo.png", fnc = main, needsRestart = False),
              PluginDescriptor(name="E2Kodi", where = PluginDescriptor.WHERE_SESSIONSTART, fnc = sessionstart, needsRestart = False, weight = -1)
            ]
    return myList

############################################# SLeventsWrapper #################################
E2KodiEventsInstance = None

from Components.ServiceEventTracker import ServiceEventTracker#, InfoBarBase
from enigma import iPlayableService#, eServiceCenter, iServiceInformation
#import ServiceReference
from enigma import eTimer
import time, signal, traceback

class E2KodiEvents:
    def __init__(self, session):
        #print("[E2KodiEvents.__init__] >>>")
        self.session = session
        self.service = None
        self.onClose = []
        self.myCDM = None
        self.deviceCDM = None
        self.runningProcessName = ''
        self.ExtPlayerPID = 0
        self.LastServiceString = ""
        self.RestartServiceTimer = eTimer()
        self.RestartServiceTimer.callback.append(self.__restartServiceTimerCB)
        self.LastPlayedService = None
        self.Disable__evEnd = False
        self.__event_tracker = ServiceEventTracker(screen=self, eventmap={iPlayableService.evStart: self.__evStart,
                                                                          iPlayableService.evEnd: self.__evEnd
                                                                          })
        return

    def __killRunningPlayer(self):
        print("[E2KodiEvents.__killRunningPlayer] >>>")
        self.RestartServiceTimer.stop()
        self.LastPlayedService = None
        if not self.deviceCDM is None:
            self.deviceCDM.stopPlaying() #wyłącza playera i czyści bufor dvb, bez tego  mamy 5s opóźnienia
        killCdmDevicePlayer()

    def __restartServiceTimerCB(self):
        #print("[E2KodiEvents.__restartServiceTimerCB] >>>")
        self.RestartServiceTimer.stop()
        if self.LastPlayedService is None:
            print("[E2KodiEvents.__restartServiceTimerCB] self.LastPlayedService is None, stopping currently playing service")
            self.LastPlayedService = self.session.nav.getCurrentlyPlayingServiceReference()
            self.session.nav.stopService()
            self.restartServiceTimerCBCounter = 20
            self.ExtPlayerPID = 0
            self.RestartServiceTimer.start(2000, True)
            self.Disable__evEnd = False
        else:
            #waiting for exteplayer3 to start
            if os.path.exists('/var/run/cdmDevicePlayer.pid'):
                if self.ExtPlayerPID == 0:
                    self.ExtPlayerPID = int(open('/var/run/cdmDevicePlayer.pid', 'r').readline().strip())
                    self.RestartServiceTimer.start(1000, True) # dajemy czas na załadowanie wszystkiego
                elif os.path.exists(os.path.join('/proc', str(self.ExtPlayerPID))):
                    print("[E2KodiEvents.__restartServiceTimerCB] cdmDevicePlayer uruchomiony, włączam E2 żeby widzieć dane EPG")
                    self.session.nav.playService(self.LastPlayedService)
                    self.LastPlayedService = None
                else:
                    print("[E2KodiEvents.__restartServiceTimerCB] cdmDevicePlayer niespodziewanie wyłączony")
            elif os.path.exists('/var/run/emukodiCLI.pid'):
                if not os.path.exists('/var/run/exteplayer3.pid'):
                    if self.restartServiceTimerCBCounter > 0:
                        print("[E2KodiEvents.__restartServiceTimerCB] czekam jeszcze %s sekund na uruchomienie exteplayer3" % self.restartServiceTimerCBCounter)
                        self.restartServiceTimerCBCounter -= 1
                        self.RestartServiceTimer.start(1000, True)
                    else:
                        print("[E2KodiEvents.__restartServiceTimerCB] czekam jeszcze %s sekund ma uruchomienie exteplayer3" % self.restartServiceTimerCBCounter)
                else:
                    print("[E2KodiEvents.__restartServiceTimerCB] exteplayer3 uruchomiony, włączam E2 żeby widzieć dane EPG")
                    self.session.nav.playService(self.LastPlayedService)
                    self.LastPlayedService = None
            else:
                print("[E2KodiEvents.__restartServiceTimerCB] emukodiCLI niespodziewanie wyłączony")

    def __evEnd(self):
        if self.Disable__evEnd:
            print("[E2KodiEvents.__evEnd] disabled")
        else:
            print("[E2KodiEvents.__evEnd] >>>")
            self.__killRunningPlayer()#zatrzymuje uruchomiony z kontrolą podprocess odtwarzacza
            self.LastServiceString = ''
        
    def __evStart(self):
        print("[E2KodiEvents.__evStart] >>>")
        try:
            service = self.session.nav.getCurrentlyPlayingServiceReference()
            if not service is None:
                CurrentserviceString = service.toString()
                print("[E2KodiEvents]__evStart CurrentserviceString=", CurrentserviceString)
                global E2KodiLeaveStandbyEvent
                if E2KodiLeaveStandbyEvent:
                    E2KodiLeaveStandbyEvent = False
                elif self.LastServiceString == CurrentserviceString:
                    #print('[E2KodiEvents.__evStart] LastServiceString = CurrentserviceString, nothing to do')
                    return
                self.LastServiceString = CurrentserviceString
                self.__killRunningPlayer()#zatrzymuje uruchomiony z kontrolą podprocess odtwarzacza
                if not ':http%3a//cdmplayer' in CurrentserviceString:
                    #print('[E2KodiEvents.__evStart] no http%3a//cdmplayer service, nothing to do')
                    return
                else:
                    serviceList = CurrentserviceString.split(":")
                    #print("[E2KodiEvents.__evStart] serviceList=", serviceList)
                    url = serviceList[10].strip()
                    if url.startswith('http%3a//cdmplayer/'):
                        print("[E2KodiEvents.__evStart] url = '%s'" % url)
                        if self.deviceCDM is None: #tutaj, zeby bez sensu nie ladować jak ktos nie ma/nie uzywa
                            try:
                                import pywidevine.cdmdevice.cdmDevice
                                self.deviceCDM = pywidevine.cdmdevice.cdmDevice.cdmDevice()
                                print("[E2KodiEvents.__evStart] deviceCDM loaded")
                            except ImportError:
                                self.deviceCDM = False
                                print("[E2KodiEvents.__evStart] EXCEPTION loading deviceCDM")
                        if self.deviceCDM != False:
                            if not self.deviceCDM.doWhatYouMustDo(url):
                                #tryToDoSomething take time to proceed and initiate player.
                                # so we need to ...
                                #   - mark this to properly manage __evEnd eventmap (if not managed, killed process & black screen)
                                #   - stop enigma player (if not stopped only back screen)
                                self.deviceCDM.tryToDoSomething(url)
                                self.Disable__evEnd = True
                                self.RestartServiceTimer.start(100, True)
        except Exception as e:
            print('[E2KodiEvents.__evStart] EXCEPTION:', str(e))
            print(traceback.format_exc())
