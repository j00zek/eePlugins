# -*- coding: utf-8 -*-
# @j00zek 2015-2022
# based on some VTI concepts
#
from __future__ import absolute_import #zmiana strategii ladowania modulow w py2 z relative na absolute jak w py3

from Components.ActionMap import ActionMap
from Components.Console import Console as ComConsole
from Components.j00zekComponents import isINETworking, getImageType
from Components.j00zekModHex2strColor import clr
from Components.Label import Label
from Components.MenuList import MenuList
from Components.ScrollLabel import ScrollLabel 
from Components.Sources.List import List
from Components.Sources.StaticText import StaticText
from enigma import eConsoleAppContainer
from Screens.MessageBox import MessageBox
from os import listdir, statvfs, popen as os_popen, system as os_system, remove as os_remove, path as os_path
from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from sys import version_info
from Tools.LoadPixmap import LoadPixmap
from Tools.Directories import *

from Plugins.Extensions.j00zekOPKGmgr.__init__ import *
_ = mygettext
from Plugins.Extensions.j00zekOPKGmgr.Jconsole import Jconsole
############################################

myDEBUG = False

myDEBUGfile = '/tmp/j00zekOPKGmgr.log'
append2file=False

PyMajorVersion = version_info.major

def printDEBUG( callingFunction , myText = ''):
    global append2file
    if myDEBUG:
        print ("%s: %s" % (callingFunction , myText))
        try:
            if append2file == False:
                append2file = True
                f = open(myDEBUGfile, 'w')
            else:
                f = open(myDEBUGfile, 'a')
            f.write("%s: %s\n" % (callingFunction , myText))
            f.close
        except:
            pass

def feedsStatus():
    try:
        from urllib import urlopen
        import socket
        socket.setdefaulttimeout(3)
        d = urlopen("http://openvix.co.uk/TrafficLightState.php")
        trafficText = d.read()
    except Exception as e:
        printDEBUG("%s" % str(e))
        trafficText = "unknown"
    if trafficText == 'stable': trafficText = clr['G']
    elif trafficText == 'updating': trafficText = clr['O']
    elif trafficText == 'unstable': trafficText = clr['R']
    else: trafficText = clr['Gray']
        
    return trafficText

def areFeedsRunning():
    retVal = False
    servers = []
    if os_path.exists('/etc/opkg'):
        for filename in listdir('/etc/opkg'):
            fline=open('/etc/opkg/' + filename).readline().strip()
            if fline.startswith('src/gz'):
                try:
                    srv = fline.split('http://')[1].split('/')[0]
                    if srv not in servers:
                      servers.append(srv)
                      #print srv
                except Exception:
                    pass
        for srv in servers:
            if isINETworking(srv, 80):
                retVal = True
                break
            else:
                return False
    return retVal            
      
############################################

