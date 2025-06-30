# -*- coding: utf-8 -*-

# UserSkin, based on AtileHD concept by schomi & plnick
#
# maintainer: j00zek
#
# extension for openpli, all skins, descriptions, bar selections and other @j00zek 2014/2015
# Uszanuj czyjąś pracę i NIE przywłaszczaj sobie autorstwa!

#This plugin is free software, you are allowed to
#modify it (if you keep the license),
#but you are not allowed to distribute/publish
#it without source code (this version and your modifications).
#This means you also have to distribute
#source code of your modifications.
from __future__ import absolute_import #zmiana strategii ladowanie modulow w py2 z relative na absolute jak w py3

from Plugins.Extensions.UserSkin.debug import printDEBUG
from Plugins.Extensions.UserSkin.inits import *
from Plugins.Extensions.UserSkin.translate import _

from Components.ActionMap import ActionMap

from Components.config import *
from Components.Label import Label
from Components.Pixmap import Pixmap
from Components.Sources.List import List
from Plugins.Plugin import PluginDescriptor
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Tools.Directories import resolveFilename, pathExists, SCOPE_SKIN, SCOPE_PLUGINS
from Tools.LoadPixmap import LoadPixmap
#from Tools import Notifications
#import shutil
#import re
from os import path, remove

from sys import version_info
PyMajorVersion = version_info.major
if PyMajorVersion > 2:
    from importlib import reload

if path.exists('/etc/enigma2/skinModified'):        
    try: remove('/etc/enigma2/skinModified')
    except Exception: pass
if path.exists('/etc/enigma2/dvbappHungMarker'):        
    try: 
        remove('/etc/enigma2/dvbappHungMarker')
        with open ('/tmp/safeMode.log', 'a') as f:
            f.write('dvbapp restarted successfully :)')
            f.close()
    except Exception: pass

def Plugins(**kwargs):
    return [PluginDescriptor(name=_("UserSkin Setup"), description=_("Personalize your Skin"), where = PluginDescriptor.WHERE_MENU, fnc=menu)]

def menu(menuid, **kwargs):
    if menuid == "vtimain" or menuid == "system":
        if path.exists('/usr/share/enigma2/%s/allScreens' % CurrentSkinName): 
            return [(_("Setup - UserSkin") + " " + CurrentSkinName, main, "UserSkin_Menu", 40)]
    return []

def main(session, **kwargs):
    printDEBUG("Opening UserSkin%s menu ..." % UserSkinInfo)
    skinHistory, skinUpdate, skinAddOns, skinComponents = readSkinConfig()
    if skinHistory or skinUpdate or skinAddOns or skinComponents:
        session.open(UserSkin_Menu)
    else:
        #from skinconfig import UserSkin_Config
        #session.open(UserSkin_Config)
        import Plugins.Extensions.UserSkin.skinconfig
        reload(Plugins.Extensions.UserSkin.skinconfig)
        session.open(Plugins.Extensions.UserSkin.skinconfig.UserSkin_Config)

def readSkinConfig():
    skinHistory = False
    skinUpdate = False
    skinAddOns = False
    skinComponents = False
    if pathExists("%s%s" % (SkinPath,'skin.config')):
        with open("%s%s" % (SkinPath,'skin.config'), 'r') as cf:
            for cfg in cf:
                if cfg[:8] == "history=":
                    skinHistory = True
                if cfg[:8] == "skinurl=":
                    skinUpdate = True
                if cfg[:7] == "addons=":
                    skinAddOns = True
                if cfg[:11] == "components=":
                    skinComponents = True
    return skinHistory, skinUpdate, skinAddOns, skinComponents
  
