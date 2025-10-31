# -*- coding: utf-8 -*-
from Plugins.Extensions.StreamlinkConfig.__init__ import mygettext as _
from Plugins.Extensions.StreamlinkConfig.version import Version
import os, time, sys
# GUI (Screens)
from Components.ActionMap import ActionMap
from Components.config import *
from Components.ConfigList import ConfigListScreen
from Components.Label import Label
#from Components.Sources.StaticText import StaticText
from enigma import eTimer, eConsoleAppContainer

from Screens.ChoiceBox import ChoiceBox
from Screens.Console import Console
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Screens.Setup import SetupSummary

   
class StreamlinkConfiguration(Screen, ConfigListScreen):
    from enigma import getDesktop
    if getDesktop(0).size().width() == 1920: #definicja skin-a musi byc tutaj, zeby vti sie nie wywalalo na labelach, inaczej trzeba uzywasc zrodla statictext
        skin = """<screen name="StreamlinkConfiguration" position="center,center" size="1000,700" title="Streamlink configuration">
                    <widget name="config"     position="20,20"   zPosition="1" size="960,600" scrollbarMode="showOnDemand" />
                    <widget name="key_red"    position="20,630"  zPosition="2" size="240,30" foregroundColor="red"    valign="center" halign="left" font="Regular;22" transparent="1" />
                    <widget name="key_green"  position="260,630" zPosition="2" size="240,30" foregroundColor="green"  valign="center" halign="left" font="Regular;22" transparent="1" />
                    <widget name="key_yellow" position="500,630" zPosition="2" size="240,30" foregroundColor="yellow" valign="center" halign="left" font="Regular;22" transparent="1" />
                    <widget name="key_blue"   position="740,630" zPosition="2" size="240,30" foregroundColor="blue"   valign="center" halign="left" font="Regular;22" transparent="1" />
                  </screen>"""
    else:
        skin = """<screen name="StreamlinkConfiguration" position="center,center" size="700,400" title="Streamlink configuration">
                    <widget name="config"     position="20,20" size="640,325" zPosition="1" scrollbarMode="showOnDemand" />
                    <widget name="key_red"    position="20,350" zPosition="2" size="150,30" foregroundColor="red" valign="center" halign="left" font="Regular;22" transparent="1" />
                    <widget name="key_green"  position="170,350" zPosition="2" size="150,30" foregroundColor="green" valign="center" halign="left" font="Regular;22" transparent="1" />
                    <widget name="key_yellow" position="360,350" zPosition="2" size="150,30" foregroundColor="yellow" valign="center" halign="left" font="Regular;22" transparent="1" />
                    <widget name="key_blue"   position="500,350" zPosition="2" size="150,30" foregroundColor="blue" valign="center" halign="left" font="Regular;22" transparent="1" />
                  </screen>"""
    def buildList(self):
        print('buildList >>> self.VisibleSection = %s' % self.VisibleSection )
        self.DoBuildList.stop()
        Mlist = []
        # pilot.wp.pl
        if os.path.exists('/etc/enigma2/userbouquet.WPPL.tv'):
            fc = open('/etc/enigma2/userbouquet.WPPL.tv','r').read()
            #if 'http%3a//slplayer' in fc:
            #    Mlist.append(getConfigListEntry('\c00f2ec73' + "Obecnie kanały bukietu WPPL korzystają z odtwarzacza zewnętrznego"))
            #else:
            #    Mlist.append(getConfigListEntry('\c00f2ec73' + "Obecnie kanały bukietu WPPL korzystają z serviceapp"))
        Mlist.append(getConfigListEntry(_("Username:"), config.plugins.streamlinkSRV.WPusername))
        Mlist.append(getConfigListEntry(_("Password:"), config.plugins.streamlinkSRV.WPpassword))
        Mlist.append(getConfigListEntry(_("Check login credentials"), config.plugins.streamlinkSRV.WPlogin))
        #Mlist.append(getConfigListEntry("Przedstaw się jako:", config.plugins.streamlinkSRV.WPdevice))
        #Mlist.append(getConfigListEntry(_("Prefer DASH than HLS:"), config.plugins.streamlinkSRV.WPpreferDASH))
        #Mlist.append(getConfigListEntry(_("Delay video:"), config.plugins.streamlinkSRV.WPvideoDelay))
        Mlist.append(getConfigListEntry(_("Press OK to create %s bouquet") % "userbouquet.WPPL.tv", config.plugins.streamlinkSRV.WPbouquet))
        return Mlist
    
    def __init__(self, session, args=None):
        print('%s' % '__init__')
        self.doAction = None
        self.VisibleSection = 0
        if os.path.exists('/usr/sbin/streamlinkSRV') and os.path.islink('/usr/sbin/streamlinkSRV') and 'StreamlinkConfig/' in os.readlink('/usr/sbin/streamlinkSRV'):
            self.mySL = True
        else:
            self.mySL = False
        
        self.DoBuildList = eTimer()
        self.DoBuildList.callback.append(self.buildList)
        
        Screen.__init__(self, session)
        self.session = session

        # Summary
        self.setup_title = 'Konfiguracja pilot.wp.pl EOL'
        self.onChangedEntry = []

        # Buttons
        self["key_red"] = Label(_("Cancel"))
        
        if self.mySL == True:
            self["key_green"] = Label(_("Save"))
            self["key_blue"] = Label(_("Restart daemon"))
            if os.path.exists('/usr/lib/python2.7'):
                self["key_yellow"] = Label()
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
        ConfigListScreen.__init__(self, self.buildList(), on_change = self.changedEntry)

    def saveConfig(self):
        for x in self["config"].list:
            if len(x) >= 2:
                x[1].save()
        configfile.save()

    def save(self):
        if self.mySL == True:
            self.saveConfig()
            os.system('%s stop' % config.plugins.streamlinkSRV.binName.value)
            if config.plugins.streamlinkSRV.enabled.value:
                os.system('%s start' % config.plugins.streamlinkSRV.binName.value)
            self.VisibleSection = 0
            self.close(None)
        
    def refreshBuildList(self, ret = False):
        print('refreshBuildList >>>')
        self["config"].list = self.buildList()
        self.DoBuildList.start(50, True)
        
    def doNothing(self, ret = False):
        print('doNothing >>>')
        return
      
    def yellow(self):
        if self.mySL == True:
            if os.path.exists('/tmp/streamlinkSRV.log'):
                self.session.openWithCallback(self.doNothing ,Console, title = '/tmp/streamlinkSRV.log', cmdlist = [ 'cat /tmp/streamlinkSRV.log' ])
        
    def blue(self):
        if self.mySL == True:
            mtitle = _('Restarting daemon')
            cmd = '/usr/sbin/%s restart' % config.plugins.streamlinkSRV.binName.value
            self.session.openWithCallback(self.doNothing ,Console, title = mtitle, cmdlist = [ cmd ])
        
    def exit(self):
        self.VisibleSection = 0
        self.close(None)
        
    def prevConf(self):
        print('prevConf >>> VisibleSection = %s' % self.VisibleSection)
        self.VisibleSection -= 1
        if self.VisibleSection < 1:
            self.VisibleSection = 5
        self.refreshBuildList()
        
    def nextConf(self):
        print('nextConf >>> VisibleSection = %s' % self.VisibleSection)
        self.VisibleSection += 1
        if self.VisibleSection > 5:
            self.VisibleSection = 1
        self.refreshBuildList()
    
    def layoutFinished(self):
        print('layoutFinished')
        self.VisibleSection = 0
        self.DoBuildList.start(10, True)
        self.setTitle(self.setup_title)
        
        if os.path.exists("/usr/lib/enigma2/python/Plugins/SystemPlugins/ServiceApp/serviceapp.so"):
            self.choicesList = [("Odtwarzacz zewnętrzny (zalecany)","1e"), ("Odtwarzacz zewnętrzny (zalecany dla Vu+)","4097e"), ("gstreamer (root 4097)","4097"), ("ServiceApp gstreamer (root 5001)","5001"), ("ServiceApp ffmpeg (root 5002)","5002")]
        else:
            self.choicesList = [("Odtwarzacz zewnętrzny (zalecany)","1e"), ("Odtwarzacz zewnętrzny (zalecany dla Vu+)","4097e"), ("gstreamer (root 4097)","4097"), (_("ServiceApp not installed!"), None)]
        
    def changedEntry(self):
        print('%s' % 'changedEntry()')
        try:
            for x in self.onChangedEntry:
                x()
        except Exception as e:
            print('%s' % str(e))

    def selectionChanged(self):
        if 0:
            print('%s' % 'selectionChanged(%s)' % self["config"].getCurrent()[0])

    def getCurrentEntry(self):
        return self["config"].getCurrent()[0]

    def getCurrentValue(self):
        if len(self["config"].getCurrent()) >= 2:
            return str(self["config"].getCurrent()[1].getText())

    def createSummary(self):
        return SetupSummary

    def Okbutton(self):
        print('%s' % 'Okbutton')
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
                        self.session.openWithCallback(self.doNothing ,Console, title = "SL %s %s" % (Version, _('Credentials verification')), cmdlist = [ cmd ])
                        return
                elif currItem == config.plugins.streamlinkSRV.generateBouquet:
                    print('currItem == config.plugins.streamlinkSRV.generateBouquet')
                    bouquetFileName = currInfo.split(': ')[1].strip()
                    self.doAction = ('generate_%s.py' % bouquetFileName, '/etc/enigma2/%s' % bouquetFileName, 'anonymous','nopassword')
                ####
                print('%s' % str(self.doAction))
                if not self.doAction is None:
                    cmd = self.doAction[0]
                    bfn = self.doAction[1]
                    print('%s' % bfn)
                    if cmd == 'removeBouquet.py':
                        cmd = '/usr/bin/python /usr/lib/enigma2/python/Plugins/Extensions/StreamlinkConfig/plugins/%s' % ' '.join(self.doAction)
                        self.session.openWithCallback(self.retFromCMD ,Console, title = "SL %s %s" % (Version, _('Removing bouquet...')), cmdlist = [ cmd ])
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
            print('%s' % str(e))

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
            print("OkbuttonTextChangedConfirmed(ret ='%s')" % str(ret))
        else:
            try:
                curIndex = self["config"].getCurrentIndex()
                self["config"].list[curIndex][1].value = ret
            except Exception as e:
                print('%s' % str(e))

    def OkbuttonConfirmed(self, ret = False):
        if ret:
            self.session.openWithCallback(self.SelectedFramework, ChoiceBox, title = _("Select Multiframework"), list = self.choicesList)

    def SelectedFramework(self, ret):
        if not ret or ret == "None" or isinstance(ret, (int, float)):
            ret = (None,'4097')
        doActionPath = '/usr/lib/enigma2/python/Plugins/Extensions/StreamlinkConfig/plugins/'
        cmd = '/usr/bin/python %s%s %s %s %s' % (doActionPath,
                                                 ' '.join(self.doAction),
                                                 config.plugins.streamlinkSRV.PortNumber.value,
                                                 ret[1],
                                                 'y'
                                                )
        if self.doAction[0] == 'wpBouquet.py':
            print('%s WPuser WPpass %s %s' % (self.doAction[0], config.plugins.streamlinkSRV.PortNumber.value, ret[1]))
        else:
            print('%s' % cmd)
        self.session.openWithCallback(self.retFromCMD ,Console, title = "SL %s %s" % (Version, self.cmdTitle), cmdlist = [ cmd ])

    def reloadBouquets(self):
        from enigma import eDVBDB
        eDVBDB.getInstance().reloadBouquets()
        
    def retFromCMD(self, ret = False):
        print('retFromCMD >>>')
        self.cleanBouquets_tvradio()
        self.reloadBouquets()
        msg = _("Bouquets has been reloaded")
        self.session.openWithCallback(self.refreshBuildList,MessageBox, msg, MessageBox.TYPE_INFO, timeout = 5)