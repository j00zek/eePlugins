# -*- coding: utf-8 -*-
from __init__ import *
from __init__ import translate as _
from re import compile as re_compile
from os import path as os_path, listdir
from Components.config import config
from Components.GUIComponent import GUIComponent
from Components.MenuList import MenuList
from Components.Harddisk import harddiskmanager
from enigma import RT_HALIGN_LEFT, eListboxPythonMultiContent, eServiceReference, eServiceCenter, gFont, getDesktop
from skin import parseFont, parseColor
from Tools.Directories import SCOPE_CURRENT_SKIN, resolveFilename, fileExists
from Tools.LoadPixmap import LoadPixmap

EXTENSIONS = {
        "ts": "movie",
        "avi": "movie",
        "divx": "movie",
        "m4v": "movie",
        "mpg": "movie",
        "mpeg": "movie",
        "mkv": "movie",
        "mp4": "movie",
        "mov": "movie",
        "flv": "movie",
        
        "mp2": "music",
        "mp3": "music",
        "m4a": "music",
        "ogg": "music",
        "wav": "music",
        "fla": "music",
        "flac": "music",
        
        "jpg": "picture",
        "jpeg": "picture",
        "png": "picture",
        "bmp": "picture",
        
        "txt": "text",
        "srt": "text"
    }

import struct
cutsParser = struct.Struct('>QI') # big-endian, 64-bit PTS and 32-bit type

def getCut(cutsFileName, name):
    printDEBUG('getLastWatched >>>')
    CUT_TYPE_LAST = 3
    CUT_TYPE_LENGTH = 5
    data = ''
    currpts=0
    currLength=0
    try:
        f = open(cutsFileName, 'rb')
        data = f.read()
        f.close()
    except:
        return 0,0
    if data:
        pos = 0
        while pos + 12 <= len(data):
            pts, what = struct.unpack('>QI', data[pos:pos + 12])
            if what == CUT_TYPE_LAST and pts > currpts:
                currpts = int(pts/90/1000/60) #in mins
            elif what == CUT_TYPE_LENGTH and pts > currLength:
                currLength = int(pts/90/1000/60)
            printDEBUG("getCuts|%s: pts=%d,what=%d" %(name, pts, what))
            pos += 12
    return currpts,currLength

