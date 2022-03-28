# -*- coding: utf-8 -*-

# maintainer: <info@vuplus-support.org>

#This plugin is free software, you are allowed to
#modify it (if you keep the license),
#but you are not allowed to distribute/publish
#it without source code (this version and your modifications).
#This means you also have to distribute
#source code of your modifications.
#autoshutdown.png <from http://www.everaldo.com>

from Components.ActionMap import ActionMap
from Components.config import *
from Components.ConfigList import ConfigListScreen
from Components.FileList import FileList
from Components.Harddisk import harddiskmanager
from Components.Label import Label
from Components.Language import language
from Components.Sources.StaticText import StaticText
from Components.Task import job_manager
from enigma import eTimer, iRecordableService, eActionMap, eServiceReference
from Plugins.Plugin import PluginDescriptor
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from time import time, localtime, mktime
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, pathExists
from Tools import Notifications

import gettext
import NavigationInstance
import os
import Screens.Standby

def calculateTime(hours, minutes, day_offset = 0):
    cur_time = localtime()
    unix_time = mktime((cur_time.tm_year, cur_time.tm_mon, cur_time.tm_mday, hours, minutes, 0, cur_time.tm_wday, cur_time.tm_yday, cur_time.tm_isdst)) + day_offset
    return unix_time


def localeInit():
    lang = language.getLanguage()[:2]
    os.environ["LANGUAGE"] = lang
    gettext.bindtextdomain("plugin-AutoShutDown", \
        resolveFilename(SCOPE_PLUGINS, 'SystemPlugins/AutoShutDown/locale'))

def _(txt):
    t = gettext.dgettext("plugin-AutoShutDown", txt)
    if t == txt:
            t = gettext.gettext(txt)
    return t

localeInit()
language.addCallback(localeInit)

config.autoshutdown = ConfigSubsection()
config.autoshutdown.time = ConfigInteger(default = 120, limits = (1, 1440))
config.autoshutdown.inactivetime = ConfigInteger(default = 15, limits = (1, 1440))
config.autoshutdown.autostart = ConfigEnableDisable(default = False)
config.autoshutdown.enableinactivity = ConfigEnableDisable(default = True)
config.autoshutdown.inactivityaction = ConfigSelection(default = "standby", choices = [("standby", _("Standby")), ("deepstandby", _("Deepstandby"))])
config.autoshutdown.inactivitymessage = ConfigYesNo(default = True)
config.autoshutdown.messagetimeout = ConfigInteger(default = 5, limits = (1, 99))
config.autoshutdown.epgrefresh = ConfigYesNo(default = True)
config.autoshutdown.plugin = ConfigYesNo(default = False)
config.autoshutdown.play_media = ConfigYesNo(default = False)
config.autoshutdown.media_file = ConfigText(default = "")
config.autoshutdown.disable_at_ts = ConfigYesNo(default = False)
config.autoshutdown.disable_net_device = ConfigYesNo(default = False)
config.autoshutdown.disable_hdd = ConfigYesNo(default = False)
config.autoshutdown.net_device = ConfigIP(default = [0,0,0,0])
config.autoshutdown.exclude_time_in = ConfigYesNo(default = False)
config.autoshutdown.exclude_time_in_begin = ConfigClock(default = calculateTime(20,0))
config.autoshutdown.exclude_time_in_end = ConfigClock(default = calculateTime(0,0))
config.autoshutdown.exclude_time_off = ConfigYesNo(default = False)
config.autoshutdown.exclude_time_off_begin = ConfigClock(default = calculateTime(20,0))
config.autoshutdown.exclude_time_off_end = ConfigClock(default = calculateTime(0,0))
config.autoshutdown.fake_entry = NoSave(ConfigNothing())

def checkIP(ip_address):
    ip_address = "%s.%s.%s.%s" % (ip_address[0], ip_address[1], ip_address[2], ip_address[3])
    ping_ret = os.system("ping -q -w1 -c1 " + ip_address)
    if ping_ret == 0:
        return True
    else:
        return False

def checkHardDisk():
    for hdd in harddiskmanager.HDDList():
        if not hdd[1].isSleeping():
            return True
    return False