class Jopkg(Screen):
    skin = """
    <screen name="Jopkg" position="center,center" size="700,500" title="Jopkg" >
        <widget name="key_yellow" position="10,450" zPosition="2" size="400,22" valign="center" halign="left" font="Regular;20" transparent="1" foregroundColor="yellow" />
        <widget name="key_red" position="10,473" zPosition="2" size="130,22" valign="center" halign="left" font="Regular;20" transparent="1" foregroundColor="red" />
        <widget name="key_blue" position="520,450" zPosition="2" size="170,22" valign="center" halign="right" font="Regular;20" transparent="1" foregroundColor="blue" />
        <widget name="key_green" position="260,473" zPosition="2" size="430,22" valign="center" halign="right" font="Regular;20" transparent="1" foregroundColor="green" />

        <widget source="list" render="Listbox" position="5,5" size="690,440" scrollbarMode="showOnDemand">
            <convert type="TemplatedMultiContent">
                {"template": [
                              MultiContentEntryText(pos = (55, 2), size = (600, 24), font=0, flags = RT_HALIGN_LEFT|RT_VALIGN_CENTER, text = 0), # index 2 is the description
                              MultiContentEntryText(pos = (55, 26), size = (600, 16), font=1, flags = RT_HALIGN_LEFT|RT_VALIGN_CENTER, text = 2), # index 0 is the name
                              MultiContentEntryText(pos = (55, 42), size = (600, 16), font=1, flags = RT_HALIGN_LEFT|RT_VALIGN_CENTER, text = 1), # index 2 is the description
                              MultiContentEntryPixmapAlphaTest(pos = (5, 2), size = (48, 48), png = 4), # index 4 is the status pixmap
                              MultiContentEntryPixmapAlphaTest(pos = (55, 59), size = (652, 2), png = 5), # index 4 is the div pixmap
                              ],
                "fonts": [gFont("Regular", 22),gFont("Regular", 14)],
                "itemHeight": 61
                }
            </convert>
        </widget>
        <widget name="whatUPDATED"  position="5,75" size="690,330" font="Regular;18" transparent="1"/>

    </screen>"""

    def __init__(self, session, args=None):
        Screen.__init__(self, session)
        self.session = session
        
        printDEBUG( '__init__', getImageType() )
        if getImageType() in ('openatv', 'openatv5.3', 'openvix'):
            printDEBUG( 'feedstatus', feedsStatus() )
            self.title = feedsStatus() + _("OPKG manager")
        else:
            self.title = _("OPKG manager")
        self.setTitle(self.title )

        self.list = []
        self.SelectedIndex = None
        self.prev_running_service = None
        self.packages = []
        self.installedpackages = []
        self.upgradeablepackages = []
        self.ActiveFilterID = 0
        self.ActiveFilter = ""
        self.LocalFileName = ""
        #self.changeList = []
        self.maxSize = 8000000
        self.maxPackages = 15
        if self.getFreeSpace('/var/cache') > self.maxSize * 3:
            self.CacheDir = "/var/cache"
        elif self.getFreeSpace('/media/data') > self.maxSize * 4:
            self.CacheDir = "/media/data"
        elif self.getFreeSpace('/hdd') > self.maxSize * 4:
            self.CacheDir = "/hdd"
        else:
            self.CacheDir = "/var/cache"
            if fileExists('/hdd/epg.dat'):
                os_remove('/hdd/epg.dat')
        
        self.firstRun = True
        self.MainMenu = True
        self.pushUpgrade = True
        self.BlockedInstall = False
        #self.IPTVfullInstalled = False
        self.BlockedInput = True
        self.packages2upgrade = 0
        self.keyGreenAction = ""
        self.keyYellowAction = ""
        self.keyBlueAction = ""
        self.actionInfo = ""
        self.SkinSelectorInstalled = 0
        self.changed = False #zmiana na True kiedy cokolwiek zainstalujemy
        self.Console = ComConsole()
        self.divpng = LoadPixmap(cached = True, path = resolveFilename(SCOPE_SKIN_IMAGE, 'skin_default/div-h.png'))
        self.goinstalledpng = LoadPixmap(cached = True, path = PluginPath + 'icons/install.png')
        self.goremovepng = LoadPixmap(cached = True, path = PluginPath + 'icons/remove.png')
        self.gousbpng = LoadPixmap(cached = True, path = PluginPath + 'icons/opkg_local.png')
        self.installedpng = LoadPixmap(cached = True, path = PluginPath + 'icons/installed.png')
        self.upgradeablepng = LoadPixmap(cached = True, path = PluginPath + 'icons/upgradeable.png')
        
        self["list"] = List(self.list)

        self["key_red"] = Label(_("Refresh list"))
        self["key_green"] = Label()
        self["key_blue"] = Label()
        self["key_yellow"] = Label()
        self["whatUPDATED"] = ScrollLabel()
        
        self["actions"] = ActionMap(["OkCancelActions", "ColorActions", "DirectionActions"],
            {
                "cancel": self.keyCancel,
                "ok": self.doAction,
                "red": self.keyRed,
                "green": self.doAction,
                "yellow": self.keyYellow,
                "blue": self.keyBlue,
                "pageUp": self["whatUPDATED"].pageUp,
                "pageDown": self["whatUPDATED"].pageDown 
            }, -2)

        self.onLayoutFinish.append(self.layoutFinished)
        self.onShown.append(self.checkFreeSpace)
        if self.selectionChanged not in self['list'].onSelectionChanged:
            self['list'].onSelectionChanged.append(self.selectionChanged)

    def runCmd(self, cmd):
        printDEBUG( "runCmd" , cmd )
        self.cmd.appClosed.append(self.cmdFinished)
        self.cmd.dataAvail.append(self.cmdData)
        if self.cmd.execute(self.ipkg + " " + cmd):
            self.cmdFinished(-1)
       
    def cmdData(self, data):
        printDEBUG( "cmdData" , data )
        if self.cache is None:
            self.cache = data
        else:
            self.cache += data

        if '\n' in data:
            splitcache = self.cache.split('\n')
            if self.cache[-1] == '\n':
                iteration = splitcache
                self.cache = None
            else:
                iteration = splitcache[:-1]
                self.cache = splitcache[-1]
            for mydata in iteration:
                if mydata != '':
                    self.parseLine(mydata)

    def cmdFinished(self, retval):
        self.callCallbacks(10)
        self.cmd.appClosed.remove(self.cmdFinished)
        self.cmd.dataAvail.remove(self.cmdData)

    def layoutFinished(self, ret = 0):
        printDEBUG( "layoutFinished" , "" )
        self.setTitle(self.title )
        self.refreshLists()
        if self.firstRun == True:
            self['key_green'].setText(_('Select option'))
            #self.firstRun = False
            
    def upgradeAll(self, ret):
        if ret is True:
            self.changed = True
            self.session.openWithCallback(self.refreshLists ,Jconsole, title = _("Upgrading all packages...." ), cmdlist = [ self.keyGreenAction ])
        return
        
    def doManualInstall(self, localIPKfile ):
        if localIPKfile:
            self.LocalFileName = localIPKfile
            print(self.LocalFileName)
            self.BlockedInput = False
            self.keyGreenAction = 'opkg install "%s"' % localIPKfile
            self.doAction()
        else:
            self.LocalFileName = ''
            self.keyGreenAction = ''

    def InfoBoxReturn(self, ret=0): #from doAction
        printDEBUG( "InfoBoxReturn" , "self.keyGreenAction == %s" % self.keyGreenAction )
        self.keyGreenAction = ''
        return

    def doAction(self):
        self.SelectedIndex = self["list"].getIndex()
        printDEBUG( "doAction" , "self.keyGreenAction = '%s'" % self.keyGreenAction )
        if self.BlockedInput == True and self.keyGreenAction != 'LocalPackage':
            printDEBUG( "doAction" , "self.BlockedInput == True" )
            return
        with open("/proc/sys/vm/drop_caches", "w") as f: f.write("1\n")
        if self.keyGreenAction == 'LocalPackage':
            printDEBUG( "doAction" , "self.keyGreenAction == 'LocalPackage':" )
            from filebrowserwidget import DirectorySelectorWidget
            self.session.openWithCallback(self.doManualInstall, DirectorySelectorWidget, currDir='/', title=_("Select package") , selectFiles = True )
            return
        elif self.MainMenu == True and self.LocalFileName == "" and not self.keyGreenAction.endswith('UpgradeAll'):
            printDEBUG( "doAction" , "self.MainMenu == True and self.LocalFileName == "" not self.keyGreenAction.endswith('UpgradeAll')" )
            #self.ActiveFilter = ""
            self.MainMenu = False
            self.refreshLists()
            return
        elif self.keyGreenAction != '':
            printDEBUG( "doAction" , "self.keyGreenAction = '%s'" % self.keyGreenAction )
            current = self['list'].getCurrent()
            if current[0] == '':
                printDEBUG( "doAction" , "current[0] = ''" )
                return
            
            #>>>>> Usuwanie pakietów...
            if self.keyGreenAction.find("remove") > 0:
                tekst=_("Are you sure, you want delete % package?") % current[0]

            #>>>>> przy za malej ilosci pamieci pozwalamy jedynie na remove...
            elif self.BlockedInstall == True:
                free_flash_space = self.getFreeSpace('/')
                human_free_space = free_flash_space / 1048576
                msg = _('Only %d MB left!!!\nAt least 8MB is required to safely install and upgrade packages.') % human_free_space
                self.session.openWithCallback(self.InfoBoxReturn, MessageBox,msg,  type = MessageBox.TYPE_INFO, timeout = 10)
                return

            #>>>>> upgrade wszystkiego...
            elif self.keyGreenAction == ('UpgradeAll'):
                if self.packages2upgrade > self.maxPackages and self.getFreeSpace(self.CacheDir) < self.maxSize * 3: #ze jest wolnego 8MB to juz wiemy
                    self.session.openWithCallback(self.close, MessageBox,_("Too many packages and too small free space for upgrade!!!" ),  type = MessageBox.TYPE_INFO, timeout = 10)
                    return
                else:
                    self.session.openWithCallback(self.doActionFullUpdate, MessageBox,_("Do you want to upgrade all packages?"),  type = MessageBox.TYPE_YESNO)
                    return

            #>>>>> upgrade konkretnego pakietu...
            elif self.keyGreenAction.startswith('opkg upgrade'):
                tekst=_("Do you want to upgrade %s package?") % current[0]

            #>>>>> wszystkie inne przypadki
            else:
                #sprawdzmy, czy mamy odpowiednio wolną przestrzeń
                try:
                    result = os_popen("opkg info %s | grep -m 1 '^Size:'  | cut -d ' ' -f2" % current[0])
                except:
                    result = 'ERROR' 
                sizetxt="unknown"
                if result != 'ERROR':
                    for x in result.readlines():
                        print("OPKG manager, packet size: %s" % x)
                        x = x.strip()
                        if x.isdigit():
                            size = int(x)
                            sizetxt="%dKB" % int(size/1024)
                if self.keyGreenAction.find("install") > 0:
                    if self.LocalFileName != "":
                        tekst=_("Are you sure to install %s package?") % self.LocalFileName
                    else:
                        tekst=_("Are you sure to install %s package with %s size?") % (current[0],sizetxt)
                else:
                    tekst=_("Do you want to run '%s'? (package size %s)") % (self.keyGreenAction,sizetxt)
                if self.SkinSelectorInstalled == 0 and self.keyGreenAction.find("enigma2-skin-") > 0: # dodajemy skinSelektor
                    self.keyGreenAction += " enigma2-plugin-skinselector"
            #finalnie wykonujemy akcje
            if None != tekst:
                self.session.openWithCallback(self.doActionAfterYESNO, MessageBox, tekst, type = MessageBox.TYPE_YESNO)
            
    def doActionAfterYESNO(self, ret = True ):
        if self.keyGreenAction != '' and ret is True:
            printDEBUG( "doActionAfterYESNO" , "self.keyGreenAction = '%s' and ret is True" % self.keyGreenAction)
            self.changed = True
            self.session.openWithCallback(self.post_doAction_check_TMPUPDsh ,Jconsole, title = "%s" % self.keyGreenAction, cmdlist = [ self.keyGreenAction ])
        return

    def doActionFullUpdate(self, ret):
        if ret is True:
            self.prev_running_service = self.session.nav.getCurrentlyPlayingServiceReference()
            self.session.nav.stopService()
            runlist = []
            runlist.append('sync')
            runlist.append('opkg --cache %s upgrade' % self.CacheDir)
            runlist.append('rm -f %s/*.ipk' % self.CacheDir)
            runlist.append('sync')
            #runlist.append('rm -f /var/opkg/FullUpdate')
            self.session.openWithCallback(self.post_doAction_check_TMPUPDsh ,Jconsole, title = _("Upgrading all packages..."), cmdlist = runlist)
            self.keyGreenAction = ''
            self.changed = True
        return
        
    def post_doAction_check_TMPUPDsh(self):
        if self.prev_running_service:
            self.session.nav.playService(self.prev_running_service)
        if pathExists("/tmp/upd.sh"):
            printDEBUG( "post_doAction_check_TMPUPDsh" , "pathExists('/tmp/upd.sh')" )
            self.session.openWithCallback(self.refreshLists ,Jconsole, title = _("Post upgrade cleanup..."), cmdlist = [ "/tmp/upd.sh" ])
        else:
            self.refreshLists()
    
    def keyRed(self):
        if self.BlockedInput == True:
            return
        printDEBUG( "keyRed" , "calling self.refreshLists()" )
        self.pushUpgrade = False
        self.firstRun = False
        self.refreshLists()
        return
        
    def keyBlue(self):
        if self.BlockedInput == True:
            return
        printDEBUG( "keyBlue" , self.keyBlueAction )
        if self.keyBlueAction != '':
            self.SelectedIndex = self["list"].getIndex()
            self.session.openWithCallback(self.refreshLists ,Jconsole, title = "%s" % self.keyBlueAction, cmdlist = [ self.keyBlueAction ])
        return

    def keyYellow(self):
        if self.BlockedInput == True:
            return
        printDEBUG( "keyYellow" , self.keyYellowAction )
        if self.keyYellowAction != '':
            self.SelectedIndex = self["list"].getIndex()
            self.session.openWithCallback(self.refreshLists ,Jconsole, title = "%s" % self.keyYellowAction, cmdlist = [ self.keyYellowAction ])
        return

    def keyYellowEnd(self, ret = 0):
        return
        
    def keyCancel(self, ret = 0):
        if self.Console is not None:
            printDEBUG( "keyCancel" , "self.Console is not None" )
            if len(self.Console.appContainers):
                for name in self.Console.appContainers.keys():
                    printDEBUG( "keyCancel" , "killing %s" % name )
                    self.Console.kill(name)
        if self.MainMenu == False:
            printDEBUG( "keyCancel" , "self.MainMenu == False" )
            self.MainMenu = True
            self.refreshLists()
            return
        elif self.changed == True:
            printDEBUG( "keyCancel" , "self.changed == True" )
            self.session.openWithCallback(self.keyCancelEnd, MessageBox,_("After changes in opkg, tuner has to be restarted.\n Restart now?"),  type = MessageBox.TYPE_YESNO)
        else:
            self.close()
            
    def keyCancelEnd(self, ret):
        #some cleaning just in case
        with open("/proc/sys/vm/drop_caches", "w") as f: f.write("1\n") 
        self.LocalFileName = None
        self.list = None
        self['list'].setList([])
        self["list"].setIndex(0)
        self["whatUPDATED"].setText("")
        self.SelectedIndex=None
        self.packages = None
        self.installedpackages = None
        self.upgradeablepackages = None
        self.Console = None
        self.divpng = None
        self.goinstalledpng = None
        self.goremovepng = None
        self.gousbpng = None
        self.installedpng = None
        self.upgradeablepng = None
        
        if ret == True:
            from Components.config import config
            try: # this is for openPLI to NOT put tuner into sleep mode
                config.misc.RestartUI.value = True
                config.misc.RestartUI.save()
            except: pass
            from enigma import quitMainloop
            quitMainloop(2)
        else:
            self.close()
        
    def getFreeSpace(self, mountpoint):
        if fileExists(mountpoint):
            stat_info = statvfs(mountpoint)
            free_flash_space = stat_info.f_bfree * stat_info.f_bsize
            return free_flash_space
        else:
            return 0
    
    def checkFreeSpace(self):
        printDEBUG( "checkFreeSpace" , "" )
        self.onShown.remove(self.checkFreeSpace)
        free_flash_space = self.getFreeSpace('/')
        if free_flash_space < self.maxSize:
            self.BlockedInstall = True
            human_free_space = free_flash_space / 1048576
            msg = _('Only %d MB left!!!\nAt least 8MB is required to safely install and upgrade packages.') % human_free_space
            msg += _('Remove some packages, or upgade from console!')
            self.session.openWithCallback(self.checkFreeSpaceEnd, MessageBox, msg,  MessageBox.TYPE_INFO, timeout = 5)

    def checkFreeSpaceEnd(self, ret = 0):
        return
        
