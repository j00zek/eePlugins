# -*- coding: utf-8 -*-
from __future__ import absolute_import #zmiana strategii ladowanie modulow w py2 z relative na absolute jak w py3
from Plugins.Extensions.StreamlinkConfig.__init__ import mygettext as _ , readCFG , DBGlog
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

config.plugins.streamlinkSRV.streamlinkconfig = NoSave(ConfigNothing())
config.plugins.streamlinkSRV.streamlinkconfigFFMPEG = NoSave(ConfigSelection(default = getCurrFF(), choices = getFFlist()))


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
        DBGlog('buildList >>> self.VisibleSection = %s' % self.VisibleSection )
        self.DoBuildList.stop()
        Mlist = []
        # pilot.wp.pl
        #Mlist.append(getConfigListEntry("", NoSave(ConfigNothing()) ))
        if not os.path.exists('/usr/sbin/streamlinkSRV'):
            Mlist.append(getConfigListEntry('\c00981111' + _("*** Deamon not installed ***")))
        else:
            Mlist.append(getConfigListEntry('\c00289496' + _("*** Available IPTV bouquets ***"), config.plugins.streamlinkSRV.One))
            if self.VisibleSection == 1:
                for f in sorted(os.listdir("/usr/lib/enigma2/python/Plugins/Extensions/StreamlinkConfig/IPTVbouquets"), key=str.lower):
                    if f.startswith('OFF') or f.endswith('OFF') or f.endswith('OFF-not updated'):
                        pass
                    elif os.path.exists('/etc/enigma2/%s' % f):
                        Mlist.append(getConfigListEntry(_("Press OK to remove: %s") % f , config.plugins.streamlinkSRV.removeBouquet))
                    else:
                        Mlist.append(getConfigListEntry(_("Press OK to add: %s") % f , config.plugins.streamlinkSRV.installBouquet))
                for f in sorted(os.listdir("/usr/lib/enigma2/python/Plugins/Extensions/StreamlinkConfig/plugins"), key=str.lower):
                    if f.startswith('generate_') and f.endswith('.py'):
                        bname = f[9:-3]
                        if os.path.exists('/etc/enigma2/%s' % bname):
                            Mlist.append(getConfigListEntry(_("Press OK to remove: %s") % bname , config.plugins.streamlinkSRV.removeBouquet))
                        else:
                            Mlist.append(getConfigListEntry(_("Press OK to create: %s") % bname , config.plugins.streamlinkSRV.generateBouquet))
                if config.plugins.streamlinkSRV.azmanEnabled.value == True:
                    from Plugins.Extensions.StreamlinkConfig.plugins.azmanIPTVsettings import get_azmanIPTVsettings
                    azman = get_azmanIPTVsettings()
                    Mlist.append(getConfigListEntry('\c00009898' + azman['title']))
                    azman = azman['userbouquets']
                    for f in sorted(azman):
                        fUrl = f[0]
                        bname = _('%s (%s)') % (f[1], f[2])
                        if os.path.exists('/etc/enigma2/%s' % f[1]):
                            Mlist.append(getConfigListEntry(_("Press OK to remove: %s") % f[1] , config.plugins.streamlinkSRV.removeBouquet))
                        else:
                            Mlist.append(getConfigListEntry(_("Press OK to download: %s") % bname , config.plugins.streamlinkSRV.downloadBouquet, fUrl))
                else:
                    Mlist.append(getConfigListEntry(_("Support of azman IPTV lists:"), config.plugins.streamlinkSRV.azmanEnabled))
                    
            Mlist.append(getConfigListEntry(""))
            Mlist.append(getConfigListEntry('\c00289496' + _("*** %s configuration ***") % 'pilot.wp.pl', config.plugins.streamlinkSRV.Two))
            if self.VisibleSection == 2:
                Mlist.append(getConfigListEntry(_("Username:"), config.plugins.streamlinkSRV.WPusername))
                Mlist.append(getConfigListEntry(_("Password:"), config.plugins.streamlinkSRV.WPpassword))
                Mlist.append(getConfigListEntry(_("Check login credentials"), config.plugins.streamlinkSRV.WPlogin))
                #Mlist.append(getConfigListEntry("Przedstaw się jako:", config.plugins.streamlinkSRV.WPdevice))
                Mlist.append(getConfigListEntry(_("Prefer DASH than HLS:"), config.plugins.streamlinkSRV.WPpreferDASH))
                Mlist.append(getConfigListEntry(_("Delay video:"), config.plugins.streamlinkSRV.WPvideoDelay))
                Mlist.append(getConfigListEntry(_("Press OK to create %s bouquet") % "userbouquet.WPPL.tv", config.plugins.streamlinkSRV.WPbouquet))
        
            if os.path.islink('/usr/sbin/streamlinkSRV') and 'StreamlinkConfig/' in os.readlink('/usr/sbin/streamlinkSRV'):
                Mlist.append(getConfigListEntry(""))
                Mlist.append(getConfigListEntry('\c00289496' + _("*** remote E2 helper ***"), config.plugins.streamlinkSRV.Three))
                if self.VisibleSection == 3:
                    Mlist.append(getConfigListEntry(_("IP address:"), config.plugins.streamlinkSRV.remoteE2address))
                    Mlist.append(getConfigListEntry(_("Streaming port:"), config.plugins.streamlinkSRV.remoteE2port))
                    Mlist.append(getConfigListEntry(_("Username:"), config.plugins.streamlinkSRV.remoteE2username))
                    Mlist.append(getConfigListEntry(_("Password:"), config.plugins.streamlinkSRV.remoteE2password))
                    Mlist.append(getConfigListEntry(_("Wakeup if remote E2 in standby:"), config.plugins.streamlinkSRV.remoteE2wakeup))
                    Mlist.append(getConfigListEntry(_("Zap before stream workarround:"), config.plugins.streamlinkSRV.remoteE2zap))
        
                Mlist.append(getConfigListEntry(""))
                Mlist.append(getConfigListEntry('\c00289496' + _("*** Deamon configuration ***"), config.plugins.streamlinkSRV.Four))
                if self.VisibleSection == 4 or config.plugins.streamlinkSRV.enabled.value == False:
                    Mlist.append(getConfigListEntry(_("Enable deamon:"), config.plugins.streamlinkSRV.enabled))
                    Mlist.append(getConfigListEntry(_("Port number (127.0.0.1:X):"), config.plugins.streamlinkSRV.PortNumber))
                    Mlist.append(getConfigListEntry(_("Log level:"), config.plugins.streamlinkSRV.logLevel))
                    Mlist.append(getConfigListEntry(_("Log to file:"), config.plugins.streamlinkSRV.logToFile))
                    Mlist.append(getConfigListEntry(_("Clear log on each start:"), config.plugins.streamlinkSRV.ClearLogFile))
                    Mlist.append(getConfigListEntry(_("Save log file in:"), config.plugins.streamlinkSRV.logPath))
                    Mlist.append(getConfigListEntry(_("Buffer path:"), config.plugins.streamlinkSRV.bufferPath))
                    Mlist.append(getConfigListEntry(_("Allow Wrappers in lists:"), config.plugins.streamlinkSRV.useWrappers))
                    Mlist.append(getConfigListEntry(_(" !!! EXPERIMENTAL OPTION(S) !!!")))
                    Mlist.append(getConfigListEntry(_("Recorder mode:"), config.plugins.streamlinkSRV.Recorder))
                    Mlist.append(getConfigListEntry(_("stop deamon on standby:"), config.plugins.streamlinkSRV.StandbyMode))
                    if config.plugins.streamlinkSRV.StandbyMode.value == True:
                        Mlist.append(getConfigListEntry(_("proxy (http://127.0.0.1:8818) for channel:"), config.plugins.streamlinkSRV.streamlinkProxy1))
        
                Mlist.append(getConfigListEntry(""))
                Mlist.append(getConfigListEntry('\c00289496' + _("*** /etc/streamlink/config ***"), config.plugins.streamlinkSRV.Five))
                if self.VisibleSection == 5:
                    for cfg in getStreamlinkConfig():
                        if cfg.startswith('ffmpeg-ffmpeg='):
                            Mlist.append(getConfigListEntry("ffmpeg-ffmpeg=" , config.plugins.streamlinkSRV.streamlinkconfigFFMPEG))
                        else:
                            Mlist.append(getConfigListEntry( cfg , config.plugins.streamlinkSRV.streamlinkconfig))
            else:
                Mlist.append(getConfigListEntry(""))
                Mlist.append(getConfigListEntry('\c00981111' + _("*** not compliant Deamon found ***")))

        #Mlist.append()
        return Mlist

    def __init__(self, session, args=None):
        DBGlog('%s' % '__init__')
        self.VisibleSection = 0
        self.DoBuildList = eTimer()
        self.DoBuildList.callback.append(self.buildList)
        if os.path.exists('/usr/sbin/streamlinkSRV') and os.path.islink('/usr/sbin/streamlinkSRV') and 'StreamlinkConfig/' in os.readlink('/usr/sbin/streamlinkSRV'):
            self.mySL = True
        else:
            self.mySL = False
        
        Screen.__init__(self, session)
        self.session = session
        ConfigListScreen.__init__(self, self.buildList(), on_change = self.changedEntry)

        # Summary
        self.setup_title = _("Streamlink Configuration" + ' v.' + Version)
        self.onChangedEntry = []

        # Buttons
        self["key_red"] = Label(_("Cancel"))
        
        if self.mySL == True:
            self["key_green"] = Label(_("Save"))
            self["key_blue"] = Label(_("Restart daemon"))
            if os.path.exists('/usr/lib/python2.7'):
                self["key_yellow"] = Label(_("Check status"))
            elif os.path.exists('/tmp/streamlinkSRV.log'):
                self["key_yellow"] = Label(_("Show log"))
        else:
            self["key_green"] = Label()
            self["key_blue"] = Label()
            self["key_yellow"] = Label()

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
        if 0:
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
        if self.mySL == True:
            self.saveConfig()
            if os.path.exists('/var/run/streamlink.pid'):
                os.system('/etc/init.d/streamlinkSRV stop')
            if config.plugins.streamlinkSRV.enabled.value:
                os.system('/etc/init.d/streamlinkSRV start')
            self.VisibleSection = 0
            self.close(None)
        
    def refreshBuildList(self, ret = False):
        DBGlog('refreshBuildList >>>')
        self["config"].list = self.buildList()
        self.DoBuildList.start(50, True)
        
    def doNothing(self, ret = False):
        DBGlog('doNothing >>>')
        return
      
    def yellow(self):
        if self.mySL == True:
            if os.path.exists('/tmp/streamlinkSRV.log'):
                self.session.openWithCallback(self.doNothing ,Console, title = '/tmp/streamlinkSRV.log', cmdlist = [ 'cat /tmp/streamlinkSRV.log' ])
        
    def blue(self):
        if self.mySL == True:
            mtitle = _('Restarting daemon')
            cmd = '/usr/sbin/streamlinkSRV restart'
            self.session.openWithCallback(self.doNothing ,Console, title = mtitle, cmdlist = [ cmd ])
        
    def exit(self):
        self.VisibleSection = 0
        self.close(None)
        
    def prevConf(self):
        DBGlog('prevConf >>> VisibleSection = %s' % self.VisibleSection)
        self.VisibleSection -= 1
        if self.VisibleSection < 1:
            self.VisibleSection = 5
        self.refreshBuildList()
        
    def nextConf(self):
        DBGlog('nextConf >>> VisibleSection = %s' % self.VisibleSection)
        self.VisibleSection += 1
        if self.VisibleSection > 5:
            self.VisibleSection = 1
        self.refreshBuildList()
        
    def layoutFinished(self):
        self.VisibleSection = 0
        self.DoBuildList.start(10, True)
        self.setTitle(self.setup_title)
        
        if os.path.exists("/usr/lib/enigma2/python/Plugins/SystemPlugins/ServiceApp/serviceapp.so"):
            self.choicesList = [("gstreamer (root 4097)","4097"),("ServiceApp gstreamer (root 5001)","5001"), ("ServiceApp ffmpeg (root 5002)","5002"),("Hardware (root 1) wymagany do PIP","1")]
        else:
            self.choicesList = [("gstreamer (root 4097)","4097"),("Hardware (root 1) wymagany do PIP","1"),(_("ServiceApp not installed!"), None)]

    def changedEntry(self):
        DBGlog('%s' % 'changedEntry()')
        try:
            for x in self.onChangedEntry:
                x()
        except Exception as e:
            DBGlog('%s' % str(e))

    def selectionChanged(self):
        if 0:
            DBGlog('%s' % 'selectionChanged(%s)' % self["config"].getCurrent()[0])

    def getCurrentEntry(self):
        return self["config"].getCurrent()[0]

    def getCurrentValue(self):
        if len(self["config"].getCurrent()) >= 2:
            return str(self["config"].getCurrent()[1].getText())

    def createSummary(self):
        return SetupSummary

    def Okbutton(self):
        DBGlog('%s' % 'Okbutton')
        try:
            self.doAction = None
            curIndex = self["config"].getCurrentIndex()
            selectedItem = self["config"].list[curIndex]
            if len(selectedItem) >= 2:
                currItem = selectedItem[1]
                currInfo = selectedItem[0]
                if isinstance(currItem, ConfigText):
                    from Screens.VirtualKeyBoard import VirtualKeyBoard
                    self.session.openWithCallback(self.OkbuttonTextChangedConfirmed, VirtualKeyBoard, title=(currInfo), text = currItem.value)
                elif currItem == config.plugins.streamlinkSRV.One:
                    if self.VisibleSection == 1: self.VisibleSection = 0
                    else: self.VisibleSection = 1
                    self.refreshBuildList()
                elif currItem == config.plugins.streamlinkSRV.Two:
                    if self.VisibleSection == 2: self.VisibleSection = 0
                    else: self.VisibleSection = 2
                    self.refreshBuildList()
                elif currItem == config.plugins.streamlinkSRV.Three:
                    if self.VisibleSection == 3: self.VisibleSection = 0
                    else: self.VisibleSection = 3
                    self.refreshBuildList()
                elif currItem == config.plugins.streamlinkSRV.Four:
                    if self.VisibleSection == 4: self.VisibleSection = 0
                    else: self.VisibleSection = 4
                    self.refreshBuildList()
                elif currItem == config.plugins.streamlinkSRV.Five:
                    if self.VisibleSection == 5: self.VisibleSection = 0
                    else: self.VisibleSection = 5
                    self.refreshBuildList()
                elif currItem == config.plugins.streamlinkSRV.WPbouquet:
                    if config.plugins.streamlinkSRV.WPusername.value == '' or config.plugins.streamlinkSRV.WPpassword.value == '':
                        self.session.openWithCallback(self.doNothing,MessageBox, _("Username & Password are required!"), MessageBox.TYPE_INFO, timeout = 5)
                        return
                    else:
                        self.doAction = ('wpBouquet.py' , '/etc/enigma2/userbouquet.WPPL.tv', config.plugins.streamlinkSRV.WPusername.value, config.plugins.streamlinkSRV.WPpassword.value)
                elif currItem == config.plugins.streamlinkSRV.WPlogin:
                    if config.plugins.streamlinkSRV.WPusername.value == '' or config.plugins.streamlinkSRV.WPpassword.value == '':
                        self.session.openWithCallback(self.doNothing,MessageBox, _("Username & Password are required!"), MessageBox.TYPE_INFO, timeout = 5)
                        return
                    else:
                        self.saveConfig()
                        cmd = "/usr/bin/python /usr/lib/enigma2/python/Plugins/Extensions/StreamlinkConfig/plugins/wpBouquet.py checkLogin '%s' '%s'" % (config.plugins.streamlinkSRV.WPusername.value, config.plugins.streamlinkSRV.WPpassword.value)
                        self.session.openWithCallback(self.doNothing ,Console, title = _('Credentials verification'), cmdlist = [ cmd ])
                        return
                elif currItem == config.plugins.streamlinkSRV.generateBouquet:
                    DBGlog('currItem == config.plugins.streamlinkSRV.generateBouquet')
                    bouquetFileName = currInfo.split(': ')[1].strip()
                    self.doAction = ('generate_%s.py' % bouquetFileName, '/etc/enigma2/%s' % bouquetFileName, 'anonymous','nopassword')
                elif currItem == config.plugins.streamlinkSRV.removeBouquet: #removeBouquet
                    DBGlog('currItem == config.plugins.streamlinkSRV.removeBouquet')
                    #wybrany bukiet
                    bouquetFileName = currInfo.split(': ')[1].strip()
                    self.doAction = ('removeBouquet.py', '/etc/enigma2/%s' % bouquetFileName, _("Bouquet_'%s' _removed_properly") % bouquetFileName)
                elif currItem == config.plugins.streamlinkSRV.installBouquet: #installBouquet
                    DBGlog('currItem == config.plugins.streamlinkSRV.installBouquet')
                    #wybrany bukiet
                    bouquetFileName = currInfo.split(': ')[1].strip()
                    self.cleanBouquets_tvradio()
                    self.doAction = ('installBouquet.py', bouquetFileName)
                elif currItem == config.plugins.streamlinkSRV.downloadBouquet: #downloadBouquet
                    DBGlog('currItem == config.plugins.streamlinkSRV.installBouquet')
                    #wybrany bukiet
                    bouquetFileName = currInfo.split(': ',1)[1].split(' ',1)[0].strip()
                    self.cleanBouquets_tvradio()
                    url2bouquet = selectedItem[2]
                    #DBGlog('url2bouquet=%s' % url2bouquet)
                    self.doAction = ('downloadBouquet.py', bouquetFileName, url2bouquet, )
                    
                ####
                DBGlog('%s' % str(self.doAction))
                if not self.doAction is None:
                    cmd = self.doAction[0]
                    bfn = self.doAction[1]
                    DBGlog('%s' % bfn)
                    if cmd == 'removeBouquet.py':
                        cmd = '/usr/bin/python /usr/lib/enigma2/python/Plugins/Extensions/StreamlinkConfig/plugins/%s' % ' '.join(self.doAction)
                        self.session.openWithCallback(self.retFromCMD ,Console, title = _('Removing bouquet...'), cmdlist = [ cmd ])
                    elif os.path.exists(bfn):
                        self.cmdTitle = _('Updating %s...') % bfn
                        self.session.openWithCallback(self.OkbuttonConfirmed, MessageBox, _("Do you want to update '%s' file?") % bfn, MessageBox.TYPE_YESNO, default = False)
                    elif cmd == 'downloadBouquet.py':
                        self.cmdTitle = _('Downloading %s...') % bfn
                        self.session.openWithCallback(self.OkbuttonConfirmed, MessageBox, _("Do you want to download '%s' file?") % bfn, MessageBox.TYPE_YESNO, default = False)
                    else:
                        self.cmdTitle = _('Creating %s...') % bfn
                        self.session.openWithCallback(self.OkbuttonConfirmed, MessageBox, _("Do you want to create '%s' file?") % bfn, MessageBox.TYPE_YESNO, default = True)
        except Exception as e:
            DBGlog('%s' % str(e))

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
            DBGlog("OkbuttonTextChangedConfirmed(ret ='%s')" % str(ret))
        else:
            try:
                curIndex = self["config"].getCurrentIndex()
                self["config"].list[curIndex][1].value = ret
            except Exception as e:
                DBGlog('%s' % str(e))

    def OkbuttonConfirmed(self, ret = False):
        if ret:
            self.session.openWithCallback(self.SelectedFramework, ChoiceBox, title = _("Select Multiframework"), list = self.choicesList)

    def SelectedFramework(self, ret):
        if not ret or ret == "None":
            ret = (None,'4097')
        cmd = '/usr/bin/python /usr/lib/enigma2/python/Plugins/Extensions/StreamlinkConfig/plugins/%s %s %s %s' % (' '.join(self.doAction),
                                                                                                                config.plugins.streamlinkSRV.PortNumber.value,
                                                                                                                ret[1],
                                                                                                                 config.plugins.streamlinkSRV.useWrappers.value
                                                                                                               )
        if self.doAction[0] == 'wpBouquet.py':
            DBGlog('%s WPuser WPpass %s %s' % (self.doAction[0], config.plugins.streamlinkSRV.PortNumber.value, ret[1]))
        else:
            DBGlog('%s' % cmd)
        self.session.openWithCallback(self.retFromCMD ,Console, title = self.cmdTitle, cmdlist = [ cmd ])

    def reloadBouquets(self):
        from enigma import eDVBDB
        eDVBDB.getInstance().reloadBouquets()
        
    def retFromCMD(self, ret = False):
        DBGlog('retFromCMD >>>')
        self.cleanBouquets_tvradio()
        self.reloadBouquets()
        msg = _("Bouquets has been reloaded")
        self.session.openWithCallback(self.refreshBuildList,MessageBox, msg, MessageBox.TYPE_INFO, timeout = 5)