def checkExcludeTime(begin_config, end_config):
    (begin_h, begin_m) = begin_config
    (end_h, end_m) = end_config
    cur_time = time()
    begin = calculateTime(begin_h, begin_m)
    end = calculateTime(end_h, end_m)
    if begin >= end:
        if cur_time < end:
            day_offset = -24.0 * 3600.0
            begin = calculateTime(begin_h, begin_m, day_offset)
        elif cur_time > end:
            day_offset = 24.0 * 3600.0
            end = calculateTime(end_h, end_m, day_offset)
        else:
            return False
    if cur_time > begin and cur_time < end:
        return True
    return False

class AutoShutDownActions:
    
    def __init__(self):
        self.oldservice = None
    
    def cancelShutDown(self):
        from Screens.Standby import inStandby
        if not inStandby:
            self.stopKeyTimer()
            self.startKeyTimer()
        else:
            self.stopTimer()
            self.startTimer()
    
    def doShutDown(self):
        do_shutdown = True

        jobs = job_manager.getPendingJobs()
        if jobs:
            print("[AutoShutDown] there are running jobs  --> ignore shutdown callback")
            do_shutdown = False

        if config.autoshutdown.disable_net_device.value and checkIP(config.autoshutdown.net_device.value):
            print("[AutoShutDown] network device is not down  --> ignore shutdown callback")
            do_shutdown = False

        if config.autoshutdown.exclude_time_off.value:
            begin = config.autoshutdown.exclude_time_off_begin.value
            end = config.autoshutdown.exclude_time_off_end.value
            if checkExcludeTime(begin, end):
                print("[AutoShutDown] shutdown timer end but we are in exclude interval --> ignore power off")
                do_shutdown = False
        
        if config.autoshutdown.epgrefresh.value == True and os.path.exists("/usr/lib/enigma2/python/Plugins/Extensions/EPGRefresh/EPGRefresh.py"):
            begin = config.plugins.epgrefresh.begin.value
            end = config.plugins.epgrefresh.end.value
            if checkExcludeTime(begin, end):
                print("[AutoShutDown] in EPGRefresh interval => restart of Timer")
                do_shutdown = False
        
        if config.autoshutdown.disable_hdd.value and checkHardDisk():
            print("[AutoShutDown] At least one hard disk is active  --> ignore shutdown callback")
            do_shutdown = False
        
        if do_shutdown:
            print("[AutoShutDown] PowerOff STB")
            session.open(Screens.Standby.TryQuitMainloop,1)
        else:
            self.cancelShutDown()
    
    def enterStandBy(self):
        print("[AutoShutDown] STANDBY . . . ")
        #Notifications.AddNotification(Screens.Standby.Standby)
        session.open(Screens.Standby.Standby)
    
    def startTimer(self):
        if config.autoshutdown.autostart.value == True:
            print("[AutoShutDown] Starting ShutDownTimer")
            shutdowntime = config.autoshutdown.time.value*60000
            self.AutoShutDownTimer = eTimer()
            self.AutoShutDownTimer.start(shutdowntime, True)
            self.AutoShutDownTimer.callback.append(shutdownactions.doShutDown)
    
    def stopTimer(self):
        try:
            if self.AutoShutDownTimer.isActive():
                print("[AutoShutDown] Stopping ShutDownTimer")
                self.AutoShutDownTimer.stop()
        except:
            print("[AutoShutDown] No ShutDownTimer to stop")
    
    def startKeyTimer(self):
        if config.autoshutdown.enableinactivity.value == True:
            inactivetime = config.autoshutdown.inactivetime.value*60000
            self.AutoShutDownKeyTimer = eTimer()
            self.AutoShutDownKeyTimer.start(inactivetime, True)
            self.AutoShutDownKeyTimer.callback.append(shutdownactions.endKeyTimer)
    
    def stopKeyTimer(self):
        try:
            self.AutoShutDownKeyTimer.stop()
        except:
            print("[AutoShutDown] No inactivity timer to stop")
    
    def endKeyTimer(self):
        do_action = True
        
        if config.autoshutdown.inactivityaction.value == "deepstandby"  and config.autoshutdown.disable_net_device.value and checkIP(config.autoshutdown.net_device.value):
            print("[AutoShutDown] network device is not down  --> ignore shutdown callback")
            do_action = False
        
        if config.autoshutdown.disable_at_ts.value:
            running_service = session.nav.getCurrentService()
            timeshift_service = running_service and running_service.timeshift()
            
            if timeshift_service and timeshift_service.isTimeshiftActive():
                print("[AutoShutDown] inactivity timer end but timeshift is active --> ignore inactivity action")
                do_action = False
        
        if config.autoshutdown.exclude_time_in.value:
            begin = config.autoshutdown.exclude_time_in_begin.value
            end = config.autoshutdown.exclude_time_in_end.value
            if checkExcludeTime(begin, end):
                print("[AutoShutDown] inactivity timer end but we are in exclude interval --> ignore inactivity action")
                do_action = False
            
        if do_action:
            if config.autoshutdown.inactivitymessage.value == True:
                self.asdkeyaction = None
                if config.autoshutdown.inactivityaction.value == "standby":
                    self.asdkeyaction = _("Go to standby")
                elif config.autoshutdown.inactivityaction.value == "deepstandby":
                    self.asdkeyaction = _("Power off STB")
                if config.autoshutdown.play_media.value and os.path.exists(config.autoshutdown.media_file.value):
                    current_service = session.nav.getCurrentlyPlayingServiceReference()
                    if self.oldservice is None:
                        self.oldservice = current_service
                    media_service = eServiceReference(4097, 0, config.autoshutdown.media_file.value)
                    session.nav.playService(media_service)
                session.openWithCallback(shutdownactions.actionEndKeyTimer, MessageBox, _("AutoShutDown: %s ?") % self.asdkeyaction, MessageBox.TYPE_YESNO, timeout=config.autoshutdown.messagetimeout.value)
            else:
                res = True
                shutdownactions.actionEndKeyTimer(res)
        else:
            self.startKeyTimer()
    
    def actionEndKeyTimer(self, res):
        if config.autoshutdown.play_media.value and os.path.exists(config.autoshutdown.media_file.value):
            session.nav.playService(self.oldservice)
        
        if res == True:
            if config.autoshutdown.inactivityaction.value == "standby":
                print("[AutoShutDown] inactivity timer end => go to standby")
                self.enterStandBy()
            elif config.autoshutdown.inactivityaction.value == "deepstandby":
                print("[AutoShutDown] inactivity timer end => shutdown")
                self.doShutDown()
        else:
            if config.autoshutdown.play_media.value and os.path.exists(config.autoshutdown.media_file.value):
                self.oldservice = None

