# -*- coding: utf-8 -*-
from Plugins.Extensions.StreamlinkConfig.__init__ import mygettext as _ , DBGlog
from Plugins.Extensions.StreamlinkConfig.version import Version
import os, time, sys
# GUI (Screens)
from Components.ActionMap import ActionMap
from Components.config import *
from Components.ConfigList import ConfigListScreen
from Components.Label import Label
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
    print('[SLK] błąd ładowania emukodi', str(e))
    addons_path = 'ERROR'
    emukodi_path = 'ERROR'
    emukodiConsole = Console

config.plugins.streamlinkSRV.streamlinkconfig = NoSave(ConfigNothing())
config.plugins.streamlinkSRV.streamlinkEMUKODIconfig = NoSave(ConfigNothing())
    
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
        self.DoBuildList.stop()
        Mlist = []
        #cdmStatus == True:
        pythonRunner = '/usr/bin/python'
        addonScript = 'plugin.video.pilot.wp/addon.py'
        runAddon = '%s %s' % (pythonRunner, os.path.join(addons_path, addonScript))
        webServer = ''
                            
        if not os.path.exists('/etc/streamlink/pilot.wp'):
            os.system('mkdir -p /etc/streamlink/pilot.wp')
        for cfgFile in ['username', 'password', 'mode', 'netviapisessid']:
            if not os.path.exists('/etc/streamlink/pilot.wp/%s' % cfgFile): os.system('touch /etc/streamlink/pilot.wp/%s' % cfgFile)
        #info
        if os.path.exists('/etc/enigma2/userbouquet.pilot.wp.tv'):
            fc = open('/etc/enigma2/userbouquet.pilot.wp.tv','r').read()
            if 'http%3a//cdmplayer' in fc:
                Mlist.append(getConfigListEntry('\c00f2ec73' + "Obecnie kanały bukietu pilot.wp korzystają z odtwarzacza zewnętrznego"))
            else:
                Mlist.append(getConfigListEntry('\c00f2ec73' + "Obecnie kanały bukietu pilot.wp korzystają z serviceapp"))

        if open('/etc/streamlink/pilot.wp/username','r').read().strip() == '' and config.plugins.streamlinkSRV.WPusername.value == '':
            Mlist.append(getConfigListEntry( 'Brak danych w /etc/streamlink/pilot.wp/username' , config.plugins.streamlinkSRV.streamlinkconfig))
        elif open('/etc/streamlink/pilot.wp/password','r').read().strip() == '' and config.plugins.streamlinkSRV.WPpassword.value == '':
            Mlist.append(getConfigListEntry( 'Brak danych w /etc/streamlink/pilot.wp/password' , config.plugins.streamlinkSRV.streamlinkconfig))
        elif open('/etc/streamlink/pilot.wp/netviapisessid','r').read().strip() == '':
            open('/etc/streamlink/pilot.wp/mode','w').write("0") #marker logowanie po username i hasle
            emuKodiCmdsList = []
            emuKodiCmdsList.append(runAddon + " '1' '' 'resume:false'") #logowanie nastepuje bez podania trybu
            autoClose = True #ustawienie parametrow w zaleznoci od akcji
            webServer = ''
            Mlist.append(getConfigListEntry( "Zaloguj do pilot.wp", config.plugins.streamlinkSRV.streamlinkEMUKODIconfig, ('pilot.wp', 'ActionConfirmed', emuKodiCmdsList, autoClose, webServer, addonScript)))
        else:
            if open('/etc/streamlink/pilot.wp/netviapisessid','r').read().strip() != '':
                #wylogowanie
                emuKodiCmdsList = []
                emuKodiCmdsList.append("rm -f /etc/streamlink/pilot.wp/*")
                emuKodiCmdsList.append("echo 'Wylogowano z serwisu cda i usunięto dane tymczasowe'")
                emuKodiCmdsList.append("sleep 2")
                autoClose = True #ustawienie parametrow w zaleznoci od akcji
                Mlist.append(getConfigListEntry( 'WYLOGUJ!!!', config.plugins.streamlinkSRV.streamlinkEMUKODIconfig, ('pilot.wp', 'ActionConfirmed', emuKodiCmdsList, autoClose, webServer, addonScript)))
            #pobieranie listy
            emuKodiCmdsList = []
            emuKodiCmdsList.append("echo 'Logowanie do serwisu'")
            emuKodiCmdsList.append(runAddon + " '1' '' 'resume:false'") #logowanie nastepuje bez podania trybu
            emuKodiCmdsList.append("echo 'Pobieranie listy kanałów'")
            emuKodiCmdsList.append(runAddon + " '1' '?action=BUILD_M3U' 'resume:false'")
            autoClose = True #ustawienie parametrow w zaleznoci od akcji
            webServer = ''
            Mlist.append(getConfigListEntry( _("Press OK to create bouquet for") + ' WP Pilot' , config.plugins.streamlinkSRV.streamlinkEMUKODIconfig, ('pilot.wp', 'userbouquet', emuKodiCmdsList, autoClose, webServer, addonScript)))
        return Mlist
    
    def __init__(self, session, args=None):
        DBGlog('%s' % '__init__')
        self.wybranyFramework = '4097'
        if os.path.exists('/usr/sbin/streamlinkSRV') and os.path.islink('/usr/sbin/streamlinkSRV') and 'StreamlinkConfig/' in os.readlink('/usr/sbin/streamlinkSRV'):
            self.mySL = True
        else:
            self.mySL = False
        
        self.DoBuildList = eTimer()
        self.DoBuildList.callback.append(self.buildList)
        
        Screen.__init__(self, session)
        self.session = session

        # Summary
        self.setup_title = 'Konfguracja WP Pilot'
        self.onChangedEntry = []

        # Buttons
        self["key_red"] = Label(_("Cancel"))
        self["key_yellow"] = Label()
        self["key_blue"] = Label()
        
        if self.mySL == True:
            self["key_green"] = Label(_("Save"))
        else:
            self["key_green"] = Label()

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
            self.close(None)
        
    def refreshBuildList(self, ret = False):
        DBGlog('refreshBuildList >>>')
        self["config"].list = self.buildList()
        self.DoBuildList.start(50, True)
        
    def doNothing(self, ret = False):
        DBGlog('doNothing >>>')
        return
      
    def yellow(self):
        pass
        
    def blue(self):
        pass
        
    def exit(self):
        self.close(None)
        
    def prevConf(self):
        self.refreshBuildList()
        
    def nextConf(self):
        self.refreshBuildList()
    
    def layoutFinished(self):
        print('layoutFinished')
        self.DoBuildList.start(10, True)
        self.setTitle(self.setup_title)
        
        if os.path.exists("/usr/lib/enigma2/python/Plugins/SystemPlugins/ServiceApp/serviceapp.so"):
            self.choicesList = [("Odtwarzacz zewnętrzny (zalecany)","1e"), ("Odtwarzacz zewnętrzny (Vu+)","4097e"), ("gstreamer (root 4097)","4097"),("ServiceApp gstreamer (root 5001)","5001"), ("ServiceApp ffmpeg (root 5002)","5002")]
        else:
            self.choicesList = [("Odtwarzacz zewnętrzny (zalecany)","1e"),  ("Odtwarzacz zewnętrzny (Vu+)","4097e"), ("gstreamer (root 4097)","4097"),(_("ServiceApp not installed!"), None)]
        
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
            curIndex = self["config"].getCurrentIndex()
            selectedItem = self["config"].list[curIndex]
            if len(selectedItem) >= 2:
                currItem = selectedItem[1]
                currInfo = selectedItem[0]
                if isinstance(currItem, ConfigText):
                    from Screens.VirtualKeyBoard import VirtualKeyBoard
                    self.session.openWithCallback(self.OkbuttonTextChangedConfirmed, VirtualKeyBoard, title=(currInfo), text = currItem.value)
                elif currItem == config.plugins.streamlinkSRV.streamlinkEMUKODIconfig: #bouquets based on KODI plugins
                    DBGlog('currItem == config.plugins.streamlinkSRV.streamlinkEMUKODIconfig')
                    self.emuKodiActions(selectedItem)
                    return
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

    def reloadBouquets(self):
        from enigma import eDVBDB
        eDVBDB.getInstance().reloadBouquets()
        
    def retFromCMD(self, ret = False):
        DBGlog('retFromCMD >>>')
        self.cleanBouquets_tvradio()
        self.reloadBouquets()
        msg = _("Bouquets has been reloaded")
        self.session.openWithCallback(self.refreshBuildList,MessageBox, msg, MessageBox.TYPE_INFO, timeout = 5)

    def emuKodiConsoleCallback(self, ret = False):
        if self.emuKodiAction[1] == 'userbouquet': #akcja
            self.retFromCMD(ret)
        else:
            self.refreshBuildList()

    def emuKodiActionConfirmed(self, ret = False):
        if ret:
            curIndex = self["config"].getCurrentIndex()
            selectedItem = self["config"].list[curIndex]
            self.emuKodiAction = selectedItem[2] #('playermb', 'login', emuKodiCmdsList, autoClose, webServer, addonScript)
            dostawca = self.emuKodiAction[0]
            akcja = self.emuKodiAction[1]
            emuKodiCmdsList = self.emuKodiAction[2]
            autoClose = self.emuKodiAction[3]
            webServer = self.emuKodiAction[4]
            addonScript = self.emuKodiAction[5]
            pythonRunner = '/usr/bin/python'
            if akcja == 'userbouquet':
                plikBukietu = '/etc/enigma2/userbouquet.%s.tv' % dostawca
                emuKodiCmdsList.append('%s %s %s "%s" %s' % (pythonRunner, os.path.join(emukodi_path, 'e2Bouquets.py'), plikBukietu, addonScript, self.wybranyFramework))
            #uruchomienie lancucha komend
            if webServer != '':
                pass
            if len(emuKodiCmdsList) > 0:
                cleanWorkingDir()
                log("===== %s - %s ====" % (dostawca, akcja))
                self.session.openWithCallback(self.emuKodiConsoleCallback ,emukodiConsole, title = "SL %s %s-%s" % (Version, 'EmuKodi', dostawca), 
                                                cmdlist = emuKodiCmdsList, closeOnSuccess = autoClose)
            
    def emuKodiActions(self, selectedItem):
        DBGlog('emuKodiActions(%s)' % str(selectedItem))
        if len(selectedItem) < 3:
            self.session.openWithCallback(self.doNothing,MessageBox, 'Nie wiem co zrobić ;)', MessageBox.TYPE_INFO, timeout = 5)
            return
        else:
            self.emuKodiAction = selectedItem[2] #('playermb', 'login', emuKodiCmdsList, autoClose, webServer, addonScript)
            dostawca = self.emuKodiAction[0]
            akcja = self.emuKodiAction[1]
            if akcja == 'userbouquet':
                #pobranie swiezych definicji
                os.system('wget https://raw.githubusercontent.com/azman26/EPGazman/main/azman_channels_mappings.py -O /usr/lib/enigma2/python/Plugins/Extensions/StreamlinkConfig/plugins/azman_channels_mappings.py')
                plikBukietu = '/etc/enigma2/userbouquet.%s.tv' % dostawca
                if os.path.exists(plikBukietu): MsgInfo = "Zaktualizować plik %s ?" % plikBukietu
                else: MsgInfo = "Utworzyć plik %s ?" % plikBukietu
                self.session.openWithCallback(self.userbouquetConfirmed, MessageBox, MsgInfo, MessageBox.TYPE_YESNO, default = False, timeout = 15)
                return
            else:
                self.emuKodiActionConfirmed(True)
        return

    def userbouquetConfirmed(self, ret = False):
        if ret:
            self.session.openWithCallback(self.SelectedFramework, ChoiceBox, title = _("Select Multiframework"), list = self.choicesList)

    def SelectedFramework(self, ret):
        if not ret or ret == "None" or isinstance(ret, (int, float)):
            ret = (None,'4097')
        self.wybranyFramework = ret[1]
        self.emuKodiActionConfirmed(True)
