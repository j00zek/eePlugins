# -*- coding: utf-8 -*-
###################################################
from __future__ import absolute_import #zmiana strategii ladowania modulow w py2 z relative na absolute jak w py3
from Screens.Screen import Screen
from Screens.HelpMenu import HelpableScreen
from Screens.VirtualKeyBoard import VirtualKeyBoard
from Screens.MessageBox import MessageBox
from Components.FileList import FileList
from Components.Sources.StaticText import StaticText
from Components.Label import Label
from Components.ActionMap import ActionMap
from Tools.BoundFunction import boundFunction
from os import path as os_path, mkdir as os_mkdir
from __init__ import *
_ = mygettext
###################################################
 
class DirectorySelectorWidget(Screen):
    skin = """
    <screen name="DirectorySelectorWidget" position="center,center" size="620,440" title="DirectorySelectorWidget">
            <widget name="key_red"     position="10,10"  zPosition="2"  size="600,35" valign="center"  halign="left"   font="Regular;22" transparent="1" foregroundColor="red" />
            <widget name="key_blue"    position="10,10"  zPosition="2"  size="600,35" valign="center"  halign="center" font="Regular;22" transparent="1" foregroundColor="blue" />
            <widget name="key_green"   position="10,10"  zPosition="2"  size="600,35" valign="center"  halign="right"  font="Regular;22" transparent="1" foregroundColor="green" />
            <widget name="curr_dir"    position="10,50"  zPosition="2"  size="600,35" valign="center"  halign="left"   font="Regular;18" transparent="1" foregroundColor="white" />
            <widget name="filelist"    position="10,85"  zPosition="1"  size="580,335" transparent="1" scrollbarMode="showOnDemand" />
    </screen>"""
    def __init__(self, session, currDir, title="Directory browser", selectFiles = True):
        print("DirectorySelectorWidget.__init__ -------------------------------")
        Screen.__init__(self, session)
        self["key_red"]    = Label(_("Cancel"))
        #self["key_yellow"] = Label(_("Refresh"))
        self["key_blue"]   = Label(_("New directory"))
        self["key_green"]  = Label(_("Apply"))
        self["curr_dir"]   = Label(_(" "))
        self.filelist      = FileList(directory=currDir, matchingPattern="", showFiles=selectFiles)
        self["filelist"]   = self.filelist
        self["FilelistActions"] = ActionMap(["SetupActions", "ColorActions"],
            {
                "green" : self.use,
                "red"   : self.exit,
                "yellow": self.refresh,
                #"blue"  : XXXXXX,
                "ok"    : self.ok,
                "cancel": self.exit
            })
        self.title = title
        self.returnFile = selectFiles
        self.onLayoutFinish.append(self.layoutFinished)
        self.onClose.append(self.__onClose)

    def mkdir(newdir):
        """ Wrapper for the os.mkdir function
            returns status instead of raising exception
        """
        try:
            os_mkdir(newdir)
            sts = True
            msg = _('%s directory has been created.') % newdir
        except:
            sts = False
            msg = _('Error creating %s directory.') % newdir
            printExc()
        return sts,msg
    
    def __onClose(self):
        self.onClose.remove(self.__onClose)
        self.onLayoutFinish.remove(self.layoutFinished)

    def layoutFinished(self):
        self.setTitle(_(self.title))
        self.currDirChanged()

    def currDirChanged(self):
        self["curr_dir"].setText(_(self.getCurrentDirectory()))
        
    def getCurrentDirectory(self):
        currDir = self["filelist"].getCurrentDirectory()
        if currDir and os_path.isdir( currDir ):
            return currDir
        else:
            return "/"

    def use(self):
        if self['filelist'].getCurrent()[0][1] == True: #nie da sie zainstalowac katalogu
          return
        try:
            print("DirectorySelectorWidget: selected file '%s'" % (self.getCurrentDirectory() + self['filelist'].getCurrent()[0][0]))
            self.close( self.getCurrentDirectory() + self['filelist'].getCurrent()[0][0] )
        except:
            print("DirectorySelectorWidget: no file in %s selected!!!" % ( self.getCurrentDirectory() ))

    def exit(self):
        self.close(None)

    def ok(self):
        if self.filelist.canDescent():
            self.filelist.descent()
        self.currDirChanged()

    def refresh(self):
        self["filelist"].refresh()

    def IsValidFileName(name, NAME_MAX=255):
        prohibited_characters = ['/', "\000", '\\', ':', '*', '<', '>', '|', '"']
        if isinstance(name, basestring) and (1 <= len(name) <= NAME_MAX):
            for it in name:
                if it in prohibited_characters:
                    return False
            return True
        return False