#>>>>>>>>>>>>>>>>>>>>>>>>>  refreshLists main entry
    def refreshLists(self):
        def errorMENU(errorID=992):
            printDEBUG( "refreshLists_errorMENU" , "no network connection" )
            if len(self.list) >=1:
                printDEBUG( "refreshLists" , "len(self.list) >=1" )
                self.list.pop(-1)
            if errorID == 991:
                self.list.append((_('ERROR connecting to the internet'), '', _('OPKG server does not response on pings :('), '', self.goremovepng, self.divpng))
            if errorID == 992:
                self.list.append((_('ERROR connecting to OPKG'), '', _('Neigther internet nor service is working :('), '', self.goremovepng, self.divpng))
            else:
                self.list.append((_('ERROR updating OPKG'), '', _("'opkg update' command returned an error %i :(") % errorID, '', self.goremovepng, self.divpng))
            self.list.append((_("Install local packet") , " ", _("You will be later prompted for file selection."), 'InstallLocal', self.gousbpng, self.divpng))
            self['list'].setList(self.list)
            self['key_red'].hide()
            self['key_green'].hide()
            self['key_yellow'].hide()
            self['key_blue'].hide()

        def refreshLists_opkg_update( result = None, retval = 992, extra_args = None):
            printDEBUG( "refreshLists_opkg_update" , "retval:%i" % retval )
            if retval != 0:
                errorMENU(retval)
            else:
                self.firstRun = False
                self.refreshListsmain()

        def refreshLists_firstRun_doWeHaveNetwork( result, retval, extra_args = None):
            printDEBUG( "refreshLists_firstRun_doWeHaveNetwork" , "retval:%i" % retval )
            if retval != 0: 
                errorMENU(991)
            else:
                if pathExists('/var/lib/opkg/lock'):
                    os_system('killall -9 opkg 2>/dev/null;killall -9 wget 2>/dev/null;sleep 1')
                self.Console.ePopen('opkg update', refreshLists_opkg_update )
                
        printDEBUG( "refreshLists" , "main entry" )
        if pathExists("/tmp/upd.sh"):
            os_remove("/tmp/upd.sh")
        with open("/proc/sys/vm/drop_caches", "w") as f: f.write("1\n")
        self.LocalFileName = ''
        self.list = []
        self['list'].setList(self.list)
        self["whatUPDATED"].setText("")
        if self.firstRun == True:
            printDEBUG( "refreshLists" , "self.firstRun = True" )
            self.list.append((_('Package list update'), '', _('Trying to download a new packetlist. Please wait...'), '', self.goinstalledpng, self.divpng))
            self['list'].setList(self.list)
            
            if areFeedsRunning():
                refreshLists_firstRun_doWeHaveNetwork(None, 0)
            else:
                errorMENU(992)
        else:
            self.refreshListsmain()
            
    def setCurrentIndex(self):
        if self.SelectedIndex is not None and len(self["list"].list) > self.SelectedIndex:
            self["list"].setIndex(self.SelectedIndex)
        else:
            self["list"].setIndex(0)
            
