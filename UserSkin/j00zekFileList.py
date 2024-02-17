# -*- coding: utf-8 -*-
from __future__ import absolute_import #zmiana strategii ladowanie modulow w py2 z relative na absolute jak w py3
from Components.GUIComponent import GUIComponent
from Components.MenuList import MenuList
from enigma import RT_HALIGN_LEFT, eListboxPythonMultiContent, gFont, getDesktop
from skin import parseFont, parseColor
from Tools.Directories import fileExists
from Tools.LoadPixmap import LoadPixmap

from os import path as os_path, listdir
from Plugins.Extensions.UserSkin.inits import *
from Plugins.Extensions.UserSkin.translate import _
from Plugins.Extensions.UserSkin.debug import printDEBUG

##################################################### treeSelector #####################################################

def FileEntryComponent(name, absolute = None, isDir = False, goBack = False, DimText0 = (60, 2, 500, 22), DimText1 = (80, 24, 500, 32), DimPIC = (2, 2, 54, 54) ):
    def tr(name):#currLang
        infoFile =  SkinPath + "allInfos/skin_" + name + ".txt"
        open("/tmp/test2.txt", "a").write('"%s"="%s"\n' % (name, str(absolute)))
        if os_path.exists(infoFile):
            with open(infoFile, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('#title%s:' % currLang.upper()):
                        name = line.split(':')[1]
                        break
        return _(name)
        
    res = [ (absolute, isDir) ]
    
    if isDir:
        res.append(( eListboxPythonMultiContent.TYPE_TEXT, DimText0[0], DimText0[1], DimText0[2], DimText0[3], 0, RT_HALIGN_LEFT, _(name) ))
        res.append(( eListboxPythonMultiContent.TYPE_TEXT, DimText1[0], DimText1[1], DimText1[2], DimText1[3], 1, RT_HALIGN_LEFT, ""))
        if goBack == True:
            png = LoadPixmap( cached=True, path = getPixmapPath("back.png") )
        else:
            png = LoadPixmap( cached=True, path = getPixmapPath("folder.png") )
        res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHATEST, DimPIC[0], DimPIC[1], DimPIC[2], DimPIC[3], png))
        res.append(("f"))
    else:
        description = '' #getInfo(name)
        res.append((eListboxPythonMultiContent.TYPE_TEXT, DimText0[0], DimText0[1], DimText0[2], DimText0[3], 0, RT_HALIGN_LEFT, tr(name) ))
        res.append((eListboxPythonMultiContent.TYPE_TEXT, DimText1[0], DimText1[1], DimText1[2], DimText1[3], 1, RT_HALIGN_LEFT, description))
        fileName = os_path.basename(absolute)
        if os_path.exists(SkinPath + "UserSkin_Selections/" + fileName):
            png = LoadPixmap( cached=True, path = getPixmapPath("install.png") )
            installed = "i"
        else:
            png = LoadPixmap( cached=True, path = getPixmapPath("remove.png") )
            installed = "r"
        res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHATEST, DimPIC[0], DimPIC[1], DimPIC[2], DimPIC[3], png))
        res.append((installed))
    return res

class FileList(MenuList):
    def __init__(self, directory, enableWrapAround = False):
        MenuList.__init__(self, list, enableWrapAround, eListboxPythonMultiContent)
        GUIComponent.__init__(self)
        
        self.mountpoints = []
        self.current_directory = directory
        self.current_mountpoint = None
        self.showDirectories = True
        self.rootDirectory = directory
        self.showFiles = True
        # example: matching .nfi and .ts files: "^.*\.(nfi|ts)"
        self.inhibitDirs = []
        self.inhibitMounts = []

        #default values:
        self.font0 = gFont("Regular",22)
        self.font1 = gFont("Regular",16)
        self.itemHeight = 60
        self.DimText0 = (60, 2, 500, 22)
        self.DimText1 = (80, 24, 500, 32)
        self.DimPIC = (2, 2, 54, 54)
        
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
        self.l.setFont(1,self.font1)
        self.l.setItemHeight(self.itemHeight)
        return GUIComponent.applySkin(self, desktop, parent)
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
        #else:
        #    return self.serviceHandler.info(l[0][0]).getEvent(l[0][0])

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
            self.current_mountpoint = None
            
        self.current_directory = directory
        directories = []
        files = []        

        if directory is None:
            files = [ ]
            directories = [ ]
        else:
            if fileExists(directory):
                try:
                    files = listdir(directory)
                except:
                    files = []
                files.sort(key=lambda s: s.lower())
                #files.sort()
                tmpfiles = files[:]
                for x in tmpfiles:
                    if os_path.isdir(os_path.join(directory,x) ):
                        directories.append(os_path.join(directory,x) + "/")
                        files.remove(x)

        if directory is not None and self.showDirectories:
            #to resolve issues wit "/" at the end
            if ( (directory != self.rootDirectory and directory[:-1] != self.rootDirectory and directory != self.rootDirectory[:-1]) and not
                    (self.inhibitMounts and self.getMountpoint(directory) in self.inhibitMounts) ):
                self.list.append(FileEntryComponent(name = _("Parent Category"), absolute = '/'.join(directory.split('/')[:-2]) + '/', isDir = True, goBack = True, DimText0 = self.DimText0, DimText1=self.DimText1, DimPIC=self.DimPIC))

        if self.showDirectories:
            for x in directories:
                if not (self.inhibitMounts and self.getMountpoint(x) in self.inhibitMounts) and not self.inParentDirs(x, self.inhibitDirs):
                    name = x.split('/')[-2]
                    if not listdir(x):
                        name += _(' (install from OPKG)')
                    self.list.append(FileEntryComponent(name = name, absolute = x, isDir = True, DimText0 = self.DimText0, DimText1=self.DimText1, DimPIC=self.DimPIC))

        if self.showFiles:
            for x in files:
                path = directory + x
                name = x

                if name.startswith('skin_') and name.endswith('.xml'):
                    name = name[5:-4]
                    self.list.append(FileEntryComponent(name = name, absolute = x , isDir = False, DimText0 = self.DimText0, DimText1=self.DimText1, DimPIC=self.DimPIC))

        self.l.setList(self.list)

        if select is not None:
            i = 0
            self.moveToIndex(0)
            for x in self.list:
                p = x[0][0]
                if p == select:
                    self.moveToIndex(i)
                i += 1

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
        #if isinstance(x, eServiceReference):
        #    x = x.getPath()
        return x

    def getServiceRef(self):
        if self.getSelection() is None:
            return None
        x = self.getSelection()[0]
        #if isinstance(x, eServiceReference):
        #    return x
        return None

    def refresh(self):
        self.changeDir(self.current_directory, self.getFilename())