def FileEntryComponent(name, absolute = None, isDir = False, goBack = False, currDir = None, DimText0 = (45, 1, 1020, 35, 0), DimText1 = (0, 0, 0, 0), DimPIC = (5, 4, 25, 25) ):
    def getInfo(info):#currLang
        info =  "_skin_" + info + ".txt"
        if os_path.exists(SkinPath + "allInfos/info_" + currLang + info):
            myInfoFile=SkinPath + "allInfos/info_" + currLang + info
        elif os_path.exists(SkinPath + "allInfos/info_en_" + info):
            myInfoFile=SkinPath + "allInfos/info_en_" + info
        else:
            #return 'No Info'
            return ''
        info = open(myInfoFile, 'r').read().strip()
        return info
        
    def translateName(name):
        import re
        wordsList=['Channel[ ]*Selections','Channel[ ]*Selection','Infobars','Infobar','_no_']
        for word in wordsList:
            name = re.sub(word , _(word), name, flags=re.I)
        name = re.sub('(\_|\-|\.|\+)',' ', name, flags=re.I) #cleaning
        name = re.sub('(  [ ]*)',' ', name, flags=re.I) #merge multiple (2+) spaces into one
        return name
        
    res = [ (absolute, isDir) ]
    if config.plugins.AdvancedFreePlayer.NamesNOfiles.value and isDir == False:
        res.append((eListboxPythonMultiContent.TYPE_TEXT, DimText0[0], DimText0[1], DimText0[2], DimText0[3], 0, RT_HALIGN_LEFT, cleanFile(name,ReturnMovieYear = False) ))
    else:
        res.append((eListboxPythonMultiContent.TYPE_TEXT, DimText0[0], DimText0[1], DimText0[2], DimText0[3], 0, RT_HALIGN_LEFT, name))
    if isDir:
        png = LoadPixmap(cached=True, path="%spic/folder.png" % PluginPath)
    else:
        extension = name.split('.')
        extension = extension[-1].lower()
        if EXTENSIONS.has_key(extension):
            status=''
            if currDir is not None and EXTENSIONS[extension] == "movie":
                if not os_path.exists("%s/%s.cuts" %(currDir,absolute)):
                    status='0'
                else:
                    lastPosition, Length = getCut("%s/%s.cuts" %(currDir,absolute), absolute)
                    if lastPosition <= 1: #lastPositionInPTS = 10(seconds) * 90 * 1000
                        status='0'
                    elif Length == 0:
                        if lastPosition <= 25: #1min = 5 400 000
                            status='25'
                        elif lastPosition <= 50: #1min = 5 400 000
                            status='50'
                        elif lastPosition <= 75: #1min = 5 400 000
                            status='75'
                        else:
                            status='100'
                    else:
                        ratio=round(Length)/lastPosition
                        if ratio >= 4:
                            status='25'
                        elif ratio >= 2:
                            status='50'
                        elif ratio > 1.33:
                            status='75'
                        else:
                            status='100'

                #    service = getPlayerService(fullpath, movie, ext)
                #    progress, length = getProgress(service, forceRecalc=True)

            if os_path.exists(resolveFilename(SCOPE_CURRENT_SKIN, "extensions/" + EXTENSIONS[extension] + status + ".png")):
                png = LoadPixmap(resolveFilename(SCOPE_CURRENT_SKIN, "extensions/" + EXTENSIONS[extension] + ".png"))
            else:
                print("%spic/%s%s.png" % (PluginPath,EXTENSIONS[extension],status))
                png = LoadPixmap("%spic/%s%s.png" % (PluginPath,EXTENSIONS[extension],status))
        else:
            png = None
    if png is not None:
        res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHATEST, DimPIC[0], DimPIC[1], DimPIC[2], DimPIC[3], png))
    return res