class UserSkin_Menu(Screen):
        skin = """
<screen position="center,center" size="660,320">
        <widget source="list" render="Listbox" position="0,0" size="660,320" scrollbarMode="showOnDemand">
                <convert type="TemplatedMultiContent">
                        {"template": [
                                MultiContentEntryPixmapAlphaTest(pos = (12, 2), size = (40, 40), png = 0),
                                MultiContentEntryText(pos = (58, 2), size = (600, 40), font=0, flags = RT_HALIGN_LEFT|RT_VALIGN_CENTER, text = 1),
                                ],
                                "fonts": [gFont("Regular", 24)],
                                "itemHeight": 44
                        }
                </convert>
        </widget>
</screen>"""

        def __init__(self, session):
                Screen.__init__(self, session)
                self.setup_title = _("UserSkinMenu")
                Screen.setTitle(self, self.setup_title)
                self["list"] = List()
                self["setupActions"] = ActionMap(["SetupActions", "MenuActions"],
                {
                        "cancel": self.quit,
                        "ok": self.openSelected,
                        "menu": self.quit,
                }, -2)
                self.setTitle(_("UserSkin menu %s") % UserSkinInfo)
                self.createsetup()

        def createsetup(self):
                skinHistory, skinUpdate, skinAddOns, skinComponents = readSkinConfig()
                l = [(self.buildListEntry(_("Skin personalization"), "config.png",'config'))]
                
                if 0:
                    if pathExists(resolveFilename(SCOPE_PLUGINS,'Extensions/MiniTVUserSkinMaker')):
                        l.append(self.buildListEntry(_("miniTV skin creator"), "lcd.png",'LCDskin'))
                    else:
                        try:
                            from enigma import getDesktop
                            if getDesktop(1).size().width() > 132:
                                l.append(self.buildListEntry(_("Install miniTV skin creator"), "lcd.png",'LCDskinInstall'))
                            else:
                                l.append(self.buildListEntry(_("LCD/VFD too small to use miniTV skin creator"), "lcd.png",'fakeParam'))
                        except Exception:
                            pass
                    
                if skinUpdate:
                    l.append(self.buildListEntry(_("Update main skin"), "skin.png",'getskin')),
                if skinAddOns:
                    l.append(self.buildListEntry(_("Download addons"), "addon.png",'getaddons'))
                   
                #l.append(self.buildListEntry(_("Delete addons"), "remove.png",'delete_addons')),

                if skinComponents:
                    l.append(self.buildListEntry(_("Download additional Components/plugins"), "plugin.png",'getcomponents'))

                #l.append(self.buildListEntry(_("List loaded screens"), "import.png",'ListScreens')),

                if skinHistory:
                    l.append(self.buildListEntry(_("History of changes"), "history.png",'history')),
                #l.append(self.buildListEntry(_("Import foreign skin"), "import.png",'importskin')),
                l.append(self.buildListEntry(_("About"), "about.png",'about')),
                self["list"].list = l

        def buildListEntry(self, description, image, optionname):
                pixmap = LoadPixmap(getPixmapPath(image))
                return((pixmap, description, optionname))

        def refresh(self):
            index = self["list"].getIndex()
            self.createsetup()
            if index is not None and len(self["list"].list) > index:
                self["list"].setIndex(index)
            else:
                self["list"].setIndex(0)

        def rebootQuestion(self):
            def rebootQuestionAnswered(ret):
                if ret:
                    from enigma import quitMainloop
                    quitMainloop(3)
                    self.quit()
                return
            if pathExists("/tmp/.rebootGUI"):
                self.session.openWithCallback(rebootQuestionAnswered, MessageBox,_("Restart GUI now?"),  type = MessageBox.TYPE_YESNO, timeout = 10, default = False)
          
          
        def openSelected(self):
            selected = str(self["list"].getCurrent()[2])
            if selected == 'about':
                from Plugins.Extensions.UserSkin.about import UserSkin_About
                self.session.openWithCallback(self.refresh,UserSkin_About)
                return
            elif selected == 'config':
                #from skinconfig import UserSkin_Config
                #self.session.openWithCallback(self.quit,UserSkin_Config)
                import Plugins.Extensions.UserSkin.skinconfig
                reload(skinconfig)
                session.open(skinconfig.UserSkin_Config)
                return
            elif selected == 'LCDskin':
                from Plugins.Extensions.MiniTVUserSkinMaker.miniTVskinner import miniTVskinnerInitiator
                self.runLCDskin(retDict = None, initRun = True)
                return
            elif selected == 'LCDskinInstall':
                from Plugins.Extensions.UserSkin.myComponents import UserSkinconsole
                runlist = []
                runlist.append( ('opkg update') )
                runlist.append( ('opkg install enigma2-plugin-extensions--j00zeks-minitvuserskinmaker') )
                self.session.openWithCallback(self.refresh, UserSkinconsole, title = _("Installing  miniTV skin creator"), cmdlist = runlist)
                self.refresh()
                return
            elif selected == 'ListScreens':
                from Plugins.Extensions.UserSkin.ScreensLister import ScreensLister
                self.session.openWithCallback(self.doNothing,ScreensLister)
                return
            elif selected == 'getaddons':
                from Plugins.Extensions.UserSkin.myComponents import myMenu
                self.session.openWithCallback(self.refresh, myMenu, MenuFolder = '%sscripts' % PluginPath, MenuFile = '_Getaddons', MenuTitle = _("Download addons"))
                return
            elif selected == 'delete_addons':
                from Plugins.Extensions.UserSkin.myComponents import myMenu
                self.session.openWithCallback(self.refresh, myMenu, MenuFolder = '%sscripts' % PluginPath, MenuFile = '_Deleteaddons', MenuTitle = _("Delete addons"))
                return
            elif selected == 'getcomponents':
                from Plugins.Extensions.UserSkin.myComponents import myMenu
                self.session.openWithCallback(self.rebootQuestion, myMenu, MenuFolder = '%sscripts' % PluginPath, MenuFile = '_Getcomponents', MenuTitle = _("Download additional Components/plugins"))
                return
            elif selected == 'importskin':
                from Plugins.Extensions.UserSkin.myComponents import myMenu
                self.session.openWithCallback(self.refresh, myMenu, MenuFolder = '%sImportSkinScripts' % PluginPath, MenuFile = '_Skins2Import', MenuTitle = _("Import foreign skin"))
                return
            elif selected == 'getskin':
                def goUpdate(ret):
                    if ret is True:
                        from Plugins.Extensions.UserSkin.myComponents import UserSkinconsole
                        runlist = []
                        runlist.append( ('chmod 755 %sscripts/SkinUpdate.sh' % PluginPath) )
                        runlist.append( ('%sscripts/SkinUpdate.sh %s' % (PluginPath,SkinPath)) )
                        self.session.openWithCallback(self.rebootQuestion, UserSkinconsole, title = _("Updating skin"), cmdlist = runlist)
                    return
                    
                self.session.openWithCallback(goUpdate, MessageBox,_("Do you want to update skin?"),  type = MessageBox.TYPE_YESNO, timeout = 10, default = False)
                return
            elif selected == 'history':
                from Plugins.Extensions.UserSkin.myComponents import UserSkinconsole
                self.session.openWithCallback(self.refresh, UserSkinconsole, title = _("History of changes"), cmdlist = [ '%sscripts/SkinHistory.sh %s' % (PluginPath,SkinPath) ])
                return

        def runLCDskin(self, retDict = None, initRun = False):
            #from miniTVskinner import miniTVskinner
            from Plugins.Extensions.MiniTVUserSkinMaker.miniTVskinner import miniTVskinner
            if initRun == True:
                self.session.openWithCallback(self.runLCDskin,miniTVskinner, {} )
            elif retDict is not None and len(retDict) > 0:
                self.session.openWithCallback(self.runLCDskin,miniTVskinner, retDict )
            return
              
        def doNothing(self):
            return
                
        def quit(self):
            self.close()