shutdownactions = AutoShutDownActions()

def autostart(reason, **kwargs):
    global session
    if kwargs.has_key("session") and reason == 0:
        session = kwargs["session"]
        print("[AutoShutDown] start....")
        config.misc.standbyCounter.addNotifier(standbyCounterChanged, initial_call = False)
        ## from InfoBarGenerics.py
        eActionMap.getInstance().bindAction('', -0x7FFFFFFF, keyPressed)
        ##
        shutdownactions.startKeyTimer()

def keyPressed(key, flag):
    if config.autoshutdown.enableinactivity.value == True:
        from Screens.Standby import inStandby
        if not inStandby:
            if flag == 1:
                shutdownactions.stopKeyTimer()
                shutdownactions.startKeyTimer()
    return 0

def standbyCounterChanged(configElement):
    print("[AutoShutDown] go to standby . . .")
    if leaveStandby not in Screens.Standby.inStandby.onClose:
        Screens.Standby.inStandby.onClose.append(leaveStandby)
    shutdownactions.startTimer()
    shutdownactions.stopKeyTimer()

def leaveStandby():
    print("[AutoShutDown] leave standby . . .")
    shutdownactions.stopTimer()
    shutdownactions.startKeyTimer()

def main(session, **kwargs):
    print("[AutoShutDown] Open Configuration")
    session.open(AutoShutDownConfiguration)

def startSetup(menuid):
    if menuid != "shutdown":
        return [ ]
    return [(_("AutoShutDown settings") , main, "autoshutdown_setup", 60)]

def Plugins(**kwargs):
        if config.autoshutdown.plugin.value:
            return [PluginDescriptor(where = [PluginDescriptor.WHERE_SESSIONSTART, PluginDescriptor.WHERE_AUTOSTART], fnc = autostart),
                PluginDescriptor(name=_("AutoShutDown Setup"), description=_("configure automated power off / standby"), where = PluginDescriptor.WHERE_MENU, fnc=startSetup),
                PluginDescriptor(name=_("AutoShutDown Setup"), description=_("configure automated power off / standby"), where = PluginDescriptor.WHERE_PLUGINMENU, icon="autoshutdown.png", fnc=main),
                PluginDescriptor(name=_("AutoShutDown Setup"), description=_("configure automated power off / standby"), where = PluginDescriptor.WHERE_EXTENSIONSMENU, fnc=main)]
        else:
            return [PluginDescriptor(where = [PluginDescriptor.WHERE_SESSIONSTART, PluginDescriptor.WHERE_AUTOSTART], fnc = autostart),
                PluginDescriptor(name=_("AutoShutDown Setup"), description=_("configure automated power off / standby"), where = PluginDescriptor.WHERE_MENU, fnc=startSetup)]

