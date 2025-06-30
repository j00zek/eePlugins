from Components.config import config
from importlib import reload
from Plugins.Plugin import PluginDescriptor
from . import mygettext as _

import os, sys, subprocess, time


import Screens.Standby

DBG = True

def safeSubprocessCMD(myCommand):
    if DBG: print('[SLK] safeSubprocessCMD(%s)' % myCommand)
    with open("/proc/sys/vm/drop_caches", "w") as f: f.write("1\n") #for safety to not get GS due to lack of memory
    subprocess.Popen(myCommand, shell=True)

def SLconfigLeaveStandbyInitDaemon():
    print('[SLK] LeaveStandbyInitDaemon() >>>')
    safeSubprocessCMD('%s restart' % config.plugins.streamlinkSRV.binName.value)

def SLconfigStandbyCounterChanged(configElement):
    print('[SLK] standbyCounterChanged() >>>')
    if config.plugins.streamlinkSRV.StandbyMode.value == True:
        safeSubprocessCMD('streamlinkproxySRV stop;streamlinkproxySRV stop;killall -q exteplayer3')
    else:
        safeSubprocessCMD('killall -q exteplayer3')
    try:
        if SLconfigLeaveStandbyInitDaemon not in Screens.Standby.inStandby.onClose:
            Screens.Standby.inStandby.onClose.append(SLconfigLeaveStandbyInitDaemon)
    except Exception as e:
        print('standbyCounterChanged EXCEPTION: %s' % str(e))

# sessionstart
def sessionstart(reason, session = None):
    if os.path.exists("/tmp/StreamlinkConfig.log"):
        os.remove("/tmp/StreamlinkConfig.log")
    print("[SLK] sessionstart")
    if not os.path.exists('/usr/bin/exteplayer3'):
        print("[SLK] błąd brak zainstalowanego exteplayer3")
    if os.path.exists('/usr/sbin/streamlinkproxy'):
        print("[SLK] UWAGA !!! pakiet streamlinkproxy zainstalowany - to oznacza potencjalne problemy !!!")
    cmds = []
    cmds.append("[ `ps -ef|grep -v grep|grep -c streamlinkproxy` -gt 0 ] && killall streamlinkproxy >/dev/null")
    #cmds.append("/usr/lib/enigma2/python/Plugins/Extensions/StreamlinkConfig/bin/re-initiate.sh")
    cmds.append("[ `ps -ef|grep -v grep|grep -c streamlinkproxySRV` -gt 0 ] && streamlinkproxySRV stop")
    cmds.append("[ `ps -ef|grep -v grep|grep -c streamlinkSRV` -gt 0 ] && streamlinkSRV stop")
    cmds.append('killall -q streamlink')
    cmds.append('killall -q exteplayer3')
    cmds.append('killall -q ffmpeg')
    cmds.append('rm -f /tmp/ffmpeg-*')
    cmds.append('rm -f /tmp/streamlinkpipe-*')
    cmds.append('[ -e /tmp/stream.ts ] && rm -f /tmp/stream.ts')
    if config.plugins.streamlinkSRV.enabled.value:
        cmds.append("%s restart" % config.plugins.streamlinkSRV.binName.value)
    safeSubprocessCMD(';'.join(cmds))
    from Screens.Standby import inStandby
    if reason == 0 and config.plugins.streamlinkSRV.StandbyMode.value == True:
        print('[SLK] reason == 0 and StandbyMode enabled')
        config.misc.standbyCounter.addNotifier(SLconfigStandbyCounterChanged, initial_call=False)

def main(session, **kwargs):
    print("[SLK] main")
    session.open(SLK_Menu)

def Plugins(path, **kwargs):
    myList = [PluginDescriptor(name=_("Streamlink Configuration"), where = PluginDescriptor.WHERE_PLUGINMENU, icon="logo.png", fnc = main, needsRestart = False),
            PluginDescriptor(name="StreamlinkConfig", where = PluginDescriptor.WHERE_SESSIONSTART, fnc = sessionstart, needsRestart = False, weight = -1)
           ]
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
            Mlist.append(self.buildListEntry("Konfiguracja demona", "config.png",'menuDaemonConfig'))
            Mlist.append(self.buildListEntry("Dodaj/Usuń bukiet IPTV", "iptv.png",'menuAvailableIPTVbouquets'))
            Mlist.append(self.buildListEntry("Pobierz/Usuń bukiet IPTV kolegi Azman", "azman.png",'menuIPTVazman'))
            Mlist.append(self.buildListEntry("Zmień framework w serwisach IPTV", "folder.png",'menuIPTVframework'))
            Mlist.append(self.buildListEntry("Konfiguacja pilot.wp.pl", "wptv.png",'menuPilotWPpl'))
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
        elif selected == 'menuPilotWPpl':
            import Plugins.Extensions.StreamlinkConfig.menuPilotWPpl
            reload(Plugins.Extensions.StreamlinkConfig.menuPilotWPpl)
            self.session.openWithCallback(self.doNothing,Plugins.Extensions.StreamlinkConfig.menuPilotWPpl.StreamlinkConfiguration)
            return

    def doNothing(self, retVal = None):
        return
                
    def quit(self):
        self.close()
