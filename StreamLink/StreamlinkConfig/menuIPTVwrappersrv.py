# -*- coding: utf-8 -*-
from __future__ import absolute_import #zmiana strategii ladowanie modulow w py2 z relative na absolute jak w py3
from Plugins.Extensions.StreamlinkConfig.__init__ import mygettext as _ , readCFG
from Plugins.Extensions.StreamlinkConfig.version import Version
from Plugins.Extensions.StreamlinkConfig.plugins.azmanIPTVsettings import get_azmanIPTVsettings
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

try:
    from emukodi.xbmcE2 import *
    from emukodi.e2Console import emukodiConsole
except Exception as e:
    print('AQQ ERROR', str(e))
    addons_path = 'ERROR'
    emukodi_path = 'ERROR'
    emukodiConsole = Console
    
class StreamlinkConfiguration(Screen, ConfigListScreen):
    from enigma import getDesktop
    if getDesktop(0).size().width() == 1920: #definicja skin-a musi byc tutaj, zeby vti sie nie wywalalo na labelach, inaczej trzeba uzywasc zrodla statictext
        skin = """<screen name="StreamlinkConfiguration" position="center,center" size="1200,700" title="Streamlink configuration">
                    <widget name="config"     position="20,20"   zPosition="1" size="1160,600" scrollbarMode="showOnDemand" />
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
        self.DoBuildList.stop()
        Mlist = []
        #budowanie listy
        for fb in sorted(os.listdir("/etc/enigma2"), key=str.lower):
            if fb.startswith('userbouquet.') and fb.endswith('.tv') and not fb in ['userbouquet.LastScanned.tv']:
                print(fb)
                with open('/etc/enigma2/%s' % fb, 'r') as fp:
                    try:
                        fpc = fp.read()
                    except Exception:
                        pass
                    fp.close()
                    services = fpc.count('#SERVICE ') - fpc.count('64:0:0:0:0:0:0:0:0::')
                    IPTVservices = services - fpc.count('::')
                    if IPTVservices > 0:
                        myCMD = ('/usr/bin/python', 
                                 '/usr/lib/enigma2/python/Plugins/Extensions/StreamlinkConfig/plugins/changeLocalBouquet.py', 
                                 fb,
                                 'w2s', #marker zmiany wrappera
                                )
                        Mlist.append(getConfigListEntry("Zmień wrapper na serwer w %s/%s serwisach IPTV bukietu %s" % (IPTVservices, services, fb.replace('userbouquet','')),
                                                        config.plugins.streamlinkSRV.unmanagedBouquet,
                                                        myCMD
                                                        )
                                    )
        return Mlist
    
    def __init__(self, session, args=None):
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
        self.setup_title = _("Streamlink Configuration EOL")
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
        self.DoBuildList.start(10, True)
        self.setTitle(self.setup_title)
        
        if os.path.exists("/usr/lib/enigma2/python/Plugins/SystemPlugins/ServiceApp/serviceapp.so"):
            self.choicesList = [(_("Don't change"),"0"),("gstreamer (root 4097)","4097"),("ServiceApp gstreamer (root 5001)","5001"), ("ServiceApp ffmpeg (root 5002)","5002"),("Hardware (root 1) wymagany do PIP","1")]
        else:
            self.choicesList = [(_("Don't change"),"0"),("gstreamer (root 4097)","4097"),("Hardware (root 1) wymagany do PIP","1"),(_("ServiceApp not installed!"), None)]
        
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
            curIndex = self["config"].getCurrentIndex()
            selectedItem = self["config"].list[curIndex]
            self.doAction = selectedItem[2]
            myCMD = ' '.join(self.doAction)
            self.cleanBouquets_tvradio()
            self.session.openWithCallback(self.retFromCMD,
                                              Console, 
                                              title = "SL %s %s" % (Version, 'Zmiana wrappera na serwer...'),
                                              cmdlist = [ myCMD ]
                                              )
            return
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
            
    def reloadBouquets(self):
        from enigma import eDVBDB
        eDVBDB.getInstance().reloadBouquets()
        
    def retFromCMD(self, ret = False):
        print('retFromCMD >>>')
        self.cleanBouquets_tvradio()
        self.reloadBouquets()
        msg = _("Bouquets has been reloaded")
        self.session.openWithCallback(self.refreshBuildList,MessageBox, msg, MessageBox.TYPE_INFO, timeout = 5)