#>>>>>  refreshListsmain run when all above tests went correctly
    def refreshListsmain(self):
        printDEBUG( "refreshListsmain" , "enter" )
        self.BlockedInput = True
        if len(self.list) >=1:
            self.list.pop(-1)
        if self.MainMenu == True:
            self.refreshLists_MainMenu()
        else:
            #printDEBUG( "refreshListsmain" , "enter" )
            #with open("/proc/sys/vm/drop_caches", "w") as f: f.write("1\n")
            self.Console.ePopen('opkg list-upgradable', self.refreshLists_Packages_Got_upgadable )

    def refreshLists_MainMenu(self):
        printDEBUG( "refreshLists_MainMenu" , "enter" )
        with open("/proc/sys/vm/drop_caches", "w") as f: f.write("1\n")
        self.Console.ePopen('opkg list-upgradable', self.refreshLists_MainMenu_upgradeablepackages )

    def refreshLists_MainMenu_upgradeablepackages(self, result, retval, extra_args = None):
        def build_MainMenu():
            printDEBUG( "build_MainMenu" , "self.list.appends..." )
            if self.packages2upgrade > 0:
                self.list.append((_("Upgrade packages" ), '', _("Recommended update installed packages"), 'UpgradeAll', self.upgradeablepng, self.divpng))
            self.list.append((_("Show system plugins only") , '' , '', ['-systemplugins-',], LoadPixmap(cached=True, path=PluginPath + 'icons/opkg_plugin.png'), self.divpng))
            self.list.append((_("Show extension plugins only") , '' , '', ['-extensions-',], LoadPixmap(cached=True, path=PluginPath + 'icons/opkg_plugin.png'), self.divpng))
            self.list.append((_("Show j00zek's plugins only") , '' , '', ['enigma2-plugin-extensions--j00zeks-','enigma2-plugin-systemplugins--j00zeks-','system-addon--j00zeks-',], LoadPixmap(cached=True, path=PluginPath + 'icons/opkg_plugin.png'), self.divpng))
            self.list.append((_("Show j00zek's skins only") , '' , '', ['enigma2-plugin-skins--j00zeks-',], LoadPixmap(cached=True, path=PluginPath + 'icons/opkg_plugin.png'), self.divpng))
            self.list.append((_("Show Black Harmony components only") , '' , '', ['e2-j00zeks-bh-addon-'], LoadPixmap(cached=True, path=PluginPath + 'icons/opkg_plugin.png'), self.divpng))
            self.list.append((_("Show animated picons only") , '' , '', ['enigma2-plugin-picons--j00zeks-',], LoadPixmap(cached=True, path=PluginPath + 'icons/opkg_plugin.png'), self.divpng))
            self.list.append((_("show picons only" ) , '' , '', ['-picon',], LoadPixmap(cached=True, path=PluginPath + 'icons/opkg_picon.png'), self.divpng))
            self.list.append((_("Show KODI addons only") , '' , '', ['kodi-addon-','kodi-addon--j00zeks-','enigma2-plugin-extensions-kodi',], LoadPixmap(cached=True, path=PluginPath + 'icons/opkg_plugin.png'), self.divpng))
            self.list.append((_("Show openPLI skins only" ) , '' , '', ['-skin',], LoadPixmap(cached=True, path=PluginPath + 'icons/opkg_skin.png'), self.divpng))
            self.list.append((_("show fonts only" ) , '' , '', ['font',], LoadPixmap(cached=True, path=PluginPath + 'icons/opkg_fonts.png'), self.divpng))
            self.list.append((_("show oscam packages only" ) , '' , '', ['oscam',], LoadPixmap(cached=True, path=PluginPath + 'icons/opkg_softcam.png'), self.divpng))
            self.list.append((_("show Python modules only" ) , '' , '', ['python-','python3-',], LoadPixmap(cached=True, path=PluginPath + 'icons/opkg_python.png'), self.divpng))
            self.list.append((_("Show DVB USB modules only" ) , '' , '', ['dvb-usb',], LoadPixmap(cached=True, path=PluginPath + 'icons/opkg_dvbt.png'), self.divpng))
            self.list.append((_("Show all packages" ) , '' , '', '', LoadPixmap(cached=True, path=PluginPath + 'icons/opkg_all.png'), self.divpng))
            self.list.append((_("Install local packet" ) , " ", _("You will be later prompted for file selection." ), 'InstallLocal', self.gousbpng, self.divpng))
            self['list'].setList(self.list)
            self.setCurrentIndex()
            self.BlockedInput = False
            
        def build_UpgradeMenu( result, retval, extra_args = None): 
            printDEBUG( "build_UpgradeMenu" , "..." )
            self.list.append((_('Upgrade packages' ), '', _('Recommended update installed packages' ), 'UpgradeAll', self.upgradeablepng, self.divpng))
            self['list'].setList(self.list)
            self.BlockedInput = False
            isRelease=False
            self["whatUPDATED"].setText(result)
            self.keyGreenAction = 'UpgradeAll'
            #print result
            
        self.list = []
        #printDEBUG( "refreshLists_MainMenu_upgradeablepackages" , "extra_args:'%s' , result:%s , retval:%i" % (extra_args,result, retval) )
        self.upgradeablepackages = self.getOPKGlist( SameNazwy = True, lista = result )
        self.packages2upgrade = len(self.upgradeablepackages)
        if self.packages2upgrade > 0 and self.pushUpgrade == True:
            printDEBUG( "build_UpgradeMenu" , "list of packages" )
            tmptxt=''
            for x in result.splitlines():
                if PyMajorVersion == 3:
                    try: x = x.decode('utf-8')
                    except Exception: pass
                if not x.startswith('Not selecting'):
                    tmptxt += x[:x.find(' - ')] + '\n'
            self["whatUPDATED"].setText(tmptxt)
            self.list.append((_('Upgrade packages' ), '', _('Recommended update installed packages' ), 'UpgradeAll', self.upgradeablepng, self.divpng))
            self['list'].setList(self.list)
            self.keyGreenAction = 'UpgradeAll'
            self.BlockedInput = False
        else:
            build_MainMenu()
    