class AutoShutDownConfiguration(Screen, ConfigListScreen):
    skin = """
        <screen position="center,center" size="720,500" title="AutoShutDown" >
        <widget name="config" position="10,10" size="700,350" scrollbarMode="showOnDemand" enableWrapAround="1"/>
        <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/SystemPlugins/AutoShutDown/pic/button_red.png" zPosition="2" position="10,470" size="25,25" alphatest="on" />
        <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/SystemPlugins/AutoShutDown/pic/button_green.png" zPosition="2" position="150,470" size="25,25" alphatest="on" />
        <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/SystemPlugins/AutoShutDown/pic/button_yellow.png" zPosition="2" position="240,470" size="25,25" alphatest="on" />
        <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/SystemPlugins/AutoShutDown/pic/shutdown.png" zPosition="2" position="275,360" size="100,100" alphatest="blend" />
        <widget name="buttonred" position="40,472" size="100,20" valign="center" halign="left" zPosition="2" foregroundColor="white" font="Regular;18"/>
        <widget name="buttongreen" position="180,472" size="70,20" valign="center" halign="left" zPosition="2" foregroundColor="white" font="Regular;18"/>
        <widget name="buttonyellow" position="270,472" size="100,20" valign="center" halign="left" zPosition="2" foregroundColor="white" font="Regular;18"/>
        </screen>"""

    def __init__(self, session, args = 0):
        self.session = session
        Screen.__init__(self, session)

        self.createConfigList()
        self.onShown.append(self.setWindowTitle)
        ConfigListScreen.__init__(self, self.list, session = self.session, on_change = self.changedEntry)

        self["buttonred"] = Label(_("Exit"))
        self["buttongreen"] = Label(_("OK"))
        self["buttonyellow"] = Label(_("Default"))
        self["setupActions"] = ActionMap(["SetupActions", "ColorActions"],
            {
                "green": self.save,
                "red": self.cancel,
                "yellow": self.revert,
                "save": self.save,
                "cancel": self.cancel,
                "ok": self.keyOk,
            }, -2)

    def createConfigList(self):
        self.get_media = getConfigListEntry(_("Choose media file"), config.autoshutdown.media_file)
        self.list = []
        self.list.append(getConfigListEntry('\c00289496' + _("*** Configuration for automatic power off in standby ***"), config.autoshutdown.fake_entry))
        self.list.append(getConfigListEntry(_("Enable automatic power off in standby:"), config.autoshutdown.autostart))
        if config.autoshutdown.autostart.value == True:
            self.list.append(getConfigListEntry(_("Time in standby for power off (min):"), config.autoshutdown.time))
            self.list.append(getConfigListEntry(_("Disable power off for given interval:"), config.autoshutdown.exclude_time_off))
            if config.autoshutdown.exclude_time_off.value:
                self.list.append(getConfigListEntry(_("Begin of excluded interval (hh:mm):"), config.autoshutdown.exclude_time_off_begin))
                self.list.append(getConfigListEntry(_("End of excluded interval (hh:mm):"), config.autoshutdown.exclude_time_off_end))
        self.list.append(getConfigListEntry(""))
        self.list.append(getConfigListEntry('\c00289496' + _("*** Configuration for inactivity actions ***")))
        self.list.append(getConfigListEntry(_("Enable action after inactivity:"), config.autoshutdown.enableinactivity))
        if config.autoshutdown.enableinactivity.value == True:
            self.list.append(getConfigListEntry(_("Time for inactivity (min):"), config.autoshutdown.inactivetime))
            self.list.append(getConfigListEntry(_("Action for inactivity:"), config.autoshutdown.inactivityaction))
            self.list.append(getConfigListEntry(_("Disable inactivity action at timeshift:"), config.autoshutdown.disable_at_ts))
            self.list.append(getConfigListEntry(_("Show message before inactivity action:"), config.autoshutdown.inactivitymessage))
            if config.autoshutdown.inactivitymessage.value == True:
                self.list.append(getConfigListEntry(_("Message timeout (sec):"), config.autoshutdown.messagetimeout))
                self.list.append(getConfigListEntry(_("Play media file before inactivity action:"), config.autoshutdown.play_media))
                if config.autoshutdown.play_media.value:
                    self.list.append(self.get_media)
            self.list.append(getConfigListEntry(_("Disable inactivity action for given interval:"), config.autoshutdown.exclude_time_in))
            if config.autoshutdown.exclude_time_in.value:
                self.list.append(getConfigListEntry(_("Begin of excluded interval (hh:mm):"), config.autoshutdown.exclude_time_in_begin))
                self.list.append(getConfigListEntry(_("End of excluded interval (hh:mm):"), config.autoshutdown.exclude_time_in_end))
        self.list.append(getConfigListEntry(""))
        self.list.append(getConfigListEntry('\c00289496' + _("*** Common configuration ***")))
        if (config.autoshutdown.enableinactivity.value and config.autoshutdown.inactivityaction.value == "deepstandby") or config.autoshutdown.autostart.value:
            self.list.append(getConfigListEntry(_("Disable power off in EPGRefresh interval:"), config.autoshutdown.epgrefresh))
            self.list.append(getConfigListEntry(_("Disable power off until a hard disk is active:"), config.autoshutdown.disable_hdd))
            self.list.append(getConfigListEntry(_("Disable power off until a given device is pingable:"), config.autoshutdown.disable_net_device))
            if config.autoshutdown.disable_net_device.value:
                self.list.append(getConfigListEntry(_("IP address of network device:"), config.autoshutdown.net_device))
        self.list.append(getConfigListEntry(_("Show in Extensions/Plugins:"), config.autoshutdown.plugin))

    def changedEntry(self):
        shutdownactions.stopKeyTimer()
        self.createConfigList()
        cur = self["config"].getCurrent()
        self["config"].setList(self.list)
        try:
            if cur and cur is not None:
                self["config"].updateConfigListView(cur)
        except Exception:
            pass
        shutdownactions.startKeyTimer()

    def setWindowTitle(self):
        self.setTitle(_("AutoShutDown Setup"))

    def keyOk(self):
        if self["config"].getCurrent() == self.get_media:
            start_dir = "/media/"
            self.session.openWithCallback(self.selectedMediaFile,AutoShutDownFile, start_dir)

    def selectedMediaFile(self, res):
        if res is not None:
            config.autoshutdown.media_file.value = res
            config.autoshutdown.media_file.save()
            self.changedEntry()

    def save(self, ret = True):
        shutdownactions.stopKeyTimer()
        for x in self["config"].list:
            if len(x) >= 2:
                x[1].save()
        configfile.save()
        self.changedEntry()
        shutdownactions.startKeyTimer()
        if ret:
            self.close()

    def cancel(self):
        try:
            if self["config"].isChanged():
              self.session.openWithCallback(self.cancelConfirm, MessageBox, _("Really close without saving settings?"), MessageBox.TYPE_YESNO, default = False)
            else:
                for x in self["config"].list:
                    if len(x) >= 2:
                        x[1].cancel()
        except Exception:
            pass
        self.close(False,self.session)

    def cancelConfirm(self, result):
        if result is None or result is False:
            print("[AutoShutDown] Cancel not confirmed.")
        else:
            print("[AutoShutDown] Cancel confirmed. Configchanges will be lost.")
            for x in self["config"].list:
                if len(x) >= 2:
                    x[1].cancel()
            self.close(False,self.session)

    def revert(self):
        self.session.openWithCallback(self.keyYellowConfirm, MessageBox, _("Reset AutoShutDown settings to defaults?"), MessageBox.TYPE_YESNO, timeout = 20, default = False)

    def keyYellowConfirm(self, confirmed):
        if not confirmed:
            print("[AutoShutDown] Reset to defaults not confirmed.")
        else:
            print("[AutoShutDown] Setting Configuration to defaults.")
            config.autoshutdown.time.setValue(120)
            config.autoshutdown.autostart.setValue(0)
            config.autoshutdown.enableinactivity.setValue(0)
            config.autoshutdown.inactivetime.setValue(15)
            config.autoshutdown.inactivityaction.setValue("standby")
            config.autoshutdown.epgrefresh.setValue(1)
            config.autoshutdown.plugin.setValue(0)
            config.autoshutdown.inactivitymessage.setValue(1)
            config.autoshutdown.messagetimeout.setValue(5)
            config.autoshutdown.play_media.setValue(0)
            config.autoshutdown.media_file.setValue("")
            config.autoshutdown.disable_at_ts.setValue(0)
            config.autoshutdown.disable_net_device.setValue(0)
            config.autoshutdown.net_device.setValue([0,0,0,0])
            config.autoshutdown.exclude_time_in.setValue(0)
            config.autoshutdown.exclude_time_in_begin.setValue([20, 0])
            config.autoshutdown.exclude_time_in_end.setValue([0, 0])
            config.autoshutdown.exclude_time_off.setValue(0)
            config.autoshutdown.exclude_time_off_begin.setValue([20, 0])
            config.autoshutdown.exclude_time_off_end.setValue([0, 0])
            self.save(False)

