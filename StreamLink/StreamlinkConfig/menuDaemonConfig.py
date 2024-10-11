# -*- coding: utf-8 -*-
from __future__ import absolute_import #zmiana strategii ladowanie modulow w py2 z relative na absolute jak w py3
from Plugins.Extensions.StreamlinkConfig.__init__ import mygettext as _ , readCFG , DBGlog
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
from Screens.Standby import TryQuitMainloop

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
        if not os.path.exists('/usr/lib/enigma2/python/Plugins/Extensions/StreamlinkConfig/NoZapWrappers'):
            Mlist.append(getConfigListEntry('\c00289496' + "*** Ten system WSPIERA wrappery :) ***"))
        else:
            Mlist.append(getConfigListEntry('\c00981111' + "*** Ten system NIE wspiera wrapperów, korzystaj TYLKO z demona (127.0.0.1 w liście)!!! ***"))
        Mlist.append(getConfigListEntry("Aktywacja:", config.plugins.streamlinkSRV.enabled, 'streamlinkSRV.enabled'))
        if config.plugins.streamlinkSRV.enabled.value:
            Mlist.append(getConfigListEntry("Tryb pracy streamlinka:", config.plugins.streamlinkSRV.binName, 'streamlinkSRV.binName'))
            if config.plugins.streamlinkSRV.binName.value == 'streamlinkSRV':
                Mlist.append(getConfigListEntry("Aktywny odtwarzacz streamlinka:", config.plugins.streamlinkSRV.SRVmode, 'streamlinkSRV.SRVmode'))
            #Mlist.append(getConfigListEntry("Aktywny odtwarzacz materiałów DRM:", config.plugins.streamlinkSRV.DRMmode, 'streamlinkSRV.DRMmode'))
            Mlist.append(getConfigListEntry(_("stop deamon on standby:"), config.plugins.streamlinkSRV.StandbyMode))
        #KONFIGURACJA SERVICEAPP
        Mlist.append(getConfigListEntry(" "))
        Mlist.append(getConfigListEntry('\c00f83426' + "*** Konfiguracja ServiceApp ***"))
        Mlist.append(getConfigListEntry("System odtwarzania wewnętrzny E2/ServiceApp (wył/wł)", config.plugins.serviceapp.servicemp3.replace))
        Mlist.append(getConfigListEntry("Odtwarzacz systemu ServiceApp", config.plugins.serviceapp.servicemp3.player))
        #KONFIGURACJA LOGOWANIA
        Mlist.append(getConfigListEntry(" "))
        Mlist.append(getConfigListEntry('\c00489426' + "*** Konfiguracja logowania - WŁĄCZ wszystko ***"))
        Mlist.append(getConfigListEntry("Włącz dziennik debugowania", config.crash.enabledebug))
        Mlist.append(getConfigListEntry("Lokalizacja logów", config.crash.debug_path))
        Mlist.append(getConfigListEntry("Awaria obsługi pythona", config.crash.bsodpython))
        Mlist.append(getConfigListEntry("Dołącz dane ładowania ekranu", config.crash.debugScreens))
        Mlist.append(getConfigListEntry("Debuguj główną przyczynę błędu", config.crash.pystackonspinner))
        #info o vlc
        Mlist.append(getConfigListEntry(" "))
        Mlist.append(getConfigListEntry("Support VLC: użyj skryptu z folderu wtyczki 'bin/E-TV polska mod j00zek.lua'"))
        self["config"].list = Mlist
        self["config"].l.setList(Mlist)
            
        return Mlist
    
    def __init__(self, session, args=None):
        DBGlog('%s' % '__init__')
        if os.path.exists('/usr/sbin/streamlinkSRV') and os.path.islink('/usr/sbin/streamlinkSRV') and 'StreamlinkConfig/' in os.readlink('/usr/sbin/streamlinkSRV'):
            self.mySL = True
        else:
            self.mySL = False
        
        self.DoBuildList = eTimer()
        self.DoBuildList.callback.append(self.buildList)
        
        Screen.__init__(self, session)
        self.session = session

        # Summary
        self.setup_title = 'Konfiguracja demona'
        self.onChangedEntry = []

        # Buttons
        self["key_red"] = Label(_("Cancel"))
        
        if self.mySL == True:
            self["key_green"] = Label(_("Save"))
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
            }, -2)
        
        self.onLayoutFinish.append(self.layoutFinished)
        ConfigListScreen.__init__(self, [], on_change = self.changedEntry)

    def saveConfig(self):
        try:
            for x in self["config"].list:
                if len(x) >= 2:
                    x[1].save()
                    try:
                        if len(x) > 2:
                            with open(os.path.join('/etc/streamlink/',x[2]), 'w') as f:
                                f.write(str(x[1].value))
                                f.close()
                    except Exception:
                        pass
            configfile.save()
        except Exception:
            pass

    def save(self):
        if self.mySL == True:
            self.saveConfig()
            if 0:
                os.system('%s stop' % config.plugins.streamlinkSRV.binName.value)
                if config.plugins.streamlinkSRV.enabled.value:
                    os.system('%s start' % config.plugins.streamlinkSRV.binName.value)
            self.session.openWithCallback(self.rebootTunercb,MessageBox, "Zmiany wymagają restartu systemu.\nZrestartować teraz?", MessageBox.TYPE_YESNO, default = True)

    def rebootTunercb(self,answer):
        if answer is True:
            self.session.open(TryQuitMainloop, 2)
        else:
            self.close(None)
        
    def doNothing(self, ret = False):
        return
      
    def yellow(self):
        if 0: #self.mySL == True:
            if os.path.exists('/tmp/streamlinkSRV.log'):
                self.session.openWithCallback(self.doNothing ,Console, title = '/tmp/streamlinkSRV.log', cmdlist = [ 'cat /tmp/streamlinkSRV.log' ])
        
    def blue(self):
        if 0: #if self.mySL == True:
            mtitle = _('Restarting daemon')
            cmd = '/usr/sbin/%s restart' % config.plugins.streamlinkSRV.binName.value
            self.session.openWithCallback(self.doNothing ,Console, title = mtitle, cmdlist = [ cmd ])
        
    def exit(self):
        self.close(None)
        
    def layoutFinished(self):
        print('layoutFinished')
        self.DoBuildList.start(10, True)
        self.setTitle(self.setup_title)
        
    def changedEntry(self):
        DBGlog('%s' % 'changedEntry()')
        try:
            for x in self.onChangedEntry:
                x()
        except Exception as e:
            DBGlog('%s' % str(e))
        self.buildList()

    #def selectionChanged(self):
    #    self.DoBuildList.start(10, True)

    #def getCurrentEntry(self):
    #    return self["config"].getCurrent()[0]

    #def getCurrentValue(self):
    #    if len(self["config"].getCurrent()) >= 2:
    #        return str(self["config"].getCurrent()[1].getText())

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
        except Exception as e:
            DBGlog('%s' % str(e))

    def OkbuttonTextChangedConfirmed(self, ret ):
        if ret is None:
            DBGlog("OkbuttonTextChangedConfirmed(ret ='%s')" % str(ret))
        else:
            try:
                curIndex = self["config"].getCurrentIndex()
                self["config"].list[curIndex][1].value = ret
            except Exception as e:
                DBGlog('%s' % str(e))
