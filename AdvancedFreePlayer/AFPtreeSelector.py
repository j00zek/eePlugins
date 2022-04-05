# -*- coding: utf-8 -*-
from __future__ import absolute_import #zmiana strategii ladowanie modulow w py2 z relative na absolute jak w py3
from Plugins.Extensions.AdvancedFreePlayer.__init__ import *
from Plugins.Extensions.AdvancedFreePlayer.__init__ import translate as _
from Plugins.Extensions.AdvancedFreePlayer.Cleaningfilenames import *
from Plugins.Extensions.AdvancedFreePlayer.cueSheetHelper import getCut, clearLastPosition
from Plugins.Extensions.AdvancedFreePlayer.j00zekFileList import FileList, EXTENSIONS

from Screens.Screen import Screen

from Screens.ChoiceBox import ChoiceBox
from Screens.InputBox import InputBox
from Screens.MessageBox import MessageBox

from Components.ActionMap import ActionMap
try:
    from Components.j00zekAccellPixmap import j00zekAccellPixmap
except Exception:
    from j00zekAccellPixmap import j00zekAccellPixmap
from Components.Label import Label
#from Components.Pixmap import Pixmap
from Components.Sources.StaticText import StaticText
from Components.config import *
#from Tools.LoadPixmap import LoadPixmap
#from os import path, remove, listdir, symlink, system, access, W_OK,
import re

from enigma import eTimer

from skin import parseColor

from time import *
import json
import datetime
import os
import time

class AdvancedFreePlayerStarter(Screen):
    def __init__(self, session, openmovie, movieTitle):
        printDEBUG("AdvancedFreePlayerStarter >>>")
        self.sortType = 'name'
        self.openmovie = openmovie
        self.movieTitle = movieTitle
        self.opensubtitle = ''
        self.URLlinkName = ''
        self.rootID = myConfig.MultiFramework.value
        self.LastPlayedService = None
  
        if os.path.exists(ExtPluginsPath + '/DMnapi/DMnapi.pyo') or os.path.exists(ExtPluginsPath +'/DMnapi/DMnapi.pyc') or os.path.exists(ExtPluginsPath +'/DMnapi/DMnapi.py'):
            self.DmnapiInstalled = True
        else:
            self.DmnapiInstalled = False
            
        #self.skin  = LoadSkin("AdvancedFreePlayerStart")
        
        Screen.__init__(self, session)
        self.onShow.append(self.PlayMovie)

    def PlayMovie(self):
        self.onShow.remove(self.PlayMovie)
        if not self.openmovie == "":
            if not os.path.exists(self.openmovie + '.cuts'):
                self.SelectFramework()
            elif os.path.getsize(self.openmovie + '.cuts') == 0:
                self.SelectFramework()
            else:
                self.session.openWithCallback(self.ClearCuts, MessageBox, _("Do you want to resume this playback?"), timeout=10, default=True)

    def ClearCuts(self, ret):
        if not ret:
            clearLastPosition(self.openmovie)
        self.SelectFramework()

    def SelectFramework(self):
        if myConfig.MultiFramework.value == "select":
            from Screens.ChoiceBox import ChoiceBox
            self.session.openWithCallback(self.SelectedFramework, ChoiceBox, title = _("Select Multiframework"), list = getChoicesList())
        else:
            if self.openmovie.endswith('.ts'):
                self.rootID = '1'
            else:
                self.rootID = myConfig.MultiFramework.value
            self.StartPlayer()

    def SelectedFramework(self, ret):
        if ret:
            self.rootID = ret[1]
            printDEBUG("Selected framework: " + ret[1])
        self.StartPlayer()
      
    def StartPlayer(self):
        self.lastOPLIsetting = None
        
        if not os.path.exists(self.opensubtitle) and not self.opensubtitle.startswith("http://"):
            self.opensubtitle = ""
        if os.path.exists(self.openmovie) or self.openmovie.startswith("http://"):
            if myConfig.SRTplayer.value =="system":
                try: 
                    self.lastOPLIsetting = config.subtitles.pango_autoturnon.value
                    config.subtitles.pango_autoturnon.value = True
                except:
                    pass
                self.session.openWithCallback(self.ExitPlayer,AdvancedFreePlayer,self.openmovie,'',self.rootID,self.LastPlayedService,self.URLlinkName,self.movieTitle)
                return
            else:
                try: 
                    self.lastOPLIsetting = config.subtitles.pango_autoturnon.value
                    config.subtitles.pango_autoturnon.value = False
                    printDEBUG("OpenPLI subtitles disabled")
                except:
                    printDEBUG("pango_autoturnon non existent, is it VTI?")

                self.session.openWithCallback(self.ExitPlayer,AdvancedFreePlayer,self.openmovie,self.opensubtitle,self.rootID,self.LastPlayedService,self.URLlinkName,self.movieTitle)
                return
        else:
            printDEBUG("StartPlayer>>> File %s does not exist :(" % self.openmovie)
     
    def ExitPlayer(self):
        if self.lastOPLIsetting is not None:
            config.subtitles.pango_autoturnon.value = self.lastOPLIsetting
        myConfig.PlayerOn.value = False
        self.close()
##################################################################### CLASS END #####################################################################

