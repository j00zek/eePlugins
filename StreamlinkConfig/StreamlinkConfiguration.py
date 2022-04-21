# -*- coding: utf-8 -*-
from __future__ import absolute_import #zmiana strategii ladowanie modulow w py2 z relative na absolute jak w py3
from Plugins.Extensions.StreamlinkConfig.__init__ import mygettext as _ , readCFG
from Plugins.Extensions.StreamlinkConfig.version import Version
import os
# GUI (Screens)
from Components.ActionMap import ActionMap
from Components.config import *
from Components.ConfigList import ConfigListScreen
from Components.Label import Label
#from Components.Sources.StaticText import StaticText
from enigma import eTimer

from Screens.ChoiceBox import ChoiceBox
from Screens.Console import Console
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Screens.Setup import SetupSummary

config.plugins.streamlinksrv = ConfigSubsection()

config.plugins.streamlinksrv.installBouquet = NoSave(ConfigNothing())
config.plugins.streamlinksrv.removeBouquet = NoSave(ConfigNothing())
config.plugins.streamlinksrv.generateBouquet = NoSave(ConfigNothing())
config.plugins.streamlinksrv.One = NoSave(ConfigNothing())
config.plugins.streamlinksrv.Two = NoSave(ConfigNothing())
config.plugins.streamlinksrv.Three = NoSave(ConfigNothing())
config.plugins.streamlinksrv.Four = NoSave(ConfigNothing())
config.plugins.streamlinksrv.Five = NoSave(ConfigNothing())

config.plugins.streamlinksrv.enabled = ConfigYesNo(default = False)
config.plugins.streamlinksrv.logLevel = ConfigSelection(default = "info", choices = [("none", _("none")),
                                                                                    ("info", _("info")),
                                                                                    ("warning", _("warning")),
                                                                                    ("error", _("error")),
                                                                                    ("critical", _("critical")),
                                                                                    ("debug", _("debug")),
                                                                                    ("trace", _("trace")),
                                                                              ])
config.plugins.streamlinksrv.logToFile = ConfigEnableDisable(default = False)
config.plugins.streamlinksrv.ClearLogFile = ConfigEnableDisable(default = True)
config.plugins.streamlinksrv.logPath = ConfigSelection(default = "/tmp", choices = [("/home/root", "/home/root"), ("/tmp", "/tmp"), ("/hdd", "/hdd"), ])
config.plugins.streamlinksrv.PortNumber = ConfigSelection(default = "8088", choices = [("8088", "8088"), ("88", "88"), ])
config.plugins.streamlinksrv.bufferPath = ConfigText(default = "/tmp")
config.plugins.streamlinksrv.EPGserver = ConfigEnableDisable(default = False)
config.plugins.streamlinksrv.Recorder = ConfigEnableDisable(default = False)
#config.plugins.streamlinksrv.managePicons = ConfigEnableDisable(default = True)

# pilot.wp.pl
config.plugins.streamlinksrv.WPusername = ConfigText(readCFG('WPusername'), fixed_size = False)
config.plugins.streamlinksrv.WPpassword = ConfigPassword(readCFG('WPpassword'), fixed_size = False)
config.plugins.streamlinksrv.WPbouquet  = NoSave(ConfigNothing())
config.plugins.streamlinksrv.WPlogin    = NoSave(ConfigNothing())
config.plugins.streamlinksrv.WPpreferDASH = ConfigEnableDisable(default = False)
config.plugins.streamlinksrv.WPdevice = ConfigSelection(default = "androidtv", choices = [("androidtv", "Android TV"), ("web", _("web client")), ])
config.plugins.streamlinksrv.WPvideoDelay = ConfigSelection(default = "0", choices = [("0", _("don't delay")), ("0.25", _("by %s s." % '0.25')),
                                                                                      ("0.5", _("by %s s." % '0.5')), ("0.75", _("by %s s." % '0.75')),
                                                                                      ("1.0", _("by %s s." % '1.0')), ("5.0", _("by %s s." % '5.0'))])