class FileList(MenuList):
    def __init__(self, directory, showDirectories = True, showFiles = True, showMountpoints = True, matchingPattern = None, useServiceRef = False, inhibitDirs = False, inhibitMounts = False, isTop = False, enableWrapAround = False, additionalExtensions = None, sortDate=False):
        MenuList.__init__(self, list, enableWrapAround, eListboxPythonMultiContent)
        GUIComponent.__init__(self)

        self.additional_extensions = additionalExtensions
        self.mountpoints = []
        self.current_directory = None
        self.current_mountpoint = None
        self.useServiceRef = useServiceRef
        self.showDirectories = showDirectories
        self.showMountpoints = showMountpoints
        self.showFiles = showFiles
        self.isTop = isTop
        # example: matching .nfi and .ts files: "^.*\.(nfi|ts)"
        self.matchingPattern = matchingPattern
        self.inhibitDirs = inhibitDirs or []
        self.inhibitMounts = inhibitMounts or []
        self.sortDate = sortDate

        self.refreshMountpoints()
        #self.changeDir(directory)
        #self.l.setFont(0, gFont("Regular", int(config.plugins.AdvancedFreePlayer.FileListFontSize.value)))
        #self.l.setItemHeight(35)
        self.serviceHandler = eServiceCenter.getInstance()

        #default values:
        self.font0 = gFont("Regular",22)
        self.font1 = gFont("Regular",16)
        self.itemHeight = 35
        self.DimText0 = (45, 1, 1020, 35, 0)
        self.DimText1 = (0, 0, 0, 0) # not used here
        self.DimPIC = (5, 4, 25, 25)
        
    def applySkin(self, desktop, parent):
        def font0(value):
            self.font0 = parseFont(value, ((1,1),(1,1)))
        def font1(value):
            self.font1 = parseFont(value, ((1,1),(1,1)))
        def itemHeight(value):
            self.itemHeight = int(value)
        def DimText0(value):
            self.DimText0 = ( int(value.split(',')[0]), int(value.split(',')[1]), int(value.split(',')[2]), int(value.split(',')[3]) )
        def DimText1(value):
            self.DimText1 = ( int(value.split(',')[0]), int(value.split(',')[1]), int(value.split(',')[2]), int(value.split(',')[3]) )
        def DimPIC(value):
            self.DimPIC = ( int(value.split(',')[0]), int(value.split(',')[1]), int(value.split(',')[2]), int(value.split(',')[3]) )
          
        for (attrib, value) in list(self.skinAttributes):
            try:
                locals().get(attrib)(value)
                self.skinAttributes.remove((attrib, value))
            except:
                pass
              
        self.l.setFont(0,self.font0)
        #self.l.setFont(1,self.font1)
        self.l.setItemHeight(self.itemHeight)
        return GUIComponent.applySkin(self, desktop, parent)
        
    def refreshMountpoints(self):
        self.mountpoints = [os_path.join(p.mountpoint, "") for p in harddiskmanager.getMountedPartitions()]
        self.mountpoints.sort(reverse = True)

    def getMountpoint(self, file):
        file = os_path.join(os_path.realpath(file), "")
        for m in self.mountpoints:
            if file.startswith(m):
                return m
        return False

    def getMountpointLink(self, file):
        if os_path.realpath(file) == file:
            return self.getMountpoint(file)
        else:
            if file[-1] == "/":
                file = file[:-1]
            mp = self.getMountpoint(file)
            last = file
            file = os_path.dirname(file)
            while last != "/" and mp == self.getMountpoint(file):
                last = file
                file = os_path.dirname(file)
            return os_path.join(last, "")

    def getSelection(self):
        if self.l.getCurrentSelection() is None:
            return None
        return self.l.getCurrentSelection()[0]

    def getCurrentEvent(self):
        l = self.l.getCurrentSelection()
        if not l or l[0][1] == True:
            return None
        else:
            return self.serviceHandler.info(l[0][0]).getEvent(l[0][0])

    def getFileList(self):
        return self.list

    def inParentDirs(self, dir, parents):
        dir = os_path.realpath(dir)
        for p in parents:
            if dir.startswith(p):
                return True
        return False

    def changeDir(self, directory, select = None):
        self.list = []

        # if we are just entering from the list of mount points:
        if self.current_directory is None:
            if directory and self.showMountpoints:
                self.current_mountpoint = self.getMountpointLink(directory)
            else:
                self.current_mountpoint = None
        self.current_directory = directory
        directories = []
        files = []

        if directory is None and self.showMountpoints: # present available mountpoints
            for p in harddiskmanager.getMountedPartitions():
                path = os_path.join(p.mountpoint, "")
                if path not in self.inhibitMounts and not self.inParentDirs(path, self.inhibitDirs):
                    self.list.append(FileEntryComponent(name = p.description, absolute = path, isDir = True, currDir = self.current_directory))
            files = [ ]
            directories = [ ]
        elif directory is None:
            files = [ ]
            directories = [ ]
        elif self.useServiceRef:
            root = eServiceReference("2:0:1:0:0:0:0:0:0:0:" + directory)
            if self.additional_extensions:
                root.setName(self.additional_extensions)
            serviceHandler = eServiceCenter.getInstance()
            list = serviceHandler.list(root)

            while 1:
                s = list.getNext()
                if not s.valid():
                    del list
                    break
                if s.flags & s.mustDescent:
                    directories.append(s.getPath())
                else:
                    files.append(s)
            directories.sort(key=lambda s: s.lower())
            files.sort(key=lambda s: s.lower())
        else:
            if fileExists(directory):
                try:
                    files = listdir(directory)
                    
                except:
                    files = []
                if self.sortDate:
                    try: files.sort(key=lambda s: os_path.getmtime(os_path.join(directory, s)))
                    except Exception: print("Exception sorting by date!!!")
                    files.reverse()
                elif config.plugins.AdvancedFreePlayer.NamesNOfiles.value:
                    try: files.sort(key=lambda s: cleanFile(s,ReturnMovieYear = False).lower() )
                    except Exception: print("Exception sorting by MovieName!!!")
                else:
                    files.sort()
                tmpfiles = files[:]
                for x in tmpfiles:
                    if os_path.isdir(directory + x):
                        directories.append(directory + x + "/")
                        files.remove(x)

        if directory is not None and self.showDirectories and not self.isTop:
            if directory == self.current_mountpoint and self.showMountpoints:
                self.list.append(FileEntryComponent(name = "<" +_("List of Storage Devices") + ">", absolute = None, isDir = True))
            elif (directory != "/") and not (self.inhibitMounts and self.getMountpoint(directory) in self.inhibitMounts):
                #self.list.append(FileEntryComponent(name = "<" +_("Parent Directory") + ">", absolute = '/'.join(directory.split('/')[:-2]) + '/', isDir = True))
                self.list.append(FileEntryComponent(name = _("Parent Directory"), absolute = '/'.join(directory.split('/')[:-2]) + '/', isDir = True, goBack = True, DimText0 = self.DimText0, DimText1=self.DimText1, DimPIC=self.DimPIC))

        if self.showDirectories:
            for x in directories:
                if not (self.inhibitMounts and self.getMountpoint(x) in self.inhibitMounts) and not self.inParentDirs(x, self.inhibitDirs):
                    name = x.split('/')[-2]
                    #self.list.append(FileEntryComponent(name = name, absolute = x, isDir = True))
                    self.list.append(FileEntryComponent(name = name, absolute = x, isDir = True, DimText0 = self.DimText0, DimText1=self.DimText1, DimPIC=self.DimPIC))

        if self.showFiles:
            for x in files:
                if self.useServiceRef:
                    path = x.getPath()
                    name = path.split('/')[-1]
                else:
                    path = directory + x
                    name = x

                if (self.matchingPattern is None) or re_compile(self.matchingPattern).search(path):
                    #self.list.append(FileEntryComponent(name = name, absolute = x , isDir = False))
                    self.list.append(FileEntryComponent(name = name, absolute = x , isDir = False, currDir = self.current_directory, DimText0 = self.DimText0, DimText1=self.DimText1, DimPIC=self.DimPIC))

        if self.showMountpoints and len(self.list) == 0:
            self.list.append(FileEntryComponent(name = _("nothing connected"), absolute = None, isDir = False, currDir = self.current_directory, DimText0 = self.DimText0, DimText1=self.DimText1, DimPIC=self.DimPIC))

        self.l.setList(self.list)

        if select is not None:
            i = 0
            self.moveToIndex(0)
            for x in self.list:
                p = x[0][0]
                if isinstance(p, eServiceReference):
                    p = p.getPath()
                if p == select:
                    self.moveToIndex(i)
                i += 1

    def sortDateEnable(self):
        #print("sortDateEnable")
        self.sortDate=True

    def sortDateDisable(self):
        #print("sortDateDisable")
        self.sortDate=False

    def getCurrentDirectory(self):
        return self.current_directory

    def canDescent(self):
        if self.getSelection() is None:
            return False
        return self.getSelection()[1]

    def descent(self):
        if self.getSelection() is None:
            return
        self.changeDir(self.getSelection()[0], select = self.current_directory)

    def getFilename(self):
        if self.getSelection() is None:
            return None
        x = self.getSelection()[0]
        if isinstance(x, eServiceReference):
            x = x.getPath()
        return x

    def getServiceRef(self):
        if self.getSelection() is None:
            return None
        x = self.getSelection()[0]
        if isinstance(x, eServiceReference):
            return x
        return None

    def execBegin(self):
        harddiskmanager.on_partition_list_change.append(self.partitionListChanged)

    def execEnd(self):
        harddiskmanager.on_partition_list_change.remove(self.partitionListChanged)

    def refresh(self):
        self.changeDir(self.current_directory, self.getFilename())

    def partitionListChanged(self, action, device):
        self.refreshMountpoints()
        if self.current_directory is None:
            self.refresh()