class AdvancedFreePlayerStart(Screen):
    def __init__(self, session):
        #printDEBUG("AdvancedFreePlayerStart >>>")
        self.openmovie = ''
        self.opensubtitle = ''
        self.URLlinkName = ''
        self.movietxt = _('Movie: ')
        self.subtitletxt = _('Subtitle: ')
        self.rootID = myConfig.MultiFramework.value
        self.LastPlayedService = None
        self.LastFolderSelected = None
        self.movieTitle = ''
        self.gettingDataFromWEB = False
        self.ShowDelay = 100
  
        self.skin  = LoadSkin("AdvancedFreePlayerStart")
        
        Screen.__init__(self, session)
        self["info"] = Label()
        self["myPath"] = Label(myConfig.FileListLastFolder.value)
        self["myFilter"] = Label(_('Fitering disabled'))
        
        self["filemovie"] = Label(self.movietxt)
        self["filesubtitle"] = Label(self.subtitletxt)
        if myConfig.KeyOK.value == "playmovie":
            self["filemovie"].hide()
            self["filesubtitle"].hide()
            
        self["key_red"] = StaticText()
        self["key_green"] = StaticText()
        self["key_blue"] = StaticText()
        self["key_yellow"] = StaticText(_("Config"))
        
        from Plugins.Extensions.AdvancedFreePlayer.PlayWithdmnapi import KeyMapInfo #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
        self["Description"] = Label(KeyMapInfo)
        self["Cover"] = j00zekAccellPixmap()
        
        if os.path.exists(ExtPluginsPath + '/DMnapi/DMnapi.pyo') or os.path.exists(ExtPluginsPath +'/DMnapi/DMnapi.pyc') or os.path.exists(ExtPluginsPath +'/DMnapi/DMnapi.py'):
            self.DmnapiInstalled = True
            self["key_green"].setText(_("DMnapi"))
        else:
            self.DmnapiInstalled = False
            self["key_green"].setText(_("Install DMnapi"))
            
        self.sortType = myConfig.FileListSort.value
        if self.sortType == 'dateasc':    self["key_blue"].setText(_("Sorted by date ascending"))
        elif self.sortType == 'datedesc': self["key_blue"].setText(_("Sorted by date descending"))
        else:                             self["key_blue"].setText(_("Sorted by name"))
        self["info"].setText(PluginName + ' ' + PluginInfo)
        
         
        self.filelist = FileList(myConfig.FileListLastFolder.value, matchingPattern = self.buildmatchingPattern(), sortType=self.sortType)
            
        self["filelist"] = self.filelist
        self["actions"] = ActionMap(["AdvancedFreePlayerSelector"],
            {
                "selectFile": self.selectFile,
                "ExitPlayer": self.ExitPlayer,
                "lineUp": self.lineUp,
                "lineDown": self.lineDown,
                "pageUp": self.pageUp,
                "pageDown": self.pageDown,
                "PlayMovie": self.PlayMovie,
                "runDMnapi": self.runDMnapi,
                "runConfig": self.runConfig,
                "setSort": self.setSort,
                "playORdelete": self.playORdelete,
            },-2)
        self.setTitle(PluginName + ' ' + PluginInfo)
        if myConfig.StopService.value == True:
            self.LastPlayedService = self.session.nav.getCurrentlyPlayingServiceReference()
            self.session.nav.stopService()
        
        self.onLayoutFinish.append(self.__onLayoutFinish)
        self.onShown.append(self.__onShown) 
        self.GetCoverTimer = eTimer()
        #TZ LOCAL TIME offset
        now_timestamp = time.time()
        #self.TZoffset = datetime.datetime.fromtimestamp(now_timestamp) - datetime.datetime.utcfromtimestamp(now_timestamp)
        self.TZoffset = divmod((datetime.datetime.fromtimestamp(now_timestamp) - datetime.datetime.utcfromtimestamp(now_timestamp)).seconds,3600)[0]

    def __onLayoutFinish(self):
        self.GetCoverTimer.callback.append(self.__refreshFilelist)
        self.GetCoverTimer.start(50, True)

    def __onShown(self):
        printDEBUG("__onShown()")
        self.session.summary.LCD_showLogo()
    
    def buildmatchingPattern(self):
        matchingPattern = "(?i)^.*"
        if myConfig.FileNameFilter.value != '':
            matchingPattern += myConfig.FileNameFilter.value + '.*'
        matchingPattern += "\.("
        tmpPart = ''
        for myExtension in EXTENSIONS:
            print(myExtension, EXTENSIONS[myExtension])
            if EXTENSIONS[myExtension] == "movie":
                tmpPart += "|" + myExtension
            elif EXTENSIONS[myExtension] == "movieurl":
                tmpPart += "|" + myExtension
            elif myConfig.ShowMusicFiles.value == True and  EXTENSIONS[myExtension] == "music":
                tmpPart += "|" + myExtension
            elif myConfig.ShowPicturesFiles.value == True and  EXTENSIONS[myExtension] == "picture":
                tmpPart += "|" + myExtension
            elif myConfig.TextFilesOnFileList.value == True and  EXTENSIONS[myExtension] == "text":
                tmpPart += "|" + myExtension
        matchingPattern += tmpPart[1:] + ")(?!\.(cuts|ap$|meta$|sc$|wget$))"
        printDEBUG("matchingPattern=%s" % matchingPattern)
        self.currentFileNameFilter = myConfig.FileNameFilter.value
        return matchingPattern
    
    def __refreshFilelist(self):
        self.GetCoverTimer.callback.remove(self.__refreshFilelist)
        self.GetCoverTimer.callback.append(self.GetCoverTimerCB)
        self["filelist"].changeDir(myConfig.FileListLastFolder.value)
        self["filelist"].refresh()
    
    def buttonsNames(self):
        selection = self["filelist"].getSelection()
        if selection is not None and selection[1] == True and self["filelist"].getSelectedIndex() == 0:
            self["key_red"].setText("")
        elif self.openmovie == '':
            self["key_red"].setText(_("Delete"))
        elif selection is not None and selection[0].endswith('.url'): # selected different file than chosen movie
            self["key_red"].setText(_("Play"))
        elif selection is not None and selection[1] == True and self["filelist"].getSelectedIndex() > 0:
            self["key_red"].setText(_("Delete"))
        elif selection is not None and not selection[0] in self.openmovie : # selected different file than chosen movie
            self["key_red"].setText(_("Delete"))
        else:
            self["key_red"].setText(_("Play"))
      
    def pageUp(self):
        self.GetCoverTimer.stop()
        if self["filelist"].getSelectedIndex() == 0:
            self["filelist"].moveToIndex(len(self["filelist"].getFileList())-1)
        else:
            self["filelist"].pageUp()
        self.buttonsNames()
        printDEBUG("pageUp SelectedIndex()='%s'" % (self["filelist"].getSelectedIndex()))
        self.GetCoverTimer.start(self.ShowDelay,False)


    def pageDown(self):
        self.GetCoverTimer.stop()
        if self["filelist"].getSelectedIndex() == (len(self["filelist"].getFileList())-1):
            self["filelist"].moveToIndex(0)
        else:
            self["filelist"].pageDown()
        self.buttonsNames()
        printDEBUG("pageDown SelectedIndex()='%s'" % (self["filelist"].getSelectedIndex()))
        self.GetCoverTimer.start(self.ShowDelay,False)

    def lineUp(self):
        self.GetCoverTimer.stop()
        if self["filelist"].getSelectedIndex() == 0:
            self["filelist"].moveToIndex(len(self["filelist"].getFileList())-1)
        else:
            self["filelist"].up()
        self.buttonsNames()
        printDEBUG("lineUp SelectedIndex()='%s'" % (self["filelist"].getSelectedIndex()))
        self.GetCoverTimer.start(self.ShowDelay,False)

    def lineDown(self):
        self.GetCoverTimer.stop()
        if self["filelist"].getSelectedIndex() == (len(self["filelist"].getFileList())-1):
            self["filelist"].moveToIndex(0)
        else:
            self["filelist"].down()
        self.buttonsNames()
        printDEBUG("lineDown SelectedIndex()='%s'" % (self["filelist"].getSelectedIndex()))
        self.GetCoverTimer.start(self.ShowDelay,False)

    def playORdelete(self):
        if self["key_red"].getText() == _("Play"):
            self.PlayMovie()
            return
        def deleteRet(ret):
            selection = self["filelist"].getSelection()
            printDEBUG("playORdelete>deleteRet ret=%s" % str(ret))
            if ret:
                self.setCover('hideCover')
                self.setDescription('')
                selection = self["filelist"].getSelection()
                ClearMemory()
                if selection[1] == True: # isDir
                    printDEBUG('Deleting folder %s' % selection[0])
                    os.system('rm -rf "%s"' % selection[0])
                else:
                    if selection[0][-4:].lower() in ('.srt','.txt','.url'):
                        if myConfig.MoveToTrash.value == True:
                            printDEBUG('Moving file "%s/%s" to %s/' % (self.filelist.getCurrentDirectory(),selection[0], myConfig.TrashFolder.value))
                            os.system('mkdir -p "%s";mv -f "%s/%s" %s/' % (myConfig.TrashFolder.value, self.filelist.getCurrentDirectory(),selection[0], myConfig.TrashFolder.value))
                        else:
                            printDEBUG('Deleting file "%s/%s"' % (self.filelist.getCurrentDirectory(),selection[0]))
                            os.system('rm -rf "%s/%s"' % (self.filelist.getCurrentDirectory(),selection[0]))
                    else:
                        if myConfig.MoveToTrash.value == True:
                            printDEBUG('Moving files "%s/%s"* to %s/' % (self.filelist.getCurrentDirectory(),selection[0][:-4], myConfig.TrashFolder.value))
                            os.system('mkdir -p "%s";mv -f "%s/%s"* %s/' % (myConfig.TrashFolder.value, self.filelist.getCurrentDirectory(),selection[0][:-4], myConfig.TrashFolder.value))
                        else:
                            printDEBUG('Deleting files "%s/%s"*' % (self.filelist.getCurrentDirectory(),selection[0][:-4]))
                            os.system('rm -rf "%s/%s"*' % (self.filelist.getCurrentDirectory(),selection[0][:-4]))
                if self["filelist"].getSelectedIndex() > 0:
                    self["filelist"].up()
            self.GetCoverTimer.stop()
            self["filelist"].refresh()
            self.buttonsNames()
            self.GetCoverTimer.start(self.ShowDelay,False)
            return
        
        selection = self["filelist"].getSelection()
        if myConfig.MoveToTrash.value == True:
            if selection[1] == True: # isDir
                self.session.openWithCallback(deleteRet, MessageBox, _("Move folder '%s' to trash?") % selection[0], timeout=10, default=False)
            elif selection[0][-4:].lower() in ('.srt','.txt'):
                self.session.openWithCallback(deleteRet, MessageBox, _("Move subtitles for movie '%s' to trash?") % selection[0][:-4], timeout=10, default=False)
            elif selection[0][-4:].lower() in ('.url'):
                self.session.openWithCallback(deleteRet, MessageBox, _("Move link for movie '%s' to trash?") % selection[0][:-4], timeout=10, default=False)
            else:
                self.session.openWithCallback(deleteRet, MessageBox, _("Move movie '%s' to trash?") % selection[0][:-4], timeout=10, default=False)
        else:
            if selection[1] == True: # isDir
                self.session.openWithCallback(deleteRet, MessageBox, _("Delete '%s' folder?") % selection[0], timeout=10, default=False)
            elif selection[0][-4:].lower() in ('.srt','.txt'):
                self.session.openWithCallback(deleteRet, MessageBox, _("Delete subtitles for '%s' movie?") % selection[0][:-4], timeout=10, default=False)
            elif selection[0][-4:].lower() in ('.url'):
                self.session.openWithCallback(deleteRet, MessageBox, _("Delete link for '%s' movie?") % selection[0][:-4], timeout=10, default=False)
            else:
                self.session.openWithCallback(deleteRet, MessageBox, _("Delete '%s' movie?") % selection[0][:-4], timeout=10, default=False)
      
    def PlayMovie(self):
        printDEBUG('PlayMovie >>>')
        if self.openmovie != "":
            printDEBUG(self["myPath"].getText())
            if myConfig.StoreLastFolder.value == True:
                myConfig.FileListLastFolder.value =  self["myPath"].getText()
                myConfig.FileListLastFolder.save()
            if self.URLlinkName == '':
                self.lastPosition, Length = getCut(self.openmovie + '.cuts') #returns in mins
            else:
                self.lastPosition, Length = getCut(self.URLlinkName + '.cuts') #returns in mins
            if self.lastPosition < 1:
                self.SelectFramework()
            else:
                self.session.openWithCallback(self.ClearCuts, MessageBox, _("Do you want to resume this playback?"), timeout=10, default=True)

    def ClearCuts(self, ret):
        printDEBUG("AFPtreeSelector:ClearCuts resume this playback to position %s ? '%s'" % (self.lastPosition, str(ret)))
        if not ret:
            clearLastPosition(self.openmovie + '.cuts')
            self.lastPosition = 0
        self.SelectFramework()

    def SelectFramework(self):
        printDEBUG('SelectFramework >>>')
        if myConfig.MultiFramework.value == "select":
            from Screens.ChoiceBox import ChoiceBox
            self.session.openWithCallback(self.SelectedFramework, ChoiceBox, title = _("Select Multiframework"), list = getChoicesList())
        else:
            if self.openmovie.endswith('.ts'):
                self.rootID = '1'
            elif self.openmovie.endswith('.flac') or self.openmovie.endswith('.fla'):
                self.rootID = '4099'
            else:
                self.rootID = myConfig.MultiFramework.value
            printDEBUG('Selected framework: %s' % self.rootID)
            self.StartPlayer()

    def SelectedFramework(self, ret):
        if ret:
            self.rootID = ret[1]
            printDEBUG("Selected framework: " + ret[1])
            self.StartPlayer()
      
    def StartPlayer(self):
        printDEBUG('StartPlayer >>>')
        lastOPLIsetting = None
        
        def EndPlayer():
            if lastOPLIsetting is not None:
                config.subtitles.pango_autoturnon.value = lastOPLIsetting
            
            if not os.path.exists(self.openmovie):
                self.openmovie = ''
                self.opensubtitle = ''
                self.setCover('hideCover')
                self.setDescription('')
                if self["filelist"].getSelectedIndex() > 0:
                    self["filelist"].up()
            
            self.GetCoverTimer.stop()
            self["filelist"].refresh()
            self.buttonsNames()
            self.GetCoverTimer.start(self.ShowDelay,False)

        if not os.path.exists(self.opensubtitle) and not self.opensubtitle.startswith("http://"):
            self.opensubtitle = ""
            
        if os.path.exists(self.openmovie) or self.openmovie.startswith("http://"):
            if myConfig.SRTplayer.value =="system":
                printDEBUG("PlayWithSystem title:'%s' filename:'%s'" %(self.movieTitle,self.openmovie))
                from Plugins.Extensions.AdvancedFreePlayer.PlayWithSystem import AdvancedFreePlayer
            else:
                try: 
                    lastOPLIsetting = config.subtitles.pango_autoturnon.value
                    config.subtitles.pango_autoturnon.value = False
                    printDEBUG("OpenPLI subtitles disabled")
                except:
                    printDEBUG("pango_autoturnon non existent, is it VTI?")
                if myConfig.SRTplayer.value =="plugin-SubsSupport":
                    printDEBUG("PlayWithsubsupport title:'%s' filename:'%s'" %(self.movieTitle,self.openmovie))
                    from Plugins.Extensions.AdvancedFreePlayer.PlayWithsubsupport import AdvancedFreePlayer
                else:
                    printDEBUG("PlayWithdmnapi title:'%s' filename:'%s'" %(self.movieTitle,self.openmovie))
                    from Plugins.Extensions.AdvancedFreePlayer.PlayWithdmnapi import AdvancedFreePlayer
            #initiate player
            self.session.openWithCallback(EndPlayer,AdvancedFreePlayer,self.openmovie,self.opensubtitle,
                                            self.rootID,self.LastPlayedService,self.URLlinkName,
                                            self.movieTitle, self.lastPosition * 90 * 1000 * 60)
            return
        else:
            printDEBUG("StartPlayer>>> File %s does not exist :(" % self.openmovie)

    def runConfigRet(self):
        doRefresh = False
        #obsluga zmiany filtra
        if self.currentFileNameFilter != myConfig.FileNameFilter.value:
            doRefresh = True
            if myConfig.FileNameFilter.value == '':
                self["myFilter"].setText(_('Fitering disabled'))
            else:
                self["myFilter"].setText(_('Active filter: %s') % myConfig.FileNameFilter.value)
            self["filelist"].setMatchingPattern(self.buildmatchingPattern())
        #obsluga zmiany nazwy
        if myConfig.FileListSelectedItem.value != '' and myConfig.FileListSelectedItem.value != self.FileListSelectedItem:
                doRefresh = True
                currDir = self.filelist.getCurrentDirectory().strip()
                if self["filelist"].getSelection()[1] == True: # isDir
                    FullPathSource = os.path.join(currDir, self.FileListSelectedItem)
                    if os.path.exists(FullPathSource) and os.path.isdir(FullPathSource):
                        FullPathDest = os.path.join(currDir, myConfig.FileListSelectedItem.value)
                        if FullPathDest.strip() != currDir:
                            printDEBUG("Renaming directory...\n\t %s\n\t %s" % (FullPathSource,FullPathDest))
                            ClearMemory()
                            os.system('mv -f %s %s' % (FullPathSource, FullPathDest))
                    else:
                        printDEBUG("'%s' does not exist. Renaming impossible" % FullPathSource)
                else: #isFile
                    sourceNamePartToReplace = self.FileListSelectedItem + '.'
                    for f in os.listdir(currDir):
                        sourceFile = os.path.join(currDir, f)
                        if os.path.isfile(sourceFile) and sourceNamePartToReplace in f:
                            destFile = sourceFile.replace(sourceNamePartToReplace, myConfig.FileListSelectedItem.value + '.')
                            printDEBUG("Renaming...\n\t %s\n\t %s" % (sourceFile, destFile ))
                            ClearMemory()
                            os.system('mv -f %s %s' % (sourceFile, destFile))

        #finalnie odswierzamy liste, jesli to potrzebne
        if doRefresh:
            self["filelist"].refresh()

    def runConfig(self):
        from Plugins.Extensions.AdvancedFreePlayer.AFPconfig import AdvancedFreePlayerConfig
        self.session.openWithCallback(self.runConfigRet, AdvancedFreePlayerConfig)
        return

    def setSort(self):
        printDEBUG('AFPstart.sort(sortType="%s")' % self.sortType)
        if self.sortType == 'dateasc':    self.sortType = 'datedesc'
        elif self.sortType == 'datedesc': self.sortType = 'name'
        else:                             self.sortType = 'dateasc'

        #wyswietalnie info
        printDEBUG('\t after change sortType="%s"' % self.sortType)
        if self.sortType == 'dateasc':
            self["key_blue"].setText(_("Sorted by date ascending"))
        elif self.sortType == 'datedesc':
            self["key_blue"].setText(_("Sorted by date descending"))
        else:
            self["key_blue"].setText(_("Sorted by name"))
        
        self["filelist"].setSortType(self.sortType)
        self["filelist"].refresh()

    def selectFile(self):
        selection = self["filelist"].getSelection()
        if selection is None:
            return
        elif selection[1] == True: # isDir
            if selection[0] is not None and self.filelist.getCurrentDirectory() is not None and \
                    len(selection[0]) > len(self.filelist.getCurrentDirectory()) or self.LastFolderSelected == None:
                self.LastFolderSelected = selection[0]
                self["filelist"].changeDir(selection[0], "FakeFolderName")
            else:
                print("Folder Down")
                self["filelist"].changeDir(selection[0], self.LastFolderSelected)
            
            d = self.filelist.getCurrentDirectory()
            if d is None:
                d=""
            elif not d.endswith('/'):
                d +='/'
            #self.title = d
            self["myPath"].setText(d)
        else:
            d = self.filelist.getCurrentDirectory()
            if d is None:
                d=""
            elif not d.endswith('/'):
                d +='/'
            f = self.filelist.getFilename()
            printDEBUG("self.selectFile>> " + d + f)
            temp = self.getExtension(f)
            printDEBUG("self.getExtension(%s) = '%s'" %(f,temp))
            if temp == ".url":
                self.opensubtitle = ''
                self.openmovie = ''
                with open(d + f,'r') as UrlContent:
                    for data in UrlContent:
                        #printDEBUG(data)
                        if data.find('movieURL=') > -1: #find instead of startswith to avoid BOM issues ;)
                            self.openmovie = data.split('=')[1].strip()
                            self.URLlinkName = d + f
                        elif data.find('srtURL=') > -1:
                            self.opensubtitle = data.split('=')[1].strip()
                    UrlContent.close()
                printDEBUG("myConfig.KeyOK.value='%s', self.openmovie='%s', self.opensubtitle='%s'" % (myConfig.KeyOK.value, self.openmovie, self.opensubtitle))
                if myConfig.KeyOK.value == 'playmovie' and self.openmovie != '':
                    self.PlayMovie()
                    return
                elif self["filemovie"].getText() != (self.movietxt + self.openmovie):
                    self["filemovie"].setText(self.movietxt + self.openmovie)
                    self["filesubtitle"].setText(self.subtitletxt + self.opensubtitle)
                else:
                    self.openmovie = ''
                    self["filemovie"].setText(self.movietxt)
                    self.opensubtitle = ''
                    self["filesubtitle"].setText(self.subtitletxt + self.opensubtitle)
            elif temp == ".srt" or temp == ".txt":
                #if self.DmnapiInstalled == True:
                if self.opensubtitle == (d + f): #clear subtitles selection
                    self["filesubtitle"].setText(self.subtitletxt)
                    self.opensubtitle = ''
                else:
                    self["filesubtitle"].setText(self.subtitletxt + f)
                    self.opensubtitle = d + f
            else:
                if self.openmovie == (d + f):
                    if myConfig.KeyOK.value == 'play':
                        self.PlayMovie()
                        return
                    else:
                        self.openmovie = ''
                        self["filemovie"].setText(self.movietxt)
                else:
                    self.openmovie = d + f
                    self.URLlinkName = ''
                    if myConfig.KeyOK.value == "playmovie":
                        self.setSubtitles(d + f)
                        self.PlayMovie()
                        return
                    self["filemovie"].setText(self.movietxt + f)
                
                #if self.DmnapiInstalled == True:
                self.setSubtitles(d + f)
        self.buttonsNames()
        
    def setSubtitles(self, movieNameWithPath = ''):
        if movieNameWithPath == '':
            self["filesubtitle"].setText(self.subtitletxt)
            self.opensubtitle = ''
        elif os.path.exists( movieNameWithPath[:-4] + ".srt"):
            self["filesubtitle"].setText(movieNameWithPath[:-4] + ".srt")
            self.opensubtitle = movieNameWithPath[:-4] + ".srt"
        elif os.path.exists( movieNameWithPath[:-4] + ".txt"):
            self["filesubtitle"].setText(movieNameWithPath[:-4] + ".txt")
            self.opensubtitle = movieNameWithPath[:-4] + ".txt"
        else:
            self["filesubtitle"].setText(self.subtitletxt)
            self.opensubtitle = ''
      
    def getExtension(self, MovieNameWithExtension):
        return os.path.splitext( os.path.basename(MovieNameWithExtension) )[1]
      
    def SetLocalDescriptionAndCover(self, MovieNameWithPath):
        FoundCover = False
        FoundDescr = False
        if MovieNameWithPath == '':
            self.setDescription('')
            return FoundCover, FoundDescr
        
        temp = getNameWithoutExtension(MovieNameWithPath)
        WebCoverFile='/tmp/%s.AFP.jpg' % getNameWithoutExtension(self.filelist.getFilename())
        ### COVER ###
        if os.path.exists(temp + '.jpg'):
            self.setCover(temp + '.jpg')
            FoundCover = True
        elif os.path.exists(WebCoverFile) and myConfig.PermanentCoversDescriptons.value == False:
            self.setCover(WebCoverFile)
            FoundCover = True
        else:
            self.setCover('hideCover')
        WebDescrFile='/tmp/%s.AFP.txt' % getNameWithoutExtension(self.filelist.getFilename())
        ### DESCRIPTION from EIT ###
        if os.path.exists(temp + '.eit'):
            def parseMJD(MJD):
                # Parse 16 bit unsigned int containing Modified Julian Date,
                # as per DVB-SI spec
                # returning year,month,day
                YY = int( (MJD - 15078.2) / 365.25 )
                MM = int( (MJD - 14956.1 - int(YY*365.25) ) / 30.6001 )
                D  = MJD - 14956 - int(YY*365.25) - int(MM * 30.6001)
                K=0
                if MM == 14 or MM == 15: K=1
                return "%02d/%02d/%02d" % ( (1900 + YY+K), (MM-1-K*12), D)

            def unBCD(byte):
                return (byte>>4)*10 + (byte & 0xf)

            import struct

            ChannelName = ''
            if os.path.exists(MovieNameWithPath + '.meta'):
                with open(MovieNameWithPath + '.meta','r') as descrTXT:
                    tmpTXT = descrTXT.readline()
                    if tmpTXT.find('::') > -1:
                        ChannelName = _('From: %s\n') % tmpTXT.split('::')[1].strip()
                    descrTXT.close()
                
            with open(temp + '.eit','r') as descrTXT:
                data = descrTXT.read() #[19:].replace('\00','\n')
                ### Below is based on EMC handlers, thanks to author!!!
                e = struct.unpack(">HHBBBBBBH", data[0:12])
                TZhour = unBCD(e[2]) + self.TZoffset
                if TZhour >= 24: TZhour -= 24
                myDescr = _('Recorded: %s %02d:%02d:%02d\n') % (parseMJD(e[1]), TZhour, unBCD(e[3]), unBCD(e[4]) )
                myDescr += ChannelName
                myDescr += _('Lenght: %02d:%02d:%02d\n\n') % (unBCD(e[5]), unBCD(e[6]), unBCD(e[7]) )
                extended_event_descriptor = []
                EETtxt = ''
                pos = 12
                while pos < len(data):
                    rec = ord(data[pos])
                    length = ord(data[pos+1]) + 2
                    if rec == 0x4E:
                    #special way to handle CR/LF charater
                        for i in range (pos+8,pos+length):
                            if str(ord(data[i]))=="138":
                                extended_event_descriptor.append("\n")
                            else:
                                if data[i]== '\x10' or data[i]== '\x00' or  data[i]== '\x02':
                                    pass
                                else:
                                    extended_event_descriptor.append(data[i])
                    pos += length

                    # Very bad but there can be both encodings
                    # User files can be in cp1252
                    # Is there no other way?
                EETtxt = "".join(extended_event_descriptor)
                if EETtxt:
                    try:
                        EETtxt.decode('utf-8')
                    except UnicodeDecodeError:
                        try:
                            EETtxt = EETtxt.decode("cp1250").encode("utf-8")
                        except UnicodeDecodeError:
                            # do nothing, otherwise cyrillic wont properly displayed
                            #extended_event_descriptor = extended_event_descriptor.decode("iso-8859-1").encode("utf-8")
                            pass
                
                self.setDescription(myDescr + ConvertChars(EETtxt) )
                FoundDescr = True
        ### DESCRIPTION from TXT ###
        elif os.path.exists(temp + '.txt'):
            with open(temp + '.txt','r') as descrTXT:
                myDescr = descrTXT.read()
                if len(myDescr) < 4 or myDescr[0] == "{" or myDescr[0] =="[" or myDescr[1] == ":" or myDescr[2] == ":":
                    self.setDescription('')
                else:
                    self.setDescription(myDescr)
                    FoundDescr = True
        elif os.path.exists(WebDescrFile) and myConfig.PermanentCoversDescriptons.value == False:
            with open(WebDescrFile,'r') as descrTXT:
                myDescr = descrTXT.read()
                if len(myDescr) < 4 or myDescr[0] == "{" or myDescr[0] =="[" or myDescr[1] == ":" or myDescr[2] == ":":
                    self.setDescription('')
                else:
                    self.setDescription(myDescr)
                    FoundDescr = True
        else:
            self.setDescription('')
            FoundDescr = False
        #print("Na koniec SetLocalDescriptionAndCover wartosci FoundCover=", FoundCover ,", FoundDescr=", FoundDescr)
        return FoundCover, FoundDescr
    
    def ExitPlayer(self):
        try:
            if self.LastPlayedService:
                self.session.nav.playService(self.LastPlayedService)
            self.openmovie = None
            self.opensubtitle = None
            self.URLlinkName = None
            self.movietxt = None
            self.subtitletxt = None
            self.rootID = None
            self.LastPlayedService = None
            self.LastFolderSelected= None
            self.movieTitle = None
            ClearMemory() #just in case for nbox, where we have limited RAM
            os.system('(rm -rf /tmp/*.AFP.*;mkdir -p %s) &' % myConfig.TrashFolder.value)
            myConfig.PlayerOn.value = False
            myConfig.FileNameFilter.value = ''
            myConfig.FileListSelectedItem.value = ''
            configfile.save()
        except Exception:
            pass
        self.close()
        
    def setDescription(self, Text):
        self["info"].setText( ">>> " + self.movieTitle + " <<< ")
        self["Description"].setText(Text)
        
    def setCover(self, FileName):
        if FileName in ('','hideCover') or not os.path.exists(FileName):
            printDEBUG("setCover hide cover for '%s'" % FileName)
            #self["Cover"].updateIcon('dummyCover')
            self["Cover"].hide()
            try:
                self.session.summary.LCD_hide('LCDpic')
            except Exception:
                pass
        else:
            self["Cover"].updateIcon(FileName)
            try:
              self.session.summary.LCD_showPic('LCDpic', FileName)
            except Exception:
                pass
            self["Cover"].show()
    
    def GetCoverTimerCB(self, AlternateMovieName = ''):
        printDEBUG("GetCoverTimerCB >>>")
        self.GetCoverTimer.stop()
        if self.gettingDataFromWEB == True:
            printDEBUG("AFP is processing webdata, waiting %s ms." % self.ShowDelay)
            self.GetCoverTimer.start(self.ShowDelay,False)
            return
        #wybrano katalog
        if not self["filelist"].getSelection() is None and self["filelist"].getSelection()[1] == True and not self["filelist"].getSelection()[0] is None: # isDir
            self.setDescription('')
            self.setCover('hideCover')
            # do zmiany nazwy, dla katalogu podajemy cala nazwe
            try:
                self.FileListSelectedItem = os.path.basename(os.path.normpath(self["filelist"].getSelection()[0]))
                myConfig.FileListSelectedItem.value = self.FileListSelectedItem
                if self["filelist"].getSelectedIndex() != 0 and self["filelist"].getSelection()[0][:1] != '.':
                    dirFullPath = os.path.join(self.filelist.getCurrentDirectory(), myConfig.FileListSelectedItem.value)
                    printDEBUG("CurrentDirectory path %s" % dirFullPath)
                    dirDescrFile = ''
                    dirPngFile = ''
                    dirError = ''
                    for ft in ('_dir.info', '.dir.info'):
                        ftf = os.path.join(dirFullPath, ft)
                        if os.path.exists(ftf):
                            dirDescrFile = ftf
                            break
                    for ft in ('_dir.png', '.dir.png'):
                        ftf = os.path.join(dirFullPath, ft)
                        if os.path.exists(ftf):
                            dirPngFile = ftf
                            break
                    
                    if dirDescrFile != '':
                        self["Description"].setText(open(dirDescrFile, 'r').read())
                    else:
                        dirError = _('Missing directory info (_dir.info)')
                    
                    if dirPngFile != '':
                        self.setCover(dirPngFile)
                    else:
                        dirError += '\n' + _('Missing directory cover (_dir.png)')
                    
                    if myConfig.DirectoryCoversDescriptons.value == True and dirError != '':
                        self["Description"].setText(dirError)
            except Exception as e:
                printDEBUG("Exception: %s" % str(e))
            return
        
        # wybrano plik
        # do zmiany nazwy, dla plikow, nie podajemy rozszerzenia
        try:
            self.FileListSelectedItem = os.path.splitext( self.filelist.getFilename() )[0]
        except Exception:
            self.FileListSelectedItem = self.filelist.getFilename()
        myConfig.FileListSelectedItem.value = self.FileListSelectedItem

        extension = self.getExtension(self.filelist.getFilename())[1:]
        if not EXTENSIONS.has_key(extension) or EXTENSIONS[extension] != "movie":
            self.setCover('hideCover')
            self.setDescription('')
            return
            
        ClearMemory() #just in case for nbox, where we have limited RAM
           
        ### LOCAL Descriptions and Covers###
        if myConfig.AutoDownloadCoversDescriptions.value == False:
            return
        elif AlternateMovieName == '':
            myMovie, movieYear =cleanFile(self.filelist.getFilename())
            self.movieTitle = myMovie
            FoundCover, FoundDescr = self.SetLocalDescriptionAndCover(self.filelist.getCurrentDirectory() + self.filelist.getFilename())
            if (FoundCover and FoundDescr): #no need to download data if both found locally ;)
                return
        else:
            myMovie, movieYear =cleanFile(myMovie=AlternateMovieName)
            self.movieTitle = myMovie
        
        #print("Status covera i opisu:" , FoundCover,FoundDescr)
        try:
            from twisted.web.client import getPage
            from twisted.web.client import downloadPage
            from twisted.web import client, error as weberror
            #from twisted.internet import defer, reactor
            #from urllib import urlencode
        except:
            printDEBUG("Error importing twisted. Something wrong with the image?")
            self.setDescription(_("Error importing twisted package. Seems something wrong with the image. :("))
            return
        # checking if network connection is working
        if not isINETworking():
            self.setDescription(_("No internet connection. :("))
            return
            
        def WebCover(ret):
            print("[AdvancedFreePlayer] WebCover >>>")
            self.gettingDataFromWEB = False
            self.setCover(WebCoverFile)
            return
        def dataError(error = '', errorType='downloading'):
            printDEBUG("Error %s data %s" % ( str(errorType),str(error)))
            self.gettingDataFromWEB = False
            return
            
        def readTmBD(data, movieYear, isMovie,myMovie):
            printDEBUG("[readTmBD] >>>") #DEBUG
            f = open('/tmp/TmBD.AFP.webdata', 'w')
            f.write(data)
            f.close
            if isMovie == True:
                try: 
                    list = json.loads(data)
                except:
                    self.gettingDataFromWEB = False
                    return
                data=None # some cleanup, just in case
                if 'total_results' in list:
                    coverPath=''
                    overview=''
                    release_date=''
                    id=''
                    otitle=''
                    original_language=''
                    title=''
                    popularity=''
                    coverUrl = ''
                    vote_average=''
                    #>>>>>>>>>>>>>>>>>>>>>>>>>>>> znajdowanie najlepszego kandydata z listy
                    selectedIndex = 0
                    selectedIndexScore = 0
                    currIndex = 0
                    myMovieLC =myMovie.decode('utf-8', 'ignore').lower()
                    if list['total_results'] > 1:
                        for myItem in list['results']:
                            currScore = 0
                            if myMovieLC == myItem['original_title'].decode('utf-8', 'ignore').lower(): currScore += 10 #jesli org tytul jest taki sam to najwyzszy priorytet
                            if myMovieLC == myItem['title'].decode('utf-8', 'ignore').lower(): currScore += 5 #jesli tytul jest taki sam to drugi najwyzszy priorytet
                            if movieYear != '' and movieYear == myItem['release_date']: currScore += 5 #w efekcie daje w polaczeniu z title takia sama wage jak ortitle
                            if myItem['original_language'] == 'pl': currScore += 4 #wybor wedlug priorytetu jezyka
                            elif myItem['original_language'] == 'en': currScore += 3
                            elif myItem['original_language'] == 'de': currScore += 2
                            elif myItem['original_language'] == 'fr': currScore += 1
                            printDEBUG(">>> film '%s'-analiza indeksu %d(%s): currScore=%d, selIndex=%d, selScore=%d" %(myMovie,
                                                        currIndex, myItem['title'],currScore, selectedIndex, selectedIndexScore))
                            if currScore > selectedIndexScore:
                                selectedIndexScore = currScore
                                selectedIndex = currIndex
                            currIndex += 1
                    # pobieranie danych dla wybranego filmu
                    myItem = list['results'][selectedIndex]
                    if not myItem['poster_path'] is None:
                        coverPath=myItem['poster_path'].encode('ascii','ignore')
                    overview=myItem['overview']
                    release_date=myItem['release_date']
                    id=myItem['id']
                    otitle=myItem['original_title']
                    original_language=myItem['original_language']
                    title=myItem['title']
                    popularity='{:.2f}'.format(myItem['popularity'])
                    vote_average='{:.2f}'.format(myItem['vote_average'])
                    if coverPath != '':
                        coverUrl = "http://image.tmdb.org/t/p/%s%s" % (myConfig.coverfind_themoviedb_coversize.value, coverPath)
                        coverUrl = coverUrl.replace('\/','/')
                    Pelny_opis=overview + '\n\n' + _('Released: ') + release_date + '\n' + \
                                                _('Original title: ') + otitle +'\n' + _('Original language: ') + \
                                                original_language +'\n' + _('Popularity: ') + popularity + '\n' + \
                                                _('Score: ') + vote_average + '\n'
                    printDEBUG("========== Dane filmu %s ==========\nPlakat: %s,\n%s\n====================" %(title, coverUrl,Pelny_opis))
                    printDEBUG(WebDescrFile)
                    if not os.path.exists(WebDescrFile) and Pelny_opis.strip() != '':
                        with open(WebDescrFile, 'w') as WDF:
                            WDF.write(Pelny_opis)
                            WDF.close()
                    if FoundDescr == False:
                        printDEBUG("FoundDescr == False")
                        with open(WebDescrFile,'r') as descrTXT:
                            myDescr = descrTXT.read()
                            self.setDescription(myDescr)
                    if FoundCover == False or coverUrl != '': #no need to download cover, if we have it, or if there is no cover url. ;)
                        downloadPage(coverUrl,WebCoverFile).addCallback(WebCover).addErrback(dataError)
                
                else:
                    self.gettingDataFromWEB = False
                    return
            else: #dane seriali sa w xml-u!!!!
                list = re.findall('<seriesid>(.*?)</seriesid>.*?<language>(.*?)</language>.*?<SeriesName>(.*?)</SeriesName>.*?<banner>(.*?)</banner>.*?<Overview>(.*?)</Overview>.*?<FirstAired>(.*?)</FirstAired>', data, re.S)
                printDEBUG("len(list) = %s" % len(list)) #DEBUG
                if list is not None and len(list)>0:
                    #print">>>>>>>>>>>>>>>>>>>>>>>>>",list
                    idx = 0
                    seriesid, original_language, SeriesName, banner, overview, FirstAired = list[idx]
                    coverUrl = "http://www.thetvdb.com%s" % banner
                    printDEBUG("coverUrl = %s" % coverUrl)
                    if FoundDescr == False:
                        printDEBUG("Series FoundDescr == False")
                        myDescr = (overview + '\n\n' + _('Released: ') + FirstAired + '\n' + _('Original title: ') + SeriesName +'\n' + _('Original language: ') + \
                                    original_language +'\n')
                        self.setDescription(myDescr)
                        with open(WebDescrFile, 'w') as WDF:
                            WDF.write(self["Description"].getText() )
                            WDF.close()
                    if FoundCover == False: #no need to download cover, if we have it. ;)
                        downloadPage(coverUrl,WebCoverFile).addCallback(WebCover).addErrback(dataError,errorType='downloading cover')
                else:
                    self.gettingDataFromWEB = False
                    return
        
        def HTML(txt):
            return txt.replace(' ','%20').replace('&', '%26')
            
        #start >>>
        myMovie=DecodeNationalLetters(myMovie)
        if myConfig.PermanentCoversDescriptons.value == True:
            WebCoverFile='%s/%s.jpg' % (self.filelist.getCurrentDirectory(), getNameWithoutExtension(self.filelist.getFilename()) )
            WebDescrFile='%s/%s.txt' % (self.filelist.getCurrentDirectory(), getNameWithoutExtension(self.filelist.getFilename()) )
        else:
            WebCoverFile='/tmp/%s.AFP.jpg' % getNameWithoutExtension(self.filelist.getFilename())
            WebDescrFile='/tmp/%s.AFP.txt' % getNameWithoutExtension(self.filelist.getFilename())
            
        printDEBUG("mySeries = %s" % self.filelist.getFilename())
        printDEBUG("Description = %s" % self["Description"].getText())
        if re.search('[Ss][0-9]+[Ee][0-9]+', myMovie):
            printDEBUG("re.search('[Ss][0-9]+[Ee][0-9]+'")
            seriesName=re.sub('[Ss][0-9]+[Ee][0-9]+.*','', myMovie, flags=re.I)
            url = "http://thetvdb.com/api/GetSeries.php?seriesname=%s&language=%s" % (HTML(seriesName),myConfig.coverfind_language.value)
            isMovie = False
        elif re.search('odc[_ ]*[0-9]+', self.filelist.getFilename()): #odc w nazwie pliku
            printDEBUG("SERIAL >>> odc w nazwie pliku")
            seriesName=re.sub('odc.*','', myMovie, flags=re.I).replace('(','').replace(')','')
            url = "http://thetvdb.com/api/GetSeries.php?seriesname=%s&language=%s" % (HTML(seriesName),myConfig.coverfind_language.value)
            isMovie = False
        elif re.search('odc[\. ]+[0-9]+', self["Description"].getText()): #odc w opisie
            printDEBUG("re.search('odc.*[0-9]+'")
            seriesName= myMovie #re.sub('.odc_.*','', myMovie, flags=re.I)
            url = "http://thetvdb.com/api/GetSeries.php?seriesname=%s&language=%s" % (HTML(seriesName),myConfig.coverfind_language.value)
            isMovie = False
        else:
            url = "http://api.themoviedb.org/3/search/movie?api_key=8789cfd3fbab7dccf1269c3d7d867aff&query=%s&language=%s" % (HTML(myMovie),myConfig.coverfind_language.value)
            isMovie = True
        if self.gettingDataFromWEB == True:
            printDEBUG("[GetFromTMDBbyName] getPage running, skip '%s'this time" % url) #DEBUG
        else:
            printDEBUG("[GetFromTMDBbyName] url: " + url) #DEBUG
            self.gettingDataFromWEB = True
            getPage(url, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(readTmBD,movieYear,isMovie,myMovie).addErrback(dataError,errorType='getting data')
        
##################################################################### SUBTITLES >>>>>>>>>>
    def runDMnapi(self):
        if self.DmnapiInstalled == True:
            self.DMnapi()
            self["filelist"].refresh()
        else:
            def doNothing():
                pass
            def goUpdate(ret):
                if ret is True:
                    runlist = []
                    runlist.append( ('chmod 755 %s/scripts/Update*.sh' % PluginPath) )
                    runlist.append( ('cp -a %s/scripts/UpdateDMnapi.sh /tmp/AFPUpdate.sh' % PluginPath) ) #to have clear path of updating this script too ;)
                    runlist.append( ('/tmp/AFPUpdate.sh %s "%s"' % (config.plugins.AdvancedFreePlayer.Version.value,PluginInfo)) )
                    from AFPconfig import AdvancedFreePlayerConsole
                    self.session.openWithCallback(doNothing, AdvancedFreePlayerConsole, title = _("Installing DMnapi plugin"), cmdlist = runlist)
                    return
            self.session.openWithCallback(goUpdate, MessageBox,_("Do you want to install DMnapi plugin?"),  type = MessageBox.TYPE_YESNO, timeout = 10, default = False)
        return

    def DMnapi(self):
        if not self["filelist"].canDescent():
            f = self.filelist.getFilename()
            temp = f[-4:]
            if temp != ".srt" and temp != ".txt":
                curSelFile = self["filelist"].getCurrentDirectory() + self["filelist"].getFilename()
                try:
                    from Plugins.Extensions.DMnapi.DMnapi import DMnapi
                    self.session.openWithCallback(self.dmnapiCallback, DMnapi, curSelFile)
                except:
                    printDEBUG("Exception loading DMnapi!!!")
            else:
                self.session.open(MessageBox,_("Please select movie files !\n\n"),MessageBox.TYPE_INFO)
                return

    def dmnapiCallback(self, answer=False):
        self["filelist"].refresh()
        
    def createSummary(self):
        return AdvancedFreePlayerStartLCD
##################################################################### LCD Screens <<<<<<<<<<<<<<<<<<<<<<<<<<<<<
class AdvancedFreePlayerStartLCD(Screen):
    def __init__(self, session, parent):
        self.skin = LoadSkin('AdvancedFreePlayerStartLCD')
        Screen.__init__(self, session)
        try:
            self["text1"] =  Label(PluginName)
            self["text2"] = Label(PluginInfo)
            self["LCDpic"] = j00zekAccellPixmap()
            self["AFPlogo"] = j00zekAccellPixmap()
            printDEBUG("AdvancedFreePlayerStartLCD:__init__ using j00zekAccellPixmap()")
            self.onShow.append(self.LCD_showLogo)
        except Exception as e:
            printDEBUG("AdvancedFreePlayerStartLCD:__init__ Exception %s" % str(e))

    def LCD_showLogo(self):
        self.LCD_showPic('AFPlogo' ,"/usr/lib/enigma2/python/Plugins/Extensions/AdvancedFreePlayer/AdvancedFreePlayer.png")
    
    def setText(self, text):
        printDEBUG("setText(%s)" % text)
        try:
            self["text2"].setText(text[0:39])
        except Exception: pass

    def LCD_showPic(self, widgetName, picPath):
        printDEBUG("AdvancedFreePlayerStartLCD:LCD_showPic(%s, picPath=%s)" % (widgetName,picPath))
        try:
            self[widgetName].updateIcon(picPath)
            self[widgetName].show()
        except Exception: pass

    def LCD_hide(self, widgetName):
        printDEBUG("LCD_hide(%s)" % widgetName)
        try:
            self[widgetName].hide()
        except Exception: pass
                
##################################################################### CLASS ENDS <<<<<<<<<<<<<<<<<<<<<<<<<<<<< 