# remote E2
config.plugins.streamlinksrv.remoteE2address = ConfigText(default = "192.168.1.8")
config.plugins.streamlinksrv.remoteE2port = ConfigText(default = "8001")
config.plugins.streamlinksrv.remoteE2username = ConfigText(default = "root")
config.plugins.streamlinksrv.remoteE2password = ConfigPassword(default = "root")
config.plugins.streamlinksrv.remoteE2zap = ConfigEnableDisable(default = False)
config.plugins.streamlinksrv.remoteE2wakeup = ConfigEnableDisable(default = False)

if os.path.exists("/tmp/StreamlinkConfig.log"):
    os.remove("/tmp/StreamlinkConfig.log")

#### streamlink config /etc/streamlink/config ####
def getFFlist():
    ffList = []
    for f in sorted(os.listdir("/usr/bin"), key=str.lower):
        if f.startswith('ffmpeg'):
            ffList.append(("/usr/bin/%s" % f, f ))
    return ffList

def getCurrFF():
    ff = '/usr/bin/ffmpeg'
    for c in getStreamlinkConfig():
        if c.startswith('ffmpeg-ffmpeg='):
            tmp = c.split('=')[1].strip()
            if os.path.exists(tmp):
                ff = tmp
    return ff
    
def getStreamlinkConfig():
    try:
        cfg = open('/etc/streamlink/config', 'r').read().splitlines()
    except Exception:
        cfg = []
    return cfg

config.plugins.streamlinksrv.streamlinkconfig = NoSave(ConfigNothing())
config.plugins.streamlinksrv.streamlinkconfigFFMPEG = NoSave(ConfigSelection(default = getCurrFF(), choices = getFFlist()))


class StreamlinkConfiguration(Screen, ConfigListScreen):
    from enigma import getDesktop
    if getDesktop(0).size().width() == 1920: #definicja skin-a musi byc tutaj, zeby vti sie nie wywalalo na labelach, inaczje trzeba uzywasc zrodla statictext
        skin = """<screen name="StreamlinkConfiguration" position="center,center" size="1000,700" title="Streamlink configuration">
                            <widget name="config" position="20,20" size="960,600" zPosition="1" scrollbarMode="showOnDemand" />
                            <widget name="key_red"    position="91,630" zPosition="2" size="200,30" foregroundColor="red"   valign="center" halign="left" font="Regular;22" transparent="1" />
                            <widget name="key_green"  position="378,630" zPosition="2" size="200,30" foregroundColor="green"  valign="center" halign="left" font="Regular;22" transparent="1" />
                            <widget name="key_yellow" position="665,630" zPosition="2" size="200,30" foregroundColor="yellow" valign="center" halign="left" font="Regular;22" transparent="1" />
                            <widget name="key_blue"   position="865,630" zPosition="2" size="200,30" foregroundColor="blue"   valign="center" halign="left" font="Regular;22" transparent="1" />
                          </screen>"""
    else:
        skin = """<screen name="StreamlinkConfiguration" position="center,center" size="700,200" title="Streamlink configuration">
                            <widget name="config"   position="20,20" size="640,145" zPosition="1" scrollbarMode="showOnDemand" />
                            <widget name="key_red"    position="20,150" zPosition="2" size="150,30" foregroundColor="red" valign="center" halign="left" font="Regular;22" transparent="1" />
                            <widget name="key_green"  position="170,150" zPosition="2" size="150,30" foregroundColor="green" valign="center" halign="left" font="Regular;22" transparent="1" />
                            <widget name="key_yellow" position="360,150" zPosition="2" size="150,30" foregroundColor="yellow" valign="center" halign="left" font="Regular;22" transparent="1" />
                            <widget name="key_blue"   position="500,150" zPosition="2" size="150,30" foregroundColor="blue" valign="center" halign="left" font="Regular;22" transparent="1" />
                          </screen>"""
    def buildList(self):
        self.DBGlog('buildList >>> self.VisibleSection = %s' % self.VisibleSection )
        self.DoBuildList.stop()
        Mlist = []
        # pilot.wp.pl
        #Mlist.append(getConfigListEntry("", NoSave(ConfigNothing()) ))
        Mlist.append(getConfigListEntry('\c00289496' + _("*** Available IPTV bouquets ***"), config.plugins.streamlinksrv.One))
        if self.VisibleSection == 1:
            for f in sorted(os.listdir("/usr/lib/enigma2/python/Plugins/Extensions/StreamlinkConfig/IPTVbouquets"), key=str.lower):
                if f.startswith('OFF') or f.endswith('OFF') or f.endswith('OFF-not updated'):
                    pass
                elif os.path.exists('/etc/enigma2/%s' % f):
                    Mlist.append(getConfigListEntry(_("Press OK to remove: %s") % f , config.plugins.streamlinksrv.removeBouquet))
                else:
                    Mlist.append(getConfigListEntry(_("Press OK to add: %s") % f , config.plugins.streamlinksrv.installBouquet))
            for f in sorted(os.listdir("/usr/lib/enigma2/python/Plugins/Extensions/StreamlinkConfig/plugins"), key=str.lower):
                if f.startswith('generate_') and f.endswith('.py'):
                    bname = f[9:-3]
                    if os.path.exists('/etc/enigma2/%s' % bname):
                        Mlist.append(getConfigListEntry(_("Press OK to remove: %s") % bname , config.plugins.streamlinksrv.removeBouquet))
                    else:
                        Mlist.append(getConfigListEntry(_("Press OK to create: %s") % bname , config.plugins.streamlinksrv.generateBouquet))
                
        Mlist.append(getConfigListEntry(""))
        Mlist.append(getConfigListEntry('\c00289496' + _("*** %s configuration ***") % 'pilot.wp.pl', config.plugins.streamlinksrv.Two))
        if self.VisibleSection == 2:
            Mlist.append(getConfigListEntry(_("Username:"), config.plugins.streamlinksrv.WPusername))
            Mlist.append(getConfigListEntry(_("Password:"), config.plugins.streamlinksrv.WPpassword))
            Mlist.append(getConfigListEntry(_("Check login credentials"), config.plugins.streamlinksrv.WPlogin))
            #Mlist.append(getConfigListEntry("Przedstaw się jako:", config.plugins.streamlinksrv.WPdevice))
            Mlist.append(getConfigListEntry(_("Prefer DASH than HLS:"), config.plugins.streamlinksrv.WPpreferDASH))
            Mlist.append(getConfigListEntry(_("Delay video:"), config.plugins.streamlinksrv.WPvideoDelay))
            Mlist.append(getConfigListEntry(_("Press OK to create %s bouquet") % "userbouquet.WPPL.tv", config.plugins.streamlinksrv.WPbouquet))
        
        Mlist.append(getConfigListEntry(""))
        Mlist.append(getConfigListEntry('\c00289496' + _("*** remote E2 helper ***"), config.plugins.streamlinksrv.Three))
        if self.VisibleSection == 3:
            Mlist.append(getConfigListEntry(_("IP address:"), config.plugins.streamlinksrv.remoteE2address))
            Mlist.append(getConfigListEntry(_("Streaming port:"), config.plugins.streamlinksrv.remoteE2port))
            Mlist.append(getConfigListEntry(_("Username:"), config.plugins.streamlinksrv.remoteE2username))
            Mlist.append(getConfigListEntry(_("Password:"), config.plugins.streamlinksrv.remoteE2password))
            Mlist.append(getConfigListEntry(_("Wakeup if remote E2 in standby:"), config.plugins.streamlinksrv.remoteE2wakeup))
            Mlist.append(getConfigListEntry(_("Zap before stream workarround:"), config.plugins.streamlinksrv.remoteE2zap))
        
        Mlist.append(getConfigListEntry(""))
        Mlist.append(getConfigListEntry('\c00289496' + _("*** Deamon configuration ***"), config.plugins.streamlinksrv.Four))
        if self.VisibleSection == 4 or config.plugins.streamlinksrv.enabled.value == False:
            Mlist.append(getConfigListEntry(_("Enable deamon:"), config.plugins.streamlinksrv.enabled))
            Mlist.append(getConfigListEntry(_("Port number (127.0.0.1:X):"), config.plugins.streamlinksrv.PortNumber))
            Mlist.append(getConfigListEntry(_("Log level:"), config.plugins.streamlinksrv.logLevel))
            Mlist.append(getConfigListEntry(_("Log to file:"), config.plugins.streamlinksrv.logToFile))
            Mlist.append(getConfigListEntry(_("Clear log on each start:"), config.plugins.streamlinksrv.ClearLogFile))
            Mlist.append(getConfigListEntry(_("Save log file in:"), config.plugins.streamlinksrv.logPath))
            Mlist.append(getConfigListEntry(_("Buffer path:"), config.plugins.streamlinksrv.bufferPath))
            Mlist.append(getConfigListEntry(_("EPGimport mode:"), config.plugins.streamlinksrv.EPGserver))
            Mlist.append(getConfigListEntry(_("Recorder mode:"), config.plugins.streamlinksrv.Recorder))
            #Mlist.append(getConfigListEntry(_("link IPTV picons:"), config.plugins.streamlinksrv.managePicons))
        
        Mlist.append(getConfigListEntry(""))
        Mlist.append(getConfigListEntry('\c00289496' + _("*** /etc/streamlink/config ***"), config.plugins.streamlinksrv.Five))
        if self.VisibleSection == 5:
            for cfg in getStreamlinkConfig():
                if cfg.startswith('ffmpeg-ffmpeg='):
                    Mlist.append(getConfigListEntry("ffmpeg-ffmpeg=" , config.plugins.streamlinksrv.streamlinkconfigFFMPEG))
                else:
                    Mlist.append(getConfigListEntry( cfg , config.plugins.streamlinksrv.streamlinkconfig))

        #Mlist.append()
        return Mlist

    def __init__(self, session, args=None):
        self.DBGlog('%s' % '__init__')
        self.VisibleSection = 0
        self.DoBuildList = eTimer()
        self.DoBuildList.callback.append(self.buildList)
        Screen.__init__(self, session)
        self.session = session
        ConfigListScreen.__init__(self, self.buildList(), on_change = self.changedEntry)

        # Summary
        self.setup_title = _("Streamlink Configuration" + ' v.' + Version)
        self.onChangedEntry = []

        # Buttons
        self["key_red"] = Label(_("Cancel"))
        self["key_green"] = Label(_("Save"))
        self["key_yellow"] = Label(_("Check status"))
        self["key_blue"] = Label(_("Restart daemon"))

        # Define Actions
        self["actions"] = ActionMap(["StreamlinkConfiguration"],
            {
                "cancel":   self.exit,
                "red"   :   self.exit,
                "green" :   self.save,
                "yellow":   self.yellow,
                "blue"  :   self.blue,
                "save":     self.save,
                "ok":       self.Okbutton,
                "prevConf": self.prevConf,
                "nextConf": self.nextConf,
            }, -2)
        if not self.selectionChanged in self["config"].onSelectionChanged:
            self["config"].onSelectionChanged.append(self.selectionChanged)
        self.onLayoutFinish.append(self.layoutFinished)
        self.doAction = None

    def saveConfig(self):
        for x in self["config"].list:
            if len(x) >= 2:
                x[1].save()
        configfile.save()

    def save(self):
        self.saveConfig()
        if os.path.exists('/var/run/streamlink.pid'):
            os.system('/etc/init.d/streamlinksrv stop')
        if config.plugins.streamlinksrv.enabled.value:
            os.system('/etc/init.d/streamlinksrv start')
        self.VisibleSection = 0
        self.close(None)
        
    def refreshBuildList(self, ret = False):
        self.DBGlog('refreshBuildList >>>')
        self["config"].list = self.buildList()
        self.DoBuildList.start(50, True)
        
    def doNothing(self, ret = False):
        self.DBGlog('doNothing >>>')
        return
      
    def yellow(self):
        def yellowRet(ret = False):
            if ret:
                mtitle = _('(Re)installing required packages...')
                cmd = '/usr/lib/enigma2/python/Plugins/Extensions/StreamlinkConfig/plugins/installPackets.sh forceReinstall'
            else:
                mtitle = _('Checking state of required packages...')
                cmd = '/usr/lib/enigma2/python/Plugins/Extensions/StreamlinkConfig/plugins/installPackets.sh'
            self.session.openWithCallback(self.doNothing ,Console, title = mtitle, cmdlist = [ cmd ])
        self.session.openWithCallback(yellowRet, MessageBox, _("Do you want to force packets reinstallation?"), MessageBox.TYPE_YESNO, default = False)
        
    def blue(self):
        mtitle = _('Restarting daemon')
        cmd = '/usr/sbin/streamlinksrv restart'
        self.session.openWithCallback(self.doNothing ,Console, title = mtitle, cmdlist = [ cmd ])
        
    def exit(self):
        self.VisibleSection = 0
        self.close(None)
        
    def prevConf(self):
        self.DBGlog('prevConf >>> VisibleSection = %s' % self.VisibleSection)
        self.VisibleSection -= 1
        if self.VisibleSection < 1:
            self.VisibleSection = 5
        self.refreshBuildList()
        
    def nextConf(self):
        self.DBGlog('nextConf >>> VisibleSection = %s' % self.VisibleSection)
        self.VisibleSection += 1
        if self.VisibleSection > 5:
            self.VisibleSection = 1
        self.refreshBuildList()
        
    def layoutFinished(self):
        self.VisibleSection = 0
        self.DoBuildList.start(20, True)
        if os.path.exists('/usr/lib/enigma2/python/Plugins/Extensions/StreamlinkConfig/1stRun'):
            if os.path.exists('/var/run/streamlink.pid'):
                os.system('/usr/lib/enigma2/python/Plugins/Extensions/StreamlinkConfig/plugins/installPackets.sh &')
            else:
                os.system('/usr/lib/enigma2/python/Plugins/Extensions/StreamlinkConfig/plugins/installPackets.sh forceReinstall &')
            os.remove('/usr/lib/enigma2/python/Plugins/Extensions/StreamlinkConfig/1stRun')
        self.setTitle(self.setup_title)
        
        if os.path.exists("/usr/lib/enigma2/python/Plugins/SystemPlugins/ServiceApp/serviceapp.so"):
            self.choicesList = [("gstreamer (root 4097)","4097"),("ServiceApp gstreamer (root 5001)","5001"), ("ServiceApp ffmpeg (root 5002)","5002"),("Hardware (root 1) wymagany do PIP","1")]
        else:
            self.choicesList = [("gstreamer (root 4097)","4097"),("Hardware (root 1) wymagany do PIP","1"),(_("ServiceApp not installed!"), None)]

    def changedEntry(self):
        self.DBGlog('%s' % 'changedEntry()')
        try:
            for x in self.onChangedEntry:
                x()
        except Exception as e:
            self.DBGlog('%s' % str(e))

    def selectionChanged(self):
        self.DBGlog('%s' % 'selectionChanged(%s)' % self["config"].getCurrent()[0])

    def getCurrentEntry(self):
        return self["config"].getCurrent()[0]

    def getCurrentValue(self):
        if len(self["config"].getCurrent()) >= 2:
            return str(self["config"].getCurrent()[1].getText())

    def createSummary(self):
        return SetupSummary

    def DBGlog(self, text):
        open("/tmp/StreamlinkConfig.log", "a").write('%s\n' % str(text))
        
    def Okbutton(self):
        self.DBGlog('%s' % 'Okbutton')
        try:
            self.doAction = None
            curIndex = self["config"].getCurrentIndex()
            selectedItem = self["config"].list[curIndex]
            if len(selectedItem) == 2:
                currItem = selectedItem[1]
                currInfo = selectedItem[0]
                if isinstance(currItem, ConfigText):
                    from Screens.VirtualKeyBoard import VirtualKeyBoard
                    self.session.openWithCallback(self.OkbuttonTextChangedConfirmed, VirtualKeyBoard, title=(currInfo), text = currItem.value)
                elif currItem == config.plugins.streamlinksrv.One:
                    if self.VisibleSection == 1: self.VisibleSection = 0
                    else: self.VisibleSection = 1
                    self.refreshBuildList()
                elif currItem == config.plugins.streamlinksrv.Two:
                    if self.VisibleSection == 2: self.VisibleSection = 0
                    else: self.VisibleSection = 2
                    self.refreshBuildList()
                elif currItem == config.plugins.streamlinksrv.Three:
                    if self.VisibleSection == 3: self.VisibleSection = 0
                    else: self.VisibleSection = 3
                    self.refreshBuildList()
                elif currItem == config.plugins.streamlinksrv.Four:
                    if self.VisibleSection == 4: self.VisibleSection = 0
                    else: self.VisibleSection = 4
                    self.refreshBuildList()
                elif currItem == config.plugins.streamlinksrv.Five:
                    if self.VisibleSection == 5: self.VisibleSection = 0
                    else: self.VisibleSection = 5
                    self.refreshBuildList()
                elif currItem == config.plugins.streamlinksrv.WPbouquet:
                    if config.plugins.streamlinksrv.WPusername.value == '' or config.plugins.streamlinksrv.WPpassword.value == '':
                        self.session.openWithCallback(self.doNothing,MessageBox, _("Username & Password are required!"), MessageBox.TYPE_INFO, timeout = 5)
                        return
                    else:
                        self.doAction = ('wpBouquet.py' , '/etc/enigma2/userbouquet.WPPL.tv', config.plugins.streamlinksrv.WPusername.value, config.plugins.streamlinksrv.WPpassword.value)
                elif currItem == config.plugins.streamlinksrv.WPlogin:
                    if config.plugins.streamlinksrv.WPusername.value == '' or config.plugins.streamlinksrv.WPpassword.value == '':
                        self.session.openWithCallback(self.doNothing,MessageBox, _("Username & Password are required!"), MessageBox.TYPE_INFO, timeout = 5)
                        return
                    else:
                        self.saveConfig()
                        cmd = '/usr/bin/python /usr/lib/enigma2/python/Plugins/Extensions/StreamlinkConfig/plugins/wpBouquet.py checkLogin'
                        self.session.openWithCallback(self.doNothing ,Console, title = _('Credentials verification'), cmdlist = [ cmd ])
                        return
                elif currItem == config.plugins.streamlinksrv.generateBouquet:
                    self.DBGlog('currItem == config.plugins.streamlinksrv.generateBouquet')
                    bouquetFileName = currInfo.split(': ')[1].strip()
                    self.doAction = ('generate_%s.py' % bouquetFileName, '/etc/enigma2/%s' % bouquetFileName, 'anonymous','nopassword')
                elif currItem == config.plugins.streamlinksrv.removeBouquet: #removeBouquet
                    self.DBGlog('currItem == config.plugins.streamlinksrv.removeBouquet')
                    #wybrany bukiet
                    bouquetFileName = currInfo.split(': ')[1].strip()
                    self.doAction = ('removeBouquet.py', '/etc/enigma2/%s' % bouquetFileName, _("Bouquet_'%s' _removed_properly") % bouquetFileName)
                elif currItem == config.plugins.streamlinksrv.installBouquet: #installBouquet
                    self.DBGlog('currItem == config.plugins.streamlinksrv.installBouquet')
                    #wybrany bukiet
                    bouquetFileName = currInfo.split(': ')[1].strip()
                    self.cleanBouquets_tvradio()
                    self.doAction = ('installBouquet.py', bouquetFileName)
                    
                ####
                self.DBGlog('%s' % str(self.doAction))
                if not self.doAction is None:
                    cmd = self.doAction[0]
                    bfn = self.doAction[1]
                    self.DBGlog('%s' % bfn)
                    if cmd == 'removeBouquet.py':
                        cmd = '/usr/bin/python /usr/lib/enigma2/python/Plugins/Extensions/StreamlinkConfig/plugins/%s' % ' '.join(self.doAction)
                        self.session.openWithCallback(self.retFromCMD ,Console, title = _('Removing bouquet...'), cmdlist = [ cmd ])
                    elif os.path.exists(bfn):
                        self.cmdTitle = _('Updating %s...') % bfn
                        self.session.openWithCallback(self.OkbuttonConfirmed, MessageBox, _("Do you want to update '%s' file?") % bfn, MessageBox.TYPE_YESNO, default = False)
                    else:
                        self.cmdTitle = _('Creating %s...') % bfn
                        self.session.openWithCallback(self.OkbuttonConfirmed, MessageBox, _("Do you want to create '%s' file?") % bfn, MessageBox.TYPE_YESNO, default = True)
        except Exception as e:
            self.DBGlog('%s' % str(e))

    def cleanBouquets_tvradio(self): #clean bouquets.tv from non existing files
        for TypBukietu in('/etc/enigma2/bouquets.tv','/etc/enigma2/bouquets.radio'):
            f = ''
            for line in open(TypBukietu,'r'):
                if 'FROM BOUQUET' in line:
                    fname = line.split('FROM BOUQUET')[1].strip().split('"')[1].strip()
                    if os.path.exists('/etc/enigma2/%s' % fname):
                        f += line
                else:
                    f += line
            open(TypBukietu,'w').write(f)
            
    def OkbuttonTextChangedConfirmed(self, ret ):
        if ret is None:
            self.DBGlog("OkbuttonTextChangedConfirmed(ret ='%s')" % str(ret))
        else:
            try:
                curIndex = self["config"].getCurrentIndex()
                self["config"].list[curIndex][1].value = ret
            except Exception as e:
                self.DBGlog('%s' % str(e))

    def OkbuttonConfirmed(self, ret = False):
        if ret:
            self.session.openWithCallback(self.SelectedFramework, ChoiceBox, title = _("Select Multiframework"), list = self.choicesList)

    def SelectedFramework(self, ret):
        if not ret or ret == "None":
            ret = (None,'4097')
        cmd = '/usr/bin/python /usr/lib/enigma2/python/Plugins/Extensions/StreamlinkConfig/plugins/%s %s %s' % (' '.join(self.doAction),
                                                                                                                config.plugins.streamlinksrv.PortNumber.value,
                                                                                                                ret[1]
                                                                                                               )
        if self.doAction[0] == 'wpBouquet.py':
            self.DBGlog('%s WPuser WPpass %s %s' % (self.doAction[0], config.plugins.streamlinksrv.PortNumber.value, ret[1]))
        else:
            self.DBGlog('%s' % cmd)
        self.session.openWithCallback(self.retFromCMD ,Console, title = self.cmdTitle, cmdlist = [ cmd ])

    def reloadBouquets(self):
        from enigma import eDVBDB
        eDVBDB.getInstance().reloadBouquets()
        
    def retFromCMD(self, ret = False):
        self.DBGlog('retFromCMD >>>')
        self.cleanBouquets_tvradio()
        self.reloadBouquets()
        msg = _("Bouquets has been reloaded")
        self.session.openWithCallback(self.refreshBuildList,MessageBox, msg, MessageBox.TYPE_INFO, timeout = 5)
