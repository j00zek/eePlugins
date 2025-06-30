# -*- coding: utf-8 -*-
#    Coded by j00zek (c)2015
#
from __future__ import absolute_import #zmiana strategii ladowanie modulow w py2 z relative na absolute jak w py3
from Plugins.Extensions.AdvancedFreePlayer.__init__ import *
from Plugins.Extensions.AdvancedFreePlayer.__init__ import translate as _

from Components.ActionMap import ActionMap
from Components.config import *
from Components.ConfigList import ConfigList, ConfigListScreen
from Components.Console import Console
from Components.Label import Label
from enigma import eEnv, eTimer
from os import path, remove as os_remove, fsync as os_fsync, rename as os_rename, walk as os_walk, listdir, mkdir as os_mkdir, chmod as os_chmod
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.VirtualKeyBoard import VirtualKeyBoard
from Tools.Directories import fileExists, resolveFilename, pathExists, SCOPE_PLUGINS, SCOPE_SKIN_IMAGE


##############################################################
class AdvancedFreePlayerConfig(Screen, ConfigListScreen):
    skin = """
    <screen name="AdvancedFreePlayerConfig" position="center,center" size="640,500" title="AdvancedFreePlayer Config" flags="wfNoBorder" backgroundColor="#20606060" >
            <widget name="config" position="10,10" size="620,450" zPosition="1" transparent="0" scrollbarMode="showOnDemand" />
            <widget name="key_red" position="0,465" zPosition="2" size="200,35" valign="center" halign="center" font="Regular;22" transparent="1" foregroundColor="red" />
            <widget name="key_green" position="220,465" zPosition="2" size="200,35" valign="center" halign="center" font="Regular;22" transparent="1" foregroundColor="green" />
            <widget name="key_blue" position="440,465" zPosition="2" size="200,35" valign="center" halign="center" font="Regular;22" transparent="1" foregroundColor="#202673ec" />
    </screen>"""
    
    def __init__(self, session):
        Screen.__init__(self, session)
        self.session = session
        ConfigListScreen.__init__(self, [],  self.session)
        self["actions"] = ActionMap(["SetupActions", "ColorActions"],
            {
                "cancel": self.keyCancel,
                "red": self.keyCancel,
                "green": self.keySave,
                "ok": self.keyOK,
                "blue": self.keyBlue,
            }, -2)

        self["key_green"] = Label(_("Save"))
        self["key_red"] = Label(_("Cancel"))
        self["key_blue"] = Label() # _("Update"))

        self.list = [ ]
        myConfig.separator = NoSave(ConfigNothing())
        self.list.append(getConfigListEntry('\c00289496' + _("*** Session settings ***")))
        self.list.append(getConfigListEntry(_("Show only movies containing (OK):"), myConfig.FileNameFilter))
        self.list.append(getConfigListEntry(_("Rename (OK):"), myConfig.FileListSelectedItem))
        self.list.append(getConfigListEntry(""))
        self.list.append(getConfigListEntry('\c00289496' + _("*** Standard settings ***")))
        self.list.append(getConfigListEntry(_("Show Movie name instead of Filename:"), myConfig.NamesNOfiles))
        #self.list.append(getConfigListEntry(_("FileList font size (20-32):"), myConfig.FileListFontSize))
        self.list.append(getConfigListEntry(_("Show subtitles files on the list:"), myConfig.TextFilesOnFileList))
        self.list.append(getConfigListEntry(_("Show Music files on the list:"), myConfig.ShowMusicFiles))
        #self.list.append(getConfigListEntry(_("Show Picture files on the list:"), myConfig.ShowPicturesFiles))
        self.list.append(getConfigListEntry(_("Initial files sorting:"), myConfig.FileListSort))
        self.list.append(getConfigListEntry(_("Initial directories sorting:"), myConfig.DirListSort))
        
        self.list.append(getConfigListEntry(_("Stop playing entering AdvancedFreePlayer:"), myConfig.StopService))
        self.list.append(getConfigListEntry(_("Initial movies folder:"), myConfig.FileListLastFolder))
        self.list.append(getConfigListEntry(_("Remember last used folder:"), myConfig.StoreLastFolder))
        self.list.append(getConfigListEntry(_("Key OK behavior:"), myConfig.KeyOK))
        self.list.append(getConfigListEntry(_("Ask for file removal when % played (0=off):"), myConfig.DeleteWhenPercentagePlayed))
        self.list.append(getConfigListEntry(_("Always ask for file removal:"), myConfig.DeleteFileQuestion))
        self.list.append(getConfigListEntry(_("Move to trash folder instead delete:"), myConfig.MoveToTrash ))
        self.list.append(getConfigListEntry(_("Trash folder:"), myConfig.TrashFolder ))
        
        self.list.append(getConfigListEntry(""))
        self.list.append(getConfigListEntry('\c00289496' + _("*** Infobar settings ***")))
        self.list.append(getConfigListEntry(_("Time displaying infobar:"), myConfig.InfobarTime))
        self.list.append(getConfigListEntry(_("Display infobar on pause:"), myConfig.InfobarOnPause))
        
        self.list.append(getConfigListEntry(""))
        self.list.append(getConfigListEntry('\c00289496' + _("*** Subtitles settings ***")))
        self.list.append(getConfigListEntry(_("SRT subtitles displayed by:"), myConfig.SRTplayer))
        if getPlatform() in ['sh4','ServiceApp']:
            self.list.append(getConfigListEntry(_("MultiFramework selection:"), myConfig.MultiFramework))
        
        self.list.append(getConfigListEntry(""))
        self.list.append(getConfigListEntry('\c00289496' + _("*** Cover & Descriptions settings ***")))
        self.list.append(getConfigListEntry(_("Download from WEB:"), myConfig.AutoDownloadCoversDescriptions))
        self.list.append(getConfigListEntry(_("Download to movie folder:"), myConfig.PermanentCoversDescriptons))
        self.list.append(getConfigListEntry(_("Search TMDB for the language:"), myConfig.coverfind_language))
        self.list.append(getConfigListEntry(_("Cover size:"), myConfig.coverfind_themoviedb_coversize))
        self.list.append(getConfigListEntry(_("Directories info and cover:"), myConfig.DirectoryCoversDescriptons))
        
        self["config"].list = self.list        
        self.onLayoutFinish.append(self.layoutFinished)

    def layoutFinished(self):
        self.setTitle(_("%s %s Config") %(PluginName,PluginInfo))
        
    def keyBlue(self):
        return

    def OkbuttonTextChanged(self, ret ): #return from virtual keayboard
        if ret:
            curIndex = self["config"].getCurrentIndex()
            self["config"].list[curIndex][1].value = ret.strip()

    def OkbuttonConfirmChange(self, ret ): #return from virtual keayboard
        def changeConfirmed(ret2 = False):
            if ret2:
                curIndex = self["config"].getCurrentIndex()
                self["config"].list[curIndex][1].value = ret.strip()
        if ret and ret != self.currItemValue:
            self.session.openWithCallback(changeConfirmed, MessageBox, _("Changing '%s' to '%s'\nDo you confirm it?") % (self.currItemValue , ret), MessageBox.TYPE_YESNO, default = False)

    def keyOK(self):
        try:
            curIndex = self["config"].getCurrentIndex()
            selectedItem = self["config"].list[curIndex]
            if len(selectedItem) == 2:
                currItem = selectedItem[1]
                currInfo = selectedItem[0]
                self.currItemValue = currItem.value
                if currItem == myConfig.FileNameFilter:
                    self.session.openWithCallback(self.OkbuttonTextChanged, VirtualKeyBoard, title= _("Movie name must contain..."), text = currItem.value)
                elif currItem == myConfig.FileListSelectedItem:
                    self.session.openWithCallback(self.OkbuttonConfirmChange, VirtualKeyBoard, title= _("New filename..."), text = currItem.value)
        except Exception as e:
            pass

    def keySave(self):
        for x in self["config"].list:
            if len(x) == 2:
                x[1].save()
        configfile.save()
        self.close()

    def keyCancel(self):
        for x in self["config"].list:
            if len(x) == 2:
                x[1].cancel()
        self.close()
        
from enigma import eConsoleAppContainer
from Components.ScrollLabel import ScrollLabel
def substring_2_translate(text):
    to_translate = text.split('_(', 2)
    text = to_translate[1]
    to_translate = text.split(')', 2)
    text = to_translate[0]
    return text
    
def __(txt):
    if txt.find('_(') == -1:
        txt = _(txt)
    else:
        index = 0
        while txt.find('_(') != -1:
            tmptxt = substring_2_translate(txt)
            translated_tmptxt = _(tmptxt)
            txt = txt.replace('_(' + tmptxt + ')', translated_tmptxt)
            index += 1
            if index == 10:
                break

    return txt
########################################################################################################################################
class AdvancedFreePlayerConsole(Screen):
    #TODO move this to skin.xml
    skin = """
        <screen position="center,center" size="550,400" title="Command execution..." >
            <widget name="text" position="0,0" size="550,400" font="Console;14" />
        </screen>"""
        
    def __init__(self, session, title = "AdvancedFreePlayerConsole", cmdlist = None, finishedCallback = None, closeOnSuccess = False):
        Screen.__init__(self, session)

        self.finishedCallback = finishedCallback
        self.closeOnSuccess = closeOnSuccess
        self.errorOcurred = False

        self["text"] = ScrollLabel("")
        self["actions"] = ActionMap(["WizardActions", "DirectionActions"], 
        {
            "ok": self.cancel,
            "back": self.cancel,
            "up": self["text"].pageUp,
            "down": self["text"].pageDown
        }, -1)
        
        self.cmdlist = cmdlist
        self.newtitle = title
        
        self.onShown.append(self.updateTitle)
        
        self.container = eConsoleAppContainer()
        self.run = 0
        self.container.appClosed.append(self.runFinished)
        self.container.dataAvail.append(self.dataAvail)
        self.onLayoutFinish.append(self.startRun) # dont start before gui is finished

    def updateTitle(self):
        self.setTitle(self.newtitle)

    def startRun(self):
        self["text"].setText("" + "\n\n")
        print("TranslatedConsole: executing in run", self.run, " the command:", self.cmdlist[self.run])
        if self.container.execute(self.cmdlist[self.run]): #start of container application failed...
            self.runFinished(-1) # so we must call runFinished manual

    def runFinished(self, retval):
        if retval:
            self.errorOcurred = True
        self.run += 1
        if self.run != len(self.cmdlist):
            if self.container.execute(self.cmdlist[self.run]): #start of container application failed...
                self.runFinished(-1) # so we must call runFinished manual
        else:
            #lastpage = self["text"].isAtLastPage()
            #str = self["text"].getText()
            #str += _("\nUse up/down arrows to scroll text. OK closes window");
            #self["text"].setText(str)
            #if lastpage:
            self["text"].lastPage()
            if self.finishedCallback is not None:
                self.finishedCallback()
            if not self.errorOcurred and self.closeOnSuccess:
                self.cancel()

    def cancel(self):
        if self.run == len(self.cmdlist):
            self.close()
            self.container.appClosed.remove(self.runFinished)
            self.container.dataAvail.remove(self.dataAvail)

    def dataAvail(self, str):
        #lastpage = self["text"].isAtLastPage()
        self["text"].setText(self["text"].getText() + __(str))
        #if lastpage:
        self["text"].lastPage()