class AutoShutDownFile(Screen):
    skin = """
        <screen name="AutoShutDownFile" position="center,center" size="650,450" title="Select a media file for AutoShutDown">
            <widget name="media" position="10,10" size="540,30" valign="top" font="Regular;22" />
            <widget name="filelist" position="10,45" zPosition="1" size="540,350" scrollbarMode="showOnDemand"/>
            <widget render="Label" source="key_red" position="40,422" size="100,20" valign="center" halign="left" zPosition="2" font="Regular;18" foregroundColor="white" />
            <widget render="Label" source="key_green" position="180,422" size="70,20" valign="center" halign="left" zPosition="2" font="Regular;18" foregroundColor="white" />
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/SystemPlugins/AutoShutDown/pic/button_red.png" zPosition="2" position="10,420" size="25,25" alphatest="on" />
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/SystemPlugins/AutoShutDown/pic/button_green.png" zPosition="2" position="150,420" size="25,25" alphatest="on" />
        </screen>
        """

    def __init__(self, session, initDir, plugin_path = None):
        Screen.__init__(self, session)
        #self.skin_path = plugin_path
        self["filelist"] = FileList(initDir, inhibitMounts = False, inhibitDirs = False, showMountpoints = False)
        self["media"] = Label()
        self["actions"] = ActionMap(["WizardActions", "DirectionActions", "ColorActions", "EPGSelectActions"],
        {
            "back": self.cancel,
            "left": self.left,
            "right": self.right,
            "up": self.up,
            "down": self.down,
            "ok": self.ok,
            "green": self.green,
            "red": self.cancel
            
        }, -1)
        self.title=_("Select a media file for AutoShutDown")
        try:
            self["title"]=StaticText(self.title)
        except:
            print('self["title"] was not found in skin'    )
        self["key_red"] = StaticText(_("Cancel"))
        self["key_green"] = StaticText(_("OK"))

    def cancel(self):
        self.close(None)

    def green(self):
        if self["filelist"].getSelection()[1] == True:
            self["media"].setText(_("Invalid Choice"))
        else:
            directory = self["filelist"].getCurrentDirectory()
            if (directory.endswith("/")):
                self.fullpath = self["filelist"].getCurrentDirectory() + self["filelist"].getFilename()
            else:
                self.fullpath = self["filelist"].getCurrentDirectory() + "/" + self["filelist"].getFilename()
            self.close(self.fullpath)

    def up(self):
        self["filelist"].up()
        self.updateFile()

    def down(self):
        self["filelist"].down()
        self.updateFile()

    def left(self):
        self["filelist"].pageUp()
        self.updateFile()

    def right(self):
        self["filelist"].pageDown()
        self.updateFile()

    def ok(self):
        if self["filelist"].canDescent():
            self["filelist"].descent()
            self.updateFile()

    def updateFile(self):
        currFolder = self["filelist"].getSelection()[0]
        if self["filelist"].getFilename() is not None:
            directory = self["filelist"].getCurrentDirectory()
            if (directory.endswith("/")):
                self.fullpath = self["filelist"].getCurrentDirectory() + self["filelist"].getFilename()
            else:
                self.fullpath = self["filelist"].getCurrentDirectory() + "/" + self["filelist"].getFilename()
            
            self["media"].setText(self["filelist"].getFilename())
        else:
            currFolder = self["filelist"].getSelection()[0]
            if currFolder is not None:
                self["media"].setText(currFolder)
            else:
                self["media"].setText(_("Invalid Choice"))