#    def refreshLists_Packages(self):
    def refreshLists_Packages_Got_upgadable(self, result = '', retval=0, extra_args = None):
        printDEBUG( "refreshLists_Packages_Got_upgadable" , "enter" )
        self.upgradeablepackages = self.getOPKGlist( SameNazwy = True, lista = result )
        self.packages2upgrade = len(self.upgradeablepackages)
        if self.packages2upgrade > 0:
            printDEBUG( "refreshLists" , "self.packages2upgrade > 0" )
            self.list.append((_('Upgrade packages' ), '', _('Recommended update installed packages' ), 'UpgradeAll', self.upgradeablepng, self.divpng))
            self['list'].setList(self.list)
            self.keyGreenAction = 'UpgradeAll'
            self.BlockedInput = False
            if self.pushUpgrade == True:
                return
        elif (self.packages2upgrade == 0 and self.firstRun == True) or self.pushUpgrade == False:
            printDEBUG( "refreshLists" , "self.packages2upgrade == 0 and self.firstRun == True" )
            self.firstRun = False
        self.Console.ePopen('opkg list', self.refreshLists_Packages_Got_list )

    def refreshLists_Packages_Got_list(self, result = '', retval=0, extra_args = None):
        self.packages = self.getOPKGlist(SameNazwy = False, lista = result)
        self.Console.ePopen('opkg list-installed', self.refreshLists_Packages_Got_installedpackages )

    def refreshLists_Packages_Got_installedpackages(self, result = '', retval=0, extra_args = None):
        self.installedpackages = self.getOPKGlist(SameNazwy = True, lista = result)
        self.SkinSelectorInstalled = 0
        for package in self.packages:
            #łączymy duplikaty razem - duplikat to ta sama nazwa i ten sam opis, moze się różnić jedynie wersją
            if len(self.list) > 0 and package[0].strip() == self.list[-1][0] and package[2].strip() == self.list[-1][2]:
                package[1] = self.list[-1][1] + " > " + package[1].strip()
                self.list.pop(-1)
            #if self.filters[self.ActiveFilterID][0] == "" or package[0].strip().startswith(self.filters[self.ActiveFilterID][0]):
            if self.ActiveFilter == "" or any(AC in package[0].strip() for AC in self.ActiveFilter):
                if package[0].strip() in self.upgradeablepackages:
                    self.list.append(self.buildEntryComponent(package[0].strip(), package[1].strip(), package[2].strip(), 'upgradeable'))
                elif package[0].strip() in self.installedpackages and self.firstRun == False:
                    self.list.append(self.buildEntryComponent(package[0].strip(), package[1].strip(), package[2].strip(), 'installed'))
                    if package[0].strip() == "enigma2-plugin-skinselector":
                        self.SkinSelectorInstalled = 1
                elif self.firstRun == False:
                    #if self.IPTVfullInstalled == True and package[0].strip().startswith("enigma2-plugin-iptvplayer-host-"):
                    #    printDEBUG( "refreshLists" , "Removing = %s" % package[0].strip() )
                    #else:
                    self.list.append(self.buildEntryComponent(package[0].strip(), package[1].strip(), package[2].strip(), 'installable'))
        printDEBUG( "refreshLists" , "calling final self['list'].setList(self.list)" )
        self['list'].setList(self.list)
        self.setCurrentIndex()
        self.BlockedInput = False
      
    def getOPKGlist(self, SameNazwy = False , lista = '' ):
        printDEBUG( "getOPKGlist" , "SameNazwy = %s" % SameNazwy )
        myList = []
        if lista != '':
            self.packetlist = []
            for x in lista.splitlines():
                if PyMajorVersion == 3:
                    try: x = x.decode('utf-8')
                    except Exception: pass
                if x.startswith('Not selecting'):
                    continue
                parts = x.split(' - ')
                if len(parts) >=2:
                    if SameNazwy == True:
                        myList.append( parts[0].strip() )
                    else:
                        if len(parts) == 2:
                            myList.append([ parts[0].strip(), parts[1].strip(), ""])
                        elif len(parts) >=3:
                            myList.append([ parts[0].strip(), parts[1].strip(), parts[2].strip()])
        
        return myList

    def buildEntryComponent(self, name, version, description, state):
        #printDEBUG( "buildEntryComponent" , state )
        if state == 'installable':
            return (name, version, description, state, self.goinstalledpng, self.divpng)
            
        if state == 'installed':
            return (name, version, description, state, self.installedpng, self.divpng)
            
        if state == 'upgradeable':
            return (name, version, description, state, self.upgradeablepng, self.divpng)
            
        if state == 'goremove':
            return [name, version, description, state, self.goremovepng, self.divpng]

        if state == 'gousb':
            return [name, version, description, state, self.gousbpng, self.divpng]
            
    def selectionChanged(self):
        current = self['list'].getCurrent()
        self.keyBlueAction =''
        self['key_blue'].setText('')
        self["key_yellow"].setText('')
        if current:
            #printDEBUG( "selectionChanged" , "selectionChanged.current = %s" % current[3] )
            #print current
            if current[3] == 'installed':
                self['key_green'].setText(_("Delete"))
                self.actionInfo = _("delete %s" )  % current[0]
                self.keyGreenAction = 'opkg remove --autoremove %s' % current[0]
                self["key_yellow"].setText(_('Force uninstall'))
                self.keyYellowAction = 'opkg remove --force-depends %s' % current[0]
                self['key_blue'].setText(_("Reinstall"))
                self.keyBlueAction ='opkg install --force-reinstall %s' % current[0]
            elif current[3] == 'installable':
                self['key_green'].setText(_("Install"))
                self.actionInfo = _("install %s" ) % current[0]
                self.keyGreenAction = 'opkg install %s' % current[0]
            elif current[3] == 'upgradeable':
                self['key_green'].setText(_("Upgrade"))
                self.actionInfo = _("upgrade %s") % current[0]
                self.keyGreenAction = 'opkg upgrade %s' % current[0]
            elif current[3] == 'UpgradeAll':
                self['key_green'].setText(_("Upgrade packages" ))
                self.actionInfo = _("upgrade packages" )
                self.keyGreenAction = 'UpgradeAll'
            elif self.MainMenu == True:
                if current[3] == 'InstallLocal':
                    self['key_green'].setText(_("Install Local package" ))
                    self['key_green'].show()
                    self.keyGreenAction = 'LocalPackage'
                else:
                    self['key_green'].setText(_("Select option"))
                    self.keyGreenAction = ''
                    self.actionInfo = ""
                    self.ActiveFilter = current[3]
                    #print "[jopkg] selectionChanged>self.ActiveFilter = %s" % self.ActiveFilter
            else:
                self['key_green'].setText('')
                self.keyGreenAction = ''
                self.actionInfo = ""
