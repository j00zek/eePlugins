# -*- coding: utf-8 -*-

# UserSkin, based on AtileHD concept by schomi & plnick
#
# maintainer: j00zek
#
# extension for openpli, all skins, descriptions, bar selections and other @j00zek 2014/2019
# Uszanuj czyjąś pracę i NIE przywłaszczaj sobie autorstwa!

# This plugin is free software, you are allowed to
# modify it (if you keep the license),
# but you are not allowed to distribute/publish
# it without source code (this version and your modifications).
# This means you also have to distribute
# source code of your modifications.
from __future__ import absolute_import #zmiana strategii ladowanie modulow w py2 z relative na absolute jak w py3

DBG = True
FullDBG = True

from Plugins.Extensions.UserSkin.debug import printDEBUG
from Plugins.Extensions.UserSkin.inits import *
from Plugins.Extensions.UserSkin.myComponents import UserSkinToolSet
from Plugins.Extensions.UserSkin.translate import _
from Plugins.Extensions.UserSkin.j00zekFileList import FileList

from Components.ActionMap import ActionMap
from Components.config import *
from Components.ConfigList import ConfigListScreen
from Components.j00zekComponents import isImageType, getImageType
from Components.j00zekModHex2strColor import Hex2strColor
from Components.Label import Label
from Components.Pixmap import Pixmap
from Components.Sources.List import List
from Components.Sources.StaticText import StaticText
from enigma import ePicLoad, eTimer, getDesktop
from Plugins.Plugin import PluginDescriptor
from Screens.ChoiceBox import ChoiceBox
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Screens.Standby import TryQuitMainloop
from Tools.Directories import *
from Tools.LoadPixmap import LoadPixmap
from Tools import Notifications
#system imports
from os import listdir, remove, rename, system, path, symlink, chdir, rmdir, mkdir, walk
import os
import shutil
import re
try:
    import requests
except Exception:
    os.system('opkg update;opkg install python3-requests') #openPLi doesn't have it installed
    
from sys import version_info
PyMajorVersion = version_info.major

if PyMajorVersion >= 3:
    from urllib.request import urlretrieve as urllib_urlretrieve
else: #py2
    from urllib import urlretrieve as urllib_urlretrieve

import warnings
warnings.filterwarnings('ignore', message='Unverified HTTPS request')

#UserSkin permanent configs
config.plugins.UserSkin = ConfigSubsection()
config.plugins.UserSkin.refreshInterval = ConfigNumber(default=30) #in minutes
config.plugins.UserSkin.separator = NoSave(ConfigNothing())
def clearCache():
    with open("/proc/sys/vm/drop_caches", "w") as f: f.write("1\n")

def isSlowCPU():
    fc=''
    ret=False
    with open('/proc/cpuinfo', 'r') as f:
        for fc in f:
            if fc.startswith('bogomips') and fc.find(':') > 0 :
                if int(float(fc.split(':')[1].strip())) < 400:
                    ret = True
                break
        f.close()
    return ret

if isSlowCPU() == False:
    config.plugins.UserSkin.jpgPreview = ConfigYesNo(default = True)
else:
    config.plugins.UserSkin.jpgPreview = ConfigYesNo(default = False)

config.plugins.UserSkin.SafeMode = ConfigYesNo(default = True)

def getTunerName():
    def readCFGline(CFGfile):
        CFGline = 'unknown'
        with open(CFGfile, 'r') as file:
            CFGline = file.readline().strip()
            file.close()
        return CFGline
    if path.exists('/proc/stb/info/vumodel') and not path.exists('/proc/stb/info/boxtype'):
        myName = readCFGline('/proc/stb/info/vumodel')
    elif path.exists('/proc/stb/info/boxtype'):
        myName = readCFGline('/proc/stb/info/boxtype')
    else:
        myName = 'unknown'
    return myName.lower()

def vtiLCDskins( skinlist = [] ):
    def find(arg, dirname, names):
        for x in names:
            if x.startswith('skin_vfd') and x.endswith('.xml') and not x.startswith('skin_vfd_HMR_'):
                if dirname != myRoot:
                    subdir = dirname[len(myRoot):]
                    skinname = subdir + 'vfd_skin/' + x
                else:
                    skinname = 'vfd_skin/' + x
                skinlist.append(( skinname, "VTI-%s" % _(skinname[len('skin_vfd'):-4].replace("_", " ")) ))
    myRoot = '/usr/share/enigma2/vfd_skin'
    if path.exists(myRoot):
        path.walk(myRoot, find, '')

    try: skinlist.sort(key=lambda t : tuple(str(t[0]).lower()))
    except Exception: skinlist.sort()
    
    return skinlist
    
def atvLCDskins( skinlist = [] ):
    myRoot = '/usr/share/enigma2/display/'
    try:
        if path.exists(myRoot):
            for root, dirs, files in walk(myRoot, followlinks=False):
                for subdir in dirs:
                    dir = path.join(root,subdir)
                    if path.exists(path.join(dir,'skin_display.xml')):
                        #skinlist.append(subdir)
                        skinlist.append(( subdir, "ATV-%s" % _(subdir.replace("_", " ")) ))
    except Exception as e:
        if DBG == True: printDEBUG(str(e))

    try: skinlist.sort(key=lambda t : tuple(str(t[0]).lower()))
    except Exception: skinlist.sort()
    
    return [] #skinlist

def homarLCDskins( skinlist = [] , tunerName = getTunerName() ):
    if DBG == True: printDEBUG('homarLCDskins >')
    if path.exists('/usr/share/enigma2/HomarLCDskins/konfiguracja'):
        with open('/usr/share/enigma2/HomarLCDskins/konfiguracja', 'r') as file:
            trybDevelopera = file.read()
            file.close()
            if trybDevelopera.find('trybDevelopera=On') > -1:
                tunerName = 'all'
            elif trybDevelopera.find('trybDevelopera=duo4k') > -1:
                tunerName = 'duo4k'
            elif trybDevelopera.find('trybDevelopera=duo4kse') > -1:
                tunerName = 'duo4kse'

    if tunerName == 'all':
        subRoot='HomarLCDskins/'
    else:
        subRoot='HomarLCDskins/model.%s/' % tunerName.replace('duo4k', 'solo4k')
    myRoot = '/usr/share/enigma2/%s' % subRoot
    if DBG == True: printDEBUG('myRoot = %s' % myRoot)
    try:
        if path.exists(myRoot):
            if DBG == True: printDEBUG('myRoot exists')
            for root, dirs, filenames in walk(myRoot, followlinks=False):
                if DBG == True: printDEBUG(str(dirs))
                if len(dirs) == 0:
                    for x in filenames:
                        if DBG: printDEBUG("\t skinname='%s'" % x)
                        if x.startswith('skin_LCD_HMR') and x.endswith('.xml'):
                            if FullDBG: printDEBUG("\t dirname ='%s', skinname='%s'" % (myRoot, x))
                            skinname = path.join(subRoot,x)
                            if FullDBG: printDEBUG("homarLCDskins skinname'%s'" % (skinname))
                            if tunerName == 'duo4k':
                                skinlist.append(( skinname, _(x[len('skin_LCD_'):-4].replace("_", " ").replace('solo4k', 'duo4k').replace('SOLO4K', 'DUO4K')) ))
                            elif tunerName == 'duo4kse':
                                skinlist.append(( skinname, _(x[len('skin_LCD_'):-4].replace("_", " ").replace('solo4k', 'duo4kse').replace('SOLO4K', 'DUO4KSE')) ))
                            else:
                                skinlist.append(( skinname, _(x[len('skin_LCD_'):-4].replace("_", " ")) ))
                else:
                    for subdir in dirs:
                        dirname = path.join(root,subdir)
                        if DBG == True: printDEBUG(dirname)
                        __, __, filenames = next(walk(dirname), (None, None, []))
                        for x in filenames:
                            if DBG: printDEBUG("\t skinname='%s'" % x)
                            if x.startswith('skin_LCD_HMR') and x.endswith('.xml'):
                                if FullDBG: printDEBUG("\t dirname ='%s', skinname='%s'" % (dirname, x))
                                if dirname != myRoot:
                                    skinname = path.join(subRoot,subdir,x)
                                else:
                                    skinname = path.join(subRoot,x)
                                if FullDBG: printDEBUG("homarLCDskins skinname'%s'" % (skinname))
                                if tunerName == 'duo4k':
                                    skinlist.append(( skinname, _(x[len('skin_LCD_'):-4].replace("_", " ").replace('solo4k', 'duo4k').replace('SOLO4K', 'DUO4K')) ))
                                elif tunerName == 'duo4kse':
                                    skinlist.append(( skinname, _(x[len('skin_LCD_'):-4].replace("_", " ").replace('solo4k', 'duo4kse').replace('SOLO4K', 'DUO4KSE')) ))
                                else:
                                    skinlist.append(( skinname, _(x[len('skin_LCD_'):-4].replace("_", " ")) ))
    except Exception as e:
        if DBG == True: printDEBUG(str(e))

    try: skinlist.sort(key=lambda t : tuple(str(t[0]).lower()))
    except Exception: skinlist.sort()
    
    return skinlist
    
def homarLCDskinsTODEL( skinlist = [] , tunerName = getTunerName() ):
    if DBG == True: printDEBUG('homarLCDskins() >>>')
    def find(arg, dirname, names):
        for x in names:
            if x.startswith('skin_LCD_HMR') and x.endswith('.xml'):
                if FullDBG: printDEBUG("\t dirname ='%s', skinname='%s'" % (dirname, x))
                if dirname != myRoot:
                    subdir = dirname[len(myRoot):]
                    skinname = path.join(subRoot,subdir,x)
                else:
                    skinname = path.join(subRoot,x)
                if FullDBG: printDEBUG("homarLCDskins skinname'%s'" % (skinname))
                if tunerName == 'duo4k':
                    skinlist.append(( skinname, _(x[len('skin_LCD_'):-4].replace("_", " ").replace('solo4k', 'duo4k').replace('SOLO4K', 'DUO4K')) ))
                elif tunerName == 'duo4kse':
                    skinlist.append(( skinname, _(x[len('skin_LCD_'):-4].replace("_", " ").replace('solo4k', 'duo4kse').replace('SOLO4K', 'DUO4KSE')) ))
                else:
                    skinlist.append(( skinname, _(x[len('skin_LCD_'):-4].replace("_", " ")) ))
    
    if path.exists('/usr/share/enigma2/HomarLCDskins/konfiguracja'):
        with open('/usr/share/enigma2/HomarLCDskins/konfiguracja', 'r') as file:
            trybDevelopera = file.read()
            file.close()
            if trybDevelopera.find('trybDevelopera=On') > -1:
                tunerName = 'all'
            elif trybDevelopera.find('trybDevelopera=duo4k') > -1:
                tunerName = 'duo4k'
            elif trybDevelopera.find('trybDevelopera=duo4kse') > -1:
                tunerName = 'duo4kse'
    
    if tunerName == 'all':
        subRoot='HomarLCDskins/'
    else:
        subRoot='HomarLCDskins/model.%s/' % tunerName.replace('duo4k', 'solo4k')
    myRoot = '/usr/share/enigma2/%s' % subRoot
    
    if DBG == True: printDEBUG("homarLCDskins selected tuner='%s', myRoot='%s'" % (tunerName, myRoot))
    if path.exists(myRoot):
        path.walk(myRoot, find, '')
    else:
        skinlist.append(( 'HomarLCDskinsFromOPKG', _('Homar LCD skins from opkg') ))

    try: skinlist.sort(key=lambda t : tuple(str(t[0]).lower()))
    except Exception: skinlist.sort()
    
    return skinlist

def processInfo(myInfoFile):
    if DBG == True: printDEBUG('processInfo(%s)' % myInfoFile)
    info = ''
    hasLangDef = False
    if path.exists(myInfoFile):
        with open(myInfoFile, 'r') as f:
            for line in f:
                line = line.strip()
                if line == '#Lang:%s' % currLang.upper():
                    info = ''
                    hasLangDef = True
                elif hasLangDef and line == '#Lang:':
                    break
                elif line.startswith('#'):
                    continue
                else:
                    index = 0
                    while line.find('c(#') != -1:
                        HexColor = line.split('c(#', 2)[1]
                        HexColor = HexColor.split(')', 2)[0]
                        try:
                            if FullDBG == True: printDEBUG('\t HexColor="%s"' % '0x' + HexColor)
                            hex_int = int('0x' + HexColor, 16)
                            if FullDBG == True: printDEBUG('\t hex_int="%s"' % hex_int)
                            colorInHex = Hex2strColor(hex_int)
                            if FullDBG == True: printDEBUG('\t colorInHex="%s"' % colorInHex)
                        except Exception as e:
                            if DBG == True: printDEBUG('\t exception: %s' % str(e))
                            colorInHex = HexColor
                        line = line.replace('c(#' + HexColor + ')', colorInHex) #Hex2strColor(0x00ffcc00)
                        index += 1
                        if index == 10:
                            break
                    info += line + '\n'
    if FullDBG == True: printDEBUG('\t info:\n"%s"' % info)
    return info.strip()

def downloadPage(webURL, webFileName):
    retStatus = False
    try:
        HEADERS = { 'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:88.0) Gecko/20100101 Firefox/88.0', 
                    'Accept-Charset': 'utf-8', 
                    'Content-Type': 'text/html; charset=utf-8'
                    }
        resp = requests.get(webURL, headers=HEADERS, timeout=5)
        webContent = resp.content
        webHeader = resp.headers
        printDEBUG("webHeader: %s" % resp.headers )
        if webContent != '':
            with open(webFileName, 'wb') as (f):
                f.write(webContent)
                f.close()
            retStatus = True
    except Exception as e:
        printDEBUG("EXCEPTION '%s' in downloadPage() for %s" % (str(e), webURL) )
        webContent = ''
    
    return retStatus

class UserSkin_Config(Screen, ConfigListScreen):
    skin = """
  <screen name="UserSkin_Config" position="82,124" size="1101,376" title="UserSkin Setup" backgroundColor="transparent" flags="wfNoBorder">
    <eLabel position="7,2" size="1091,372" zPosition="-15" backgroundColor="#20000000" />
    <eLabel position="4,51" size="664,238" zPosition="-10" backgroundColor="#20606060" />
    <eLabel position="672,51" size="410,237" zPosition="-10" backgroundColor="#20606060" />
    <eLabel position="6,302" size="240,55" zPosition="-10" backgroundColor="#20b81c46" />
    <eLabel position="284,302" size="240,55" zPosition="-10" backgroundColor="#20009f3c" />
    <eLabel position="564,302" size="240,56" zPosition="-10" backgroundColor="#209ca81b" />
    <eLabel position="843,302" size="240,55" zPosition="-10" backgroundColor="#202673ec" />
    <widget source="Title" render="Label" position="2,4" size="889,43" font="Regular;35" foregroundColor="#00ffffff" backgroundColor="#004e4e4e" transparent="1" />
    <widget name="config" position="6,55" size="657,226" scrollbarMode="showOnDemand" transparent="1" />
    <widget name="Picture" position="676,56" size="400,225" alphatest="blend" />
    <widget name="PreviewInfo" position="676,575" size="400,225" font="Regular;25" foregroundColor="#00ffeedd" backgroundColor="#004e4e4e" transparent="1" />
    <widget name="key_red" position="18,316" size="210,25" zPosition="1" font="Regular;20" halign="left" foregroundColor="#00ffffff" backgroundColor="#20b81c46" transparent="1" />
    <widget name="key_green" position="299,317" size="210,25" zPosition="1" font="Regular;20" halign="left" foregroundColor="#00ffffff" backgroundColor="#20009f3c" transparent="1" />
    <widget name="key_yellow" position="578,317" size="210,25" zPosition="1" font="Regular;20" halign="left" foregroundColor="#00ffffff" backgroundColor="#209ca81b" transparent="1" />
    <widget name="key_blue" position="854,318" size="210,25" zPosition="1" font="Regular;20" halign="left" foregroundColor="#00ffffff" backgroundColor="#202673ec" transparent="1" />
  </screen>
"""

    skin_lines = []
    changed_screens = False
        
    def __init__(self, session, args = 0):
        if DBG == True: printDEBUG('__init__ >>>')
        self.session = session
        Screen.__init__(self, session)
        self.UserSkinToolSet = UserSkinToolSet()
        
        myTitle=_("UserSkin Setup %s") % UserSkinInfo
        self.setTitle(myTitle)
        try:
            self["title"]=StaticText(myTitle)
        except:
            pass
            
        self.currentSkin = CurrentSkinName
        printDEBUG("UserSkinInfo=%s, Image=%s, SkinPath=%s, skin=%s, currentSkin=%s" % (UserSkinInfo, getImageType(), SkinPath, config.skin.primary_skin.value, self.currentSkin))
        if self.currentSkin != '':
                self.currentSkin = '_' + self.currentSkin # default_skin = '', others '_skinname', used later
                
        if path.exists(SkinPath):
            if DBG == True: printDEBUG('#### initializing SUBDIRS ###')
            #### initializing SUBDIRS ###
            for folder in ("allBars", "allColors", "allFonts", "allInfos", "allPreviews", "allScreens", "UserSkin_Selections", 'allMiniTVskins', 'allButtons', 'allAnimatedButtons'):
                if not path.exists(SkinPath + folder):
                    mkdir(SkinPath + folder)
            
#### initializing VFD/LCD skins ###
            tunersMappingDict = {}
            if getDesktop(1).size().width() >= 220:
                self.desktopType = 'lcd'
            else:
                self.desktopType = 'vfd'
            if DBG == True: printDEBUG('#### initializing %s skins ###' % self.desktopType.upper() )
            self.LCDscreensList = []
            self.LCDLinuxEnabled = False
            if path.exists('/usr/lib/enigma2/python/Plugins/Extensions/LCDlinux') or path.exists('/usr/lib/enigma2/python/Plugins/Extensions/LCD4linux'):
                self.LCDscreensList.append(("LCDLinux", "LCDLinux"))
                if path.exists('/etc/enigma2/lcd4config'):
                    with open('/etc/enigma2/lcd4config','r') as f:
                        if 'config.Enable=true' in f.read():
                            self.LCDLinuxEnabled = True
                        f.close()
            
            if 1:
                filterVFDskins4model = False
                tunerName = getTunerName()
                mappedTunerName = tunersMappingDict.get(tunerName, tunerName)
            
                if tunerName != 'unknown':
                    for f in sorted(listdir(SkinPath + "allMiniTVskins/"), key=str.lower):
                        if f.startswith('skin_') and f.endswith('.xml') and f.lower().find(mappedTunerName) > -1:
                            filterVFDskins4model = True
                            break

                for f in sorted(listdir(SkinPath + "allMiniTVskins/"), key=str.lower):
                    if f.startswith('skin_') and f.endswith('.xml') and f.lower().find(self.desktopType) > -1:
                        if FullDBG: printDEBUG( path.join('BlackHarmony/allMiniTVskins/',f) )
                        if filterVFDskins4model:
                            if f.lower().find(mappedTunerName) > -1:
                                if mappedTunerName == tunerName:
                                    self.LCDscreensList.append(( path.join('BlackHarmony/allMiniTVskins/',f), _(f[5:-4].replace("_", " ")) ))
                                else:
                                    self.LCDscreensList.append(( path.join('BlackHarmony/allMiniTVskins/',f), mappedTunerName + ': ' + _(f[5:-4].replace("_", " ")) ))
                        else:
                            self.LCDscreensList.append(( path.join('BlackHarmony/allMiniTVskins/',f), _(f[5:-4].replace("_", " ")) ))
                          
                self.LCDscreensList.extend( atvLCDskins() )
                self.LCDscreensList.extend( vtiLCDskins() )
                if  self.desktopType == 'lcd' and tunerName != 'unknown':
                    self.LCDscreensList.extend( homarLCDskins() )
            
                self.LCDscreensList = list(set(self.LCDscreensList))
                try: self.LCDscreensList.sort(key=lambda t : tuple(str(t[0]).lower()))
                except Exception: self.LCDscreensList.sort()
            
            self.LCDscreensList.insert(0,("system", "system"))
            config.plugins.UserSkin.LCDmode = ConfigSelection(default="system", choices = self.LCDscreensList)
            
            if self.LCDLinuxEnabled == True:
                config.plugins.UserSkin.LCDmode.value = 'LCDLinux'
              
#### initializing FONTS ###
            if DBG == True: printDEBUG('#### initializing FONTS ###')
            if not path.exists(SkinPath + "allFonts/font_default.xml"):
                with open(SkinPath + 'allFonts/font_default.xml', "w") as f:
                    f.write("<skin>\n" + self.readXMLfile(SkinPath + 'skin.xml' , 'fonts') + "</skin>\n")
                    f.close()
            mylist = []
            for f in sorted(listdir(SkinPath + "allFonts/"), key=str.lower):
                if f.startswith('font_') and f.endswith('.xml'):
                    mylist.append(( f, _(f[5:-4].replace("_", " ")) ))
            if path.exists( SkinPath + "skin_user_header.xml" ):
                self.myUserSkin_font = NoSave(ConfigSelection(
                                          default = path.basename(path.realpath( SkinPath + "skin_user_header.xml" )),
                                          choices = mylist) )
            else:
                self.myUserSkin_font = NoSave(ConfigSelection(default = 'font_default.xml', choices = mylist))           
#### initializing LCD COLORS ###
            if DBG == True: printDEBUG('#### initializing LCD COLORS ###')
            self.LCDcolorsList = [("default", _("default"))]
            if self.desktopType == 'lcd':
                for f in sorted(listdir(SkinPath + "allColors/"), key=str.lower):
                    if f.startswith('LCD_colors_') and f.endswith('.xml'):
                        #if DBG == True: printDEBUG('\t f="%s"' % SkinPath + "allColors/" + f)
                        self.LCDcolorsList.append(( SkinPath + "allColors/" + f, _(f[11:-4].replace("_", " ")) ))
                if path.exists("/usr/share/enigma2/HomarLCDskins/allColors/"):
                    for f in sorted(listdir("/usr/share/enigma2/HomarLCDskins/allColors/"), key=str.lower):
                        if f.startswith('LCD_colors_') and f.endswith('.xml'):
                            self.LCDcolorsList.append(( "/usr/share/enigma2/HomarLCDskins/allColors/" + f, _(f[11:-4].replace("_", " ")) ))
            config.plugins.UserSkin.LCDcolors = ConfigSelection(default="default", choices = self.LCDcolorsList)
            if config.plugins.UserSkin.LCDcolors.value == 'HomarLCDskinsFromOPKG':
                config.plugins.UserSkin.LCDcolors.value = "default"
#### initializing COLORS ###
            if DBG == True: printDEBUG('#### initializing COLORS ###')
            if not path.exists(SkinPath + "allColors/colors_default.xml") or path.getsize(SkinPath + "allColors/colors_default.xml") > 8192:
                printDEBUG("generating colors_default.xml")
                with open(SkinPath + "allColors/colors_default.xml" , "w") as f:
                    f.write("<skin>\n")
                    f.write(self.readXMLfile(SkinPath + 'skin.xml' , 'colors'))
                    f.write(self.readXMLfile(SkinPath + 'skin.xml' , 'windowstyle'))
                    f.write("</skin>\n")
                    f.close()
            mylist = []
            for f in sorted(listdir(SkinPath + "allColors/"), key=str.lower):
                if f.startswith('colors_') and f.endswith('.xml'):
                    mylist.append(( f, _(f[7:-4].replace("_", " ")) ))
            if path.exists(SkinPath + "skin_user_colors.xml"):
                self.myUserSkin_style = NoSave(ConfigSelection(
                                          default = path.basename(path.realpath(SkinPath + "skin_user_colors.xml")),
                                          choices = mylist))
            else:
                self.myUserSkin_style = NoSave(ConfigSelection(default = 'colors_default.xml', choices = mylist))
#### initializing USER BARS ###
            if DBG == True: printDEBUG('#### initializing USER BARS ###')
            mylist = []
            #usedNames = []
            #first directories
            for f in sorted(listdir(SkinPath + "allBars/"), key=str.lower):
                if path.isdir(path.join(SkinPath + "allBars/", f)) and f.startswith('bar_') and f.find('.') > 1:
                    friendly_name = f.split(".", 1)[0]
                    friendly_name = friendly_name[4:].replace("_", " ")
                    mylist.append((f, _(friendly_name)))
                    #usedNames.append(f)
                    if DBG == True: printDEBUG(f)
                
            if len(mylist) == 0:
                mylist.append(("default", _("default") ))
                self.myUserSkin_bar = NoSave(ConfigSelection(default = "default", choices = mylist))
            else:
                if path.exists(SkinPath + 'skin_user_bar'):
                    self.myUserSkin_bar = NoSave(ConfigSelection(
                                        default = path.basename(path.realpath( SkinPath + 'skin_user_bar')),
                                        choices = mylist))
                else:
                    mylist.append(("default", _("default") ))
                    self.myUserSkin_bar = NoSave(ConfigSelection(default = "default", choices = mylist))
#### initializing USER BUTTONS ###
            mylist = []
            if DBG == True: printDEBUG('#### initializing USER BUTTONS ###')
            #if DBG == True: printDEBUG('\t' + SkinPath + "allButtons/")
            for f in sorted(listdir(SkinPath + "allButtons/"), key=str.lower):
                #if DBG == True: printDEBUG('\t f="%s"' % f)
                if path.isdir(path.join(SkinPath + "allButtons/", f)) and f.endswith('.buttons'):
                    friendly_name = f[:-8]
                    mylist.append((f, _(friendly_name)))
                    #if DBG == True: printDEBUG('\t appended=%s' % f)

            if len(mylist) == 0:
                mylist.append(("default", _("default") ))
                self.myUserSkin_buttons = NoSave(ConfigSelection(default = "default", choices = mylist))
            else:
                if path.exists(SkinPath + 'skin_user_buttons'):
                    currDefault = path.basename(path.realpath( SkinPath + 'skin_user_buttons'))
                else:
                    currDefault = "Standard-mixed.buttons"
                self.myUserSkin_buttons = NoSave(ConfigSelection(default = currDefault, choices = mylist))
#### initializing ANIMATED BUTTONS ###
            mylist = []
            mylist.append(("default", _("don't use") ))
            if DBG == True: printDEBUG('#### initializing ANIMATED BUTTONS ###')
            #if DBG == True: printDEBUG('\t' + SkinPath + "allAnimatedButtons/")
            for f in sorted(listdir(SkinPath + "allAnimatedButtons/"), key=str.lower):
                #if DBG == True: printDEBUG('\t f="%s"' % f)
                if path.isdir(path.join(SkinPath + "allAnimatedButtons/", f)):
                    friendly_name = f.replace('_',' ')
                    mylist.append((f, _(friendly_name)))
                    #if DBG == True: printDEBUG('\t appended=%s' % f)

            if path.exists(SkinPath + 'skin_user_animButtons'):
                currDefault = path.basename(path.realpath( SkinPath + 'skin_user_animButtons'))
            else:
                currDefault = "default"
            self.myUserSkin_animButtons = NoSave(ConfigSelection(default = currDefault, choices = mylist))
#### initializing ONOFF SWITCHES ###
            mylist = []
            if DBG == True: printDEBUG('#### initializing ONOFF SWITCHES ###')
            #if DBG == True: printDEBUG('\t' + SkinPath + "allButtons/")
            for f in sorted(listdir(SkinPath + "allOnOffSwitches/"), key=str.lower):
                #if DBG == True: printDEBUG('\t f="%s"' % f)
                if path.isdir(path.join(SkinPath + "allOnOffSwitches/", f)):
                    friendly_name = _(f)
                    mylist.append((f, _(friendly_name)))

            if path.exists(SkinPath + 'skin_user_OnOffSwitches'):
                currDefault = path.basename(path.realpath( SkinPath + 'skin_user_OnOffSwitches'))
            else:
                currDefault = "Standard"
            self.myUserSkin_onoffswitches = NoSave(ConfigSelection(default = currDefault, choices = mylist))
##########################################################################################################3
        if path.exists(SkinPath + "mySkin"):
            self.myUserSkin_active = NoSave(ConfigYesNo(default= True))
        else:
            self.myUserSkin_active = NoSave(ConfigYesNo(default= False))
        self.myUserSkin_fake_entry = NoSave(ConfigNothing())
        self.LackOfFile = ''
        
        if DBG == True: printDEBUG('#### initializing ConfigListScreen ###')
        self.list = []
        ConfigListScreen.__init__(self, self.list, session = self.session, on_change = self.changedEntry)

        if DBG == True: printDEBUG('#### initializing Menu Buttons ###')
        self["key_red"] = Label(_("Cancel"))
        self["key_green"] = Label(_("OK"))
        self["key_yellow"] = Label()
        self["key_blue"] = Label()
        self["setupActions"] = ActionMap(["SetupActions", "ColorActions","MenuActions"],
            {
                "red": self.cancel,
                "green": self.keyOk,
                "yellow": self.keyYellow,
                "blue": self.keyBlue,
                "cancel": self.cancel,
                "ok": self.keyOkbutton,
                "menu": self.keyMenu,
            }, -2)
            
        self["Picture"] = Pixmap()
        self["PreviewInfo"] = StaticText("")
        
        if not self.selectionChanged in self["config"].onSelectionChanged:
            self["config"].onSelectionChanged.append(self.selectionChanged)
#### initializing LCDconfigKey ###        
        if DBG == True: printDEBUG('#### initializing LCDconfigKey ###')
        self.LCDconfigKey = 'none'
        try:
            LCDconfigKey = config.skin.primary_vfdskin.value
            self.LCDconfigKey = 'primary_vfdskin'
        except Exception:
            try:
                self.LCDconfigKey = config.skin.display_skin.value
                self.LCDconfigKey = 'display_skin'
            except Exception:
                clearCache()
                if os.path.exists('/usr/lib/enigma2/python/skin.pyo') and (os.path.exists('/usr/share/enigma2/skin_display.xml') or os.path.exists('/usr/share/enigma2/skin_display.xml.org')):
                    with open('/usr/lib/enigma2/python/skin.pyo', 'rb') as f:
                        if 'skin_display.xml' in f.read():
                            self.LCDconfigKey = 'skin_display.xml'
                        f.close()
                elif os.path.exists('/usr/lib/enigma2/python/skin.pyc') and (os.path.exists('/usr/share/enigma2/skin_display.xml') or os.path.exists('/usr/share/enigma2/skin_display.xml.org')):
                    with open('/usr/lib/enigma2/python/skin.pyc', 'rb') as f:
                        if 'skin_display.xml' in f.read():
                            self.LCDconfigKey = 'skin_display.xml'
                        f.close()
                elif os.path.exists('/usr/lib/enigma2/python/skin.pyo') and (os.path.islink('/usr/share/enigma2/skin_box.xml') or not os.path.isfile('/usr/share/enigma2/skin_box.xml')):
                    with open('/usr/lib/enigma2/python/skin.pyo', 'rb') as f:
                        if 'skin_box.xml' in f.read():
                            self.LCDconfigKey = 'skin_box.xml'
                        f.close()
                elif os.path.exists('/usr/lib/enigma2/python/skin.pyc') and (os.path.islink('/usr/share/enigma2/skin_box.xml') or not os.path.isfile('/usr/share/enigma2/skin_box.xml')):
                    with open('/usr/lib/enigma2/python/skin.pyc', 'rb') as f:
                        if 'skin_box.xml' in f.read():
                            self.LCDconfigKey = 'skin_box.xml'
                        f.close()
                
        if DBG == True: printDEBUG('\t LCDconfigKey="%s"' % self.LCDconfigKey )                
        
        self.createConfigList()
        self.updateEntries = False
        self.LCD_widgets_selected = False
        system('opkg update &' )
        if DBG == True: printDEBUG('__init__  <<< ENDS')

    def createConfigList(self):
        if DBG == True: printDEBUG('self.createConfigList() >>>')
        self.list = []
        self.list.append(getConfigListEntry( '\c00289496' + _("*** Basic settings ***"), config.plugins.UserSkin.separator))
        self.list.append(getConfigListEntry(_("Enable skin personalization:"), self.myUserSkin_active))
        self.list.append(getConfigListEntry(_("Colors:"), self.myUserSkin_style))
        self.list.append(getConfigListEntry(_("Font:"), self.myUserSkin_font))
        self.list.append(getConfigListEntry(_("Selector bar style:"), self.myUserSkin_bar))
        self.list.append(getConfigListEntry(_("Selector buttons style:"), self.myUserSkin_buttons))
        self.list.append(getConfigListEntry(_("Anim buttons (if in skin):"), self.myUserSkin_animButtons))
        self.list.append(getConfigListEntry(_("On/Off switch style:"), self.myUserSkin_onoffswitches))
        if isSlowCPU() == True:
            self.list.append(getConfigListEntry(_("No JPG previews:"), config.plugins.UserSkin.jpgPreview))
        if self.LCDconfigKey != 'none':
            if self.desktopType == 'lcd':
                optionText = _("LCD skin (OK):")
            else:
                optionText = _("VFD skin (OK):")
            self.list.append(getConfigListEntry( optionText, config.plugins.UserSkin.LCDmode) )
            if self.desktopType == 'lcd':
                self.list.append(getConfigListEntry( _("LCD Colors:"), config.plugins.UserSkin.LCDcolors) )
        try:
            self.list.append(getConfigListEntry(""))
            #e2c configuration elements
            from Plugins.SystemPlugins.e2componentsInitiator.setup import buildMlist
            self.list.extend(buildMlist())
        except Exception as e:
            if DBG == True: printDEBUG('Exception %s' % str(e))
        self["config"].list = self.list
        self["config"].l.setList(self.list)
        if self.myUserSkin_active.value:
            self["key_yellow"].setText(_("User skins"))
            if 0: self["key_blue"].setText(_("Extract from skin.xml"))
            else: self["key_blue"].setText(_("About"))
        else:
            self["key_yellow"].setText("")
            self["key_blue"].setText("")

    def changedEntry(self):
        self.updateEntries = True
        if DBG == True: printDEBUG("[skinconfig:changedEntry]")
        try:
            selectedItem = self["config"].getCurrent()
            if len(selectedItem) == 2:
                selectedCFG = selectedItem[1]
                if selectedCFG   == self.myUserSkin_style:   self.setPicture(self.myUserSkin_style.value)
                elif selectedCFG == self.myUserSkin_font:    self.setPicture(self.myUserSkin_font.value)
                elif selectedCFG == self.myUserSkin_bar:     self.setPicture(self.myUserSkin_bar.value)
                elif selectedCFG == self.myUserSkin_buttons: self.setPicture(self.myUserSkin_buttons.value)
                elif selectedCFG == self.myUserSkin_onoffswitches: self.setPicture(self.myUserSkin_onoffswitches.value)
                elif selectedCFG == self.myUserSkin_active:
                    if self.myUserSkin_active.value:
                        self["key_yellow"].setText(_("User skins"))
                    else:
                        self["key_yellow"].setText("")
                elif selectedCFG == config.plugins.UserSkin.LCDcolors: self.setPicture(config.plugins.UserSkin.LCDcolors.value)
        except Exception: pass

    def selectionChanged(self):
        if DBG == True: printDEBUG("[skinconfig:selectionChanged]")
        try:
            selectedItem = self["config"].getCurrent()
            if len(selectedItem) == 2:
                #self.updateEntries = True
                selectedCFG = selectedItem[1]
                if selectedCFG   == self.myUserSkin_style:   self.setPicture(self.myUserSkin_style.value)
                elif selectedCFG == self.myUserSkin_font:    self.setPicture(self.myUserSkin_font.value)
                elif selectedCFG == self.myUserSkin_bar:     self.setPicture(self.myUserSkin_bar.value)
                elif selectedCFG == self.myUserSkin_buttons: self.setPicture(self.myUserSkin_buttons.value)
                elif selectedCFG == self.myUserSkin_onoffswitches: self.setPicture(self.myUserSkin_onoffswitches.value)
                elif selectedCFG == config.plugins.UserSkin.LCDcolors: self.setPicture(config.plugins.UserSkin.LCDcolors.value)
                else:
                    self["Picture"].hide()
                    self["PreviewInfo"].setText('')

        except Exception: pass
            
    def cancel(self):
        if self.updateEntries: #self["config"].isChanged():
            self.session.openWithCallback(self.cancelConfirm, MessageBox, _("Do you really want to cancel?"), MessageBox.TYPE_YESNO, default = False)
        else:
            for x in self["config"].list:
                if len(x) == 2:
                    x[1].cancel()
            if self.changed_screens:
                self.restartGUI()
            else:
                self.close()

    def cancelConfirm(self, result):
        if result is None or result is False:
            printDEBUG("Cancel confirmed.")
        else:
            printDEBUG("Cancel confirmed. Config changes will be lost.")
            for x in self["config"].list:
                if len(x) == 2:
                    x[1].cancel()
            self.close()
                
    def setPicture(self, f):
        if f == '':
            return
        elif f[-4:] == '.xml':
            pic = f[:-4]
        else:
            pic = f
        if DBG == True: printDEBUG("UserSkin.setPicture('%s')" % f )
        if pic.startswith('/'):
            if path.exists(pic.replace('allColors','allPreviews') + '.png'):
                self.UpdatePreviewPicture(pic.replace('allColors','allPreviews') + '.png')
            elif path.exists(pic + '.png'):
                self.UpdatePreviewPicture(pic + '.png')
            else:
                self["Picture"].hide()
        else:
            #check for jpg
            if path.exists(SkinPath + "allPreviews/" + pic + '.jpg'):
                self.UpdatePreviewPicture(SkinPath + "allPreviews/" + pic + '.jpg')
            elif path.exists(SkinPath + "allPreviews/preview_" + pic + '.jpg'):
                self.UpdatePreviewPicture(SkinPath + "allPreviews/preview_" + pic + '.jpg')
            #check for png
            elif path.exists(SkinPath + "allPreviews/" + pic + '.png'):
                self.UpdatePreviewPicture(SkinPath + "allPreviews/" + pic + '.png')
            elif path.exists(SkinPath + "allPreviews/preview_" + pic + '.png'):
                self.UpdatePreviewPicture(SkinPath + "allPreviews/preview_" + pic + '.png')
            else:
                self["Picture"].hide()
          
        infs = f[:-3] + 'txt'
        for inf in (infs, infs.replace('allColors','allInfos') ):
            #if DBG == True: printDEBUG('\t f="%s"' % inf)
            if path.exists(inf):
                self["PreviewInfo"].setText(processInfo(inf))
                break
            else:
                self["PreviewInfo"].setText('')
        
    
    def UpdatePreviewPicture(self, PreviewFileName):
            if DBG == True: printDEBUG("[skinconfig:UpdatePreviewPicture] pic =" + PreviewFileName)
            if isImageType('vuplus') == False: self["Picture"].instance.setScale(1)
            self["Picture"].instance.setPixmap(LoadPixmap(path=PreviewFileName))
            self["Picture"].show()
            
    def keyYellow(self):
        if self.myUserSkin_active.value:
            self.session.openWithCallback(self.UserSkinScreensCB, TreeUserSkinScreens)
        else:
            self["config"].setCurrentIndex(0)

    def LCDskinCB(self,ret):
        if DBG == True: printDEBUG("LCDskinCB >>>")
        def installHomarLCDscreens(ret = False):
            if DBG == True: printDEBUG("installHomarLCDscreens >>>")
            if ret == True:
                os.system('opkg update;opkg install enigma2-plugin-skins--j00zeks-homar;sync')
                self.keyOk()
        if ret:
            if DBG == True: printDEBUG(ret)
            if ret[0] == 'HomarLCDskinsFromOPKG':
                self.session.openWithCallback(installHomarLCDscreens,MessageBox, _("Installation of LCD screens prepared by Homar from opkg will take a minute. Do you want to proceed?"), MessageBox.TYPE_YESNO, default = False)
            else:
                config.plugins.UserSkin.LCDmode.value = ret[1]
                if DBG == True: printDEBUG("config.plugins.UserSkin.LCDmode.value=%s" % config.plugins.UserSkin.LCDmode.value )
        
    def selectFolderCallBack(self, curIndex, newPath):
        if None != newPath:
            self["config"].list[curIndex][1].value = newPath
            self.createConfigList()
            
    def keyOkbutton(self):
        if DBG == True: printDEBUG("keyOkbutton >>>")
        try:
            if self["config"].getCurrent()[1] == config.plugins.UserSkin.LCDmode:
                mySkin = []
                for item in self.LCDscreensList:
                    mySkin.append((item[1] , item[0]))
                self.session.openWithCallback(self.LCDskinCB, ChoiceBox, title = _("Choose LCD skin:"), list = mySkin)
            else:
                self.keyOk()
        except Exception as e:
            if DBG == True: printDEBUG("keyOkbutton() Exception %s" % str(e))
            self.keyOk()
    
    def keyOk(self):
        if self.updateEntries == True or self.changed_screens: #or self["config"].isChanged():
            self.session.openWithCallback(self.keyOkret,MessageBox, _("Do you want to update your skin modification?"), MessageBox.TYPE_YESNO, default = True)
        else:
            self.session.openWithCallback(self.keyOkret,MessageBox, _("Do you want to update your skin modification?"), MessageBox.TYPE_YESNO, default = False)
    def keyOkret(self, ret = False):
        if DBG == True: printDEBUG("keyOkret() >>>")
        if ret == True:
            printDEBUG('self["config"].isChanged()')
            printDEBUG("self.myUserSkin_style.value=" + self.myUserSkin_style.value)
            printDEBUG("self.myUserSkin_bar.value=" + self.myUserSkin_bar.value)
            printDEBUG("self.myUserSkin_buttons.value=" + self.myUserSkin_buttons.value)
            printDEBUG("self.myUserSkin_buttons.value=" + self.myUserSkin_animButtons.value)
            printDEBUG("self.myUserSkin_onoffswitches=" + self.myUserSkin_onoffswitches.value)
            for x in self["config"].list:
                if len(x) == 2:
                    x[1].save()
            configfile.save()
            ################################ SAFE MODE 
            self.UserSkinToolSet.ClearMemory()
            if isImageType('vti') or isImageType('vuplus') or isImageType('openpli-7'):
                system("touch /etc/enigma2/skinModified") #for safety, nicely manage overwrite ;)
            #we change current folder to active skin folder
            chdir(SkinPath)
            #### FONTS
            if path.exists(SkinPath + "skin_user_header.xml") or path.islink(SkinPath + "skin_user_header.xml"):
                remove(SkinPath + "skin_user_header.xml")
            if path.exists(SkinPath + 'allFonts/' + self.myUserSkin_font.value):
                printDEBUG("self.myUserSkin_font.value='%s'" % self.myUserSkin_font.value)
                symlink(SkinPath + 'allFonts/' + self.myUserSkin_font.value, SkinPath + "skin_user_header.xml")
            #### COLORS
            if path.exists(SkinPath + "skin_user_colors.xml") or path.islink(SkinPath + "skin_user_colors.xml"):
                remove(SkinPath + "skin_user_colors.xml")
            if path.exists("allColors/" + self.myUserSkin_style.value):
                symlink(SkinPath +"allColors/" + self.myUserSkin_style.value, SkinPath + "skin_user_colors.xml")
            #### USER BARS
            if path.exists(SkinPath + 'skin_user_bar') or path.islink(SkinPath + 'skin_user_bar'):
                remove(SkinPath + 'skin_user_bar')
            if path.exists(SkinPath + "allBars/" + self.myUserSkin_bar.value):
                symlink(SkinPath + "allBars/" + self.myUserSkin_bar.value , 'skin_user_bar')
                sourcePath = path.join(SkinPath , 'skin_user_bar')
                destFolder = self.myUserSkin_bar.value.split(".", 1)[1]
                destPath = path.join(SkinPath , destFolder)
                printDEBUG("cp -fr %s %s" % (sourcePath,destPath))
                self.UserSkinToolSet.ClearMemory()
                if len(os.listdir(SkinPath + "allBars/" + self.myUserSkin_bar.value)) == 0:
                    pkgName = self.myUserSkin_bar.value.lower().replace('.','-').replace('_','-')
                    system("opkg install --force-reinstall e2-j00zeks-bh-addon-allbars-%s" % pkgName) #instalacja wybranej paczki
                system("cp -fr %s/* %s/" %(sourcePath,destPath)) #for safety, nicely manage overwrite ;)
            
            #### BUTTONS >  self.myUserSkin_buttons.value
            if path.exists(SkinPath + 'skin_user_buttons') or path.islink(SkinPath + 'skin_user_buttons'):
                remove(SkinPath + 'skin_user_buttons')
            if path.exists(SkinPath + "allButtons/" + self.myUserSkin_buttons.value):
                symlink(SkinPath + "allButtons/" + self.myUserSkin_buttons.value , 'skin_user_buttons')
                sourcePath = path.join(SkinPath , 'skin_user_buttons')
                destFolder = self.myUserSkin_buttons.value.split(".", 1)[1]
                destPath = path.join(SkinPath , destFolder)
                printDEBUG("cp -fr %s %s" % (sourcePath,destPath))
                self.UserSkinToolSet.ClearMemory()
                if len(os.listdir(SkinPath + "allButtons/" + self.myUserSkin_buttons.value)) == 0:
                    pkgName = self.myUserSkin_buttons.value.lower().replace('.','-').replace('_','-')
                    system("opkg install --force-reinstall e2-j00zeks-bh-addon-allbuttons-%s" % pkgName) #instalacja wybranej paczki
                system("cp -fr %s/* %s/" %(sourcePath,destPath)) #for safety, nicely manage overwrite ;)
            
            #### ANIM BUTTONS >  self.myUserSkin_animButtons.value
            if path.exists(SkinPath + 'skin_user_animButtons') or path.islink(SkinPath + 'skin_user_animButtons'):
                remove(SkinPath + 'skin_user_animButtons')
            if path.exists(SkinPath + "allAnimatedButtons/" + self.myUserSkin_animButtons.value):
                symlink(SkinPath + "allAnimatedButtons/" + self.myUserSkin_animButtons.value , 'skin_user_animButtons')
                if len(os.listdir(SkinPath + "allAnimatedButtons/" + self.myUserSkin_animButtons.value)) == 0:
                    pkgName = self.myUserSkin_animButtons.value.lower().replace('.','-').replace('_','-')
                    system("opkg install --force-reinstall e2-j00zeks-bh-addon-allanimatedbuttons-%s" % pkgName) #instalacja wybranej paczki
            
            #### ONOFF SWITCHES >  self.myUserSkin_onoffswitches.value
            if path.exists(SkinPath + 'skin_user_OnOffSwitches') or path.islink(SkinPath + 'skin_user_OnOffSwitches'):
                remove(SkinPath + 'skin_user_OnOffSwitches')
            if path.exists(SkinPath + "allOnOffSwitches/" + self.myUserSkin_onoffswitches.value):
                symlink(SkinPath + "allOnOffSwitches/" + self.myUserSkin_onoffswitches.value , 'skin_user_OnOffSwitches')
                sourcePath = path.join(SkinPath , 'allOnOffSwitches', self.myUserSkin_onoffswitches.value)
                destPath = path.join(SkinPath , 'icons')
                printDEBUG("cp -fr %s %s" % (sourcePath,destPath))
                self.UserSkinToolSet.ClearMemory()
                system("cp -fr %s/* %s/" % (sourcePath,destPath)) #for safety, nicely manage overwrite ;)

            #### SCREENS
            if self.myUserSkin_active.value:
                if not path.exists("mySkin") and path.exists("UserSkin_Selections"):
                    try:
                        mkdir("mySkin")
                    except:
                        printDEBUG("symlinking myskin exception")
                        self.UserSkinToolSet.ClearMemory()
                        destPath = path.join(SkinPath , "mySkin")
                        system("mkdir -p %s" % destPath )
            else:
                if path.exists("mySkin"):
                    if path.exists("UserSkin_Selections"):
                        if path.islink("mySkin"):
                            remove("mySkin")
                        else:
                            shutil.rmtree("mySkin")
                    else:
                        rename("mySkin", "UserSkin_Selections")
  
            self.update_user_skin()
            if config.plugins.j00zekCC.iconsANDanims.value == True:
                system('ln -sf /usr/lib/enigma2/python/Components/j00zekSystemModificator.sh /usr/bin/enigma2_pre_start.sh')
            self.restartGUI()
        else:
            self.close()

    def UserSkinScreensCB(self):
        self.changed_screens = True
        self["config"].setCurrentIndex(0)

    def restartGUI(self):
        def restartGUIcb(answer):
            if answer is True:
                self.session.open(TryQuitMainloop, 3)
            else:
                self.close()

        def restartNotOKcb(answer):
            if answer is True:
                self.session.open(TryQuitMainloop, 3)
            else:
                user_skin_file=resolveFilename(SCOPE_CONFIG, 'skin_user' + self.currentSkin + '.xml')
                if path.exists(user_skin_file):
                    remove(user_skin_file)
                self.close()

        myMessage = ''
        if self.LackOfFile != '':
            printDEBUG("Missing components: %s" % self.LackOfFile)
            myMessage += _("Missing components found: %s\n\n") % self.LackOfFile
            myMessage += _("Skin will NOT work properly and GS expected!!!\n\n")
            myMessage += _("Are you sure you want to use it?")
            restartbox = self.session.openWithCallback(restartNotOKcb,MessageBox, myMessage, MessageBox.TYPE_YESNO, default = False)
        else:
            myMessage += _("Restart GUI now?")
            restartbox = self.session.openWithCallback(restartGUIcb,MessageBox, myMessage, MessageBox.TYPE_YESNO, default = False)
        restartbox.setTitle(_("Message"))

    def doNothing(self, ret = None):
        return
      
    def keyMenu(self):
        if path.exists(resolveFilename(SCOPE_PLUGINS, 'SystemPlugins/e2componentsInitiator')):
            from Plugins.SystemPlugins.e2componentsInitiator.setup import e2ComponentsConfig
            try:
                self.session.openWithCallback(self.doNothing, e2ComponentsConfig)
            except Exception as e:
                self.session.openWithCallback(self.doNothing,MessageBox, "EXCEPTION: %s" % str(e), MessageBox.TYPE_INFO, timeout=10) 
      
    def keyBlue(self):
        from Plugins.Extensions.UserSkin.about import UserSkin_About
        self.session.openWithCallback(self.doNothing,UserSkin_About)
        return
        
    def update_user_skin(self):
        def getScreenNames(XMLfilename):
            myPath=path.realpath(XMLfilename)
            if not path.exists(myPath):
                system('rm -f %s' % XMLfilename) 
                return []
            filecontent = ''
            screenNames = []
            with open (XMLfilename, "r") as myFile:
                for line in myFile:
                    filecontent = filecontent + line
                    if line.find('<screen') >= 0:
                        screenNames.append(line.strip())
                        printDEBUG("getScreenNames found %s" % line.strip())
                myFile.close()
            return screenNames
            
        def readScreenContent(XMLfilename, screenSection):
            myPath=path.realpath(XMLfilename)
            if not path.exists(myPath):
                system('rm -f %s' % XMLfilename) 
                return ''
            screencontent = ''
            sectionmarker = False
            with open (XMLfilename, "r") as myFile:
                for line in myFile:
                    if line.find('<skin>') >= 0 or line.find('</skin>') >= 0:
                        continue
                    if line.find('name="%s"' %screenSection) >= 0 and sectionmarker == False:
                        sectionmarker = True
                        continue
                    elif line.find('</screen>') >= 0 and sectionmarker == True:
                        sectionmarker = False
                        break
                    if sectionmarker == True:
                        screencontent = screencontent + line
                myFile.close()
            return screencontent
        
        def readSectionNameContent(XMLfilename, parameterName):
            myPath=path.realpath(XMLfilename)
            if not path.exists(myPath):
                remove(XMLfilename)
                return ''
            ParametersContent = ''
            sectionmarker = False
            with open (XMLfilename, "r") as myFile:
                for line in myFile:
                    if line.find('<skin>') >= 0 or line.find('</skin>') >= 0:
                        continue
                    if line.find('<%s>' % parameterName) >= 0 and sectionmarker == False:
                        sectionmarker = True
                        continue
                    elif line.find('</%s>' % parameterName) >= 0 and sectionmarker == True:
                        sectionmarker = False
                        break
                    if sectionmarker == True:
                        ParametersContent = ParametersContent + line
                myFile.close()
            return ParametersContent
        
        #print("[UserSkin} update_user_skin")
        if path.islink(SkinPath + 'mySkin'):
            remove(SkinPath + 'mySkin')
            mkdir(SkinPath + 'mySkin')       

        
        self.LCD_widgets_selected = False #checking if any self.LCD_widgets_selected = we need to upload to different location
        self.widgets_selected = False #checking if any self._widgets_selected = we need to merge
        
        for f in listdir(SkinPath + "UserSkin_Selections/"):
            if f.lower().find('lcd_widget') > -1:
                self.LCD_widgets_selected = True
                self.widgets_selected = True
            elif f.lower().find('widget') > -1:
                self.widgets_selected = True
            if self.widgets_selected and self.LCD_widgets_selected:
                break
        printDEBUG("self.LCD_widgets_selected = %s, self.widgets_selected = %s" % (str(self.LCD_widgets_selected), str(self.widgets_selected)))
        
        user_skin_file = SkinPath + 'mySkin/skin_user' + self.currentSkin + '.xml' #standardowo zapisujemy gotowa skorke w katalogu BH
        if path.exists(user_skin_file):
            remove(user_skin_file)
            
        if self.myUserSkin_active.value:
            if DBG: printDEBUG("update_user_skin.self.myUserSkin_active.value=True")
            user_skin = ""
            section_parameters = ""
            section_screens = ""
            section_menus = ""
            if FullDBG: printDEBUG("############################################# Initial skin:\n" + user_skin + "\n#############################################\n")        
            if isImageType('vti') == False or isImageType('openatv') == False:
                if path.exists(SkinPath + 'skin_user_header.xml'):
                    printDEBUG("- appending skin_user_header.xml")
                    user_skin = user_skin + self.readXMLfile(SkinPath + 'skin_user_header.xml' , 'fonts')
                if path.exists(SkinPath + 'skin_user_colors.xml'):
                    printDEBUG("- appending skin_user_colors.xml")
                    user_skin = user_skin + self.readXMLfile(SkinPath + 'skin_user_colors.xml' , 'ALLSECTIONS')
            if FullDBG: printDEBUG("############################################# Skin after loading header & colors:\n" + user_skin + "\n#############################################\n")        
            if path.exists(SkinPath + 'UserSkin_Selections'):
                if self.widgets_selected:
                    printDEBUG("mergeScreens mode !!!")
                    # get list of screens in file
                    user_screens = []
                    for f in listdir(SkinPath + "UserSkin_Selections/"):
                        printDEBUG("reading file %smySkin/%s" % (SkinPath,f))
                        section_parameters += readSectionNameContent(SkinPath + "UserSkin_Selections/" + f, 'parameters')
                        section_screens += readSectionNameContent(SkinPath + "UserSkin_Selections/" + f, 'screens')
                        section_menus += readSectionNameContent(SkinPath + "UserSkin_Selections/" + f, 'menus')
                        for screen in getScreenNames(SkinPath + "UserSkin_Selections/" + f):
                            if screen != [] and screen.find('name="') > 0 :
                                screenName = re.findall(' name="([^\s]*)"', screen, re.S)[0]
                                user_screens.append([screenName, screen, f])
                    # get screens content
                    screen_name = ""
                    #if FullDBG: printDEBUG('!!!!! user_screens !!!!!\n' + '\n'.join(user_screens))
                    for screen in sorted(user_screens):
                        if screen[0] != screen_name:
                            if screen_name != "":
                                user_skin = user_skin + "</screen>\n"
                            user_skin = user_skin + screen[1] + "\n"
                            screen_name = screen[0]
                        user_skin = user_skin + readScreenContent(SkinPath + "UserSkin_Selections/" + screen[2], screen[0])
                    user_skin = user_skin + "</screen>\n"
                else:
                    printDEBUG("separate Screens mode !!!")
                    for f in listdir(SkinPath + "UserSkin_Selections/"):
                        printDEBUG( "- appending " + "UserSkin_Selections/" + f )
                        user_skin = user_skin + "<!--" + f + "-->\n" + self.readXMLfile(SkinPath + "UserSkin_Selections/" + f, 'ALLSECTIONS') #zmiana 2024-11-07, 'screen')
                        
            if path.exists('/etc/enigma2/skin_user.xml'): #czyszczenie
                with open ('/etc/enigma2/skin_user.xml', "r") as myFile:
                    fl = myFile.readline()
                    myFile.close()
                    if '<!--UserSkin-->' in fl:
                        remove('/etc/enigma2/skin_user.xml')
                    
            if user_skin != '':
                if section_parameters != '': section_parameters = "  <parameters>\n" + section_parameters + "\n  </parameters>\n"
                if section_screens != '': section_screens = "  <screens>\n" + section_screens + "\n  </screens>\n"
                if section_menus != '': section_menus = "  <menus>\n" + section_menus + "\n  </menus>\n"
                user_skin = "<skin><!--UserSkin-->\n" + section_parameters + section_screens + section_menus + user_skin + "</skin>\n"
                with open (user_skin_file, "w") as myFile:
                    printDEBUG("update_user_skin.self.myUserSkin_active.value write myFile")
                    myFile.write(user_skin)
                    myFile.flush()
                    myFile.close()
                    
                    if (isImageType('vti') == True or isImageType('openatv') == True) and \
                          (self.LCD_widgets_selected == False or self.LCDLinuxEnabled == True): #VTI i openATV czytaja, to nie musimy robic pliku
                        #VTI/openatv standardowo laduja pliki z SkinPath + 'mySkin/skin_user' + self.currentSkin + '.xml'
                        printDEBUG("Tryb bezplikowy VTI, ATV")
                        if path.exists(resolveFilename(SCOPE_CONFIG, 'skin_user' + self.currentSkin + '.xml')):
                            remove(resolveFilename(SCOPE_CONFIG, 'skin_user' + self.currentSkin + '.xml'))
                    elif (isImageType('vti') == True and self.LCD_widgets_selected) or \
                          isImageType('blackhole') == True or isImageType('vuplus') == True: #BlackHole,vuplus korzystają jedynie ze standardowego mechanizmu
                        printDEBUG("Tryb pliku skin_user.xml")
                        #system('ln -sf %s /etc/enigma2/skin_user.xml' % user_skin_file)
                        system('mv -f %s /etc/enigma2/skin_user.xml' % user_skin_file)
                        self.LCDLinuxEnabled == False
                    else: # inne oparte o pli obsluguja skorki spersonalizowane dla kazdej wybranej osobno
                        printDEBUG("Tryb pliku skin_user<nazwa_skorki>.xml")
                        #system('ln -sf %s %s' % (user_skin_file, resolveFilename(SCOPE_CONFIG, 'skin_user' + self.currentSkin + '.xml')))
                        printDEBUG('moving %s to %s' % (user_skin_file, resolveFilename(SCOPE_CONFIG, 'skin_user' + self.currentSkin + '.xml')))
                        system('mv -f %s %s' % (user_skin_file, resolveFilename(SCOPE_CONFIG, 'skin_user' + self.currentSkin + '.xml')))
              
            clearCache()
            if os.path.islink('/usr/share/enigma2/skin_display.xml'):
                os.system('rm -f /usr/share/enigma2/skin_display.xml' )
            if os.path.islink('/usr/share/enigma2/skin_box.xml'):
                os.system('rm -f /usr/share/enigma2/skin_box.xml' )
            if os.path.isfile('/usr/share/enigma2/skin_LCD_UserSkin.xml'):
                os.system('rm -f /usr/share/enigma2/skin_LCD_UserSkin.xml' )
            if config.plugins.UserSkin.LCDmode.value in ("HomarLCDskinsFromOPKG"):
                os.system('opkg update;opkg install enigma2-plugin-skins--j00zeks-homar;sync')
            
            if config.plugins.UserSkin.LCDmode.value not in ('LCDLinux',"system", "HomarLCDskinsFromOPKG"):
            ##### VTI style #####
                if self.LCDconfigKey == 'primary_vfdskin':
                    if os.path.exists(config.plugins.UserSkin.LCDcolors.value):
                        if DBG: printDEBUG("primary_vfdskin (VTI) with colors mode")
                        self.generateLCDskin('/usr/share/enigma2/%s' % config.plugins.UserSkin.LCDmode.value , '/usr/share/enigma2/skin_LCD_UserSkin.xml')
                        config.skin.primary_vfdskin.value = 'skin_LCD_UserSkin.xml'
                    else:
                        config.skin.primary_vfdskin.value = config.plugins.UserSkin.LCDmode.value
                    config.skin.primary_vfdskin.save()
                    configfile.save()
                    printDEBUG("Set config.skin.primary_vfdskin.value='%s'" % config.skin.primary_vfdskin.value)
            ##### openATV style #####
                elif self.LCDconfigKey == 'display_skin':
                    config.skin.display_skin.value = "skin_LCD_UserSkin.xml"
                    config.skin.display_skin.save()
                    configfile.save()
                    printDEBUG("Set config.skin.display_skin.value='%s'" % config.skin.display_skin.value)
                    self.generateLCDskin('/usr/share/enigma2/%s' % config.plugins.UserSkin.LCDmode.value , '/usr/share/enigma2/display/%s' % config.skin.display_skin.value)
            ##### PLi style using skin_display.xml #####
                elif self.LCDconfigKey == 'skin_display.xml': #openPLi style
                    if not os.path.isfile('/usr/share/enigma2/skin_display.xml.org') and os.path.isfile('/usr/share/enigma2/skin_display.xml'):
                        os.system('cp -f /usr/share/enigma2/skin_display.xml /usr/share/enigma2/skin_display.xml.org')
                    self.generateLCDskin('/usr/share/enigma2/%s' % config.plugins.UserSkin.LCDmode.value , '/usr/share/enigma2/skin_LCD_UserSkin.xml')
                    os.system('ln -sf /usr/share/enigma2/skin_LCD_UserSkin.xml /usr/share/enigma2/skin_display.xml' )
                    printDEBUG('linking /usr/share/enigma2/%s to /usr/share/enigma2/skin_display.xml' % (config.plugins.UserSkin.LCDmode.value))
            ##### PLi style using skin_box.xml #####
                elif self.LCDconfigKey == 'skin_box.xml': #openPLi 2nd style
                    self.generateLCDskin('/usr/share/enigma2/%s' % config.plugins.UserSkin.LCDmode.value , '/usr/share/enigma2/skin_LCD_UserSkin.xml')
                    os.system('ln -sf /usr/share/enigma2/skin_LCD_UserSkin.xml /usr/share/enigma2/skin_box.xml' )
                    printDEBUG('linking /usr/share/enigma2/%s to /usr/share/enigma2/skin_box.xml' % (config.plugins.UserSkin.LCDmode.value))
            ##### obejscia LCDLINUX #####
            elif self.LCDLinuxEnabled == True and os.path.isfile('/etc/enigma2/skin_user.xml') and self.LCDconfigKey == 'skin_display.xml': #openPLi style:
                os.system('ln -sf /etc/enigma2/skin_user.xml /usr/share/enigma2/skin_display.xml' )
            elif self.LCDLinuxEnabled == True and os.path.isfile('/etc/enigma2/skin_user.xml') and self.LCDconfigKey == 'skin_box.xml': #openPLi 2nd style:
                os.system('ln -sf /etc/enigma2/skin_user.xml /usr/share/enigma2/skin_box.xml' )
              
            ##### ALL disabled #####
            else:
                if os.path.isfile('/usr/share/enigma2/skin_display.xml.org'):
                    os.system('cp -f /usr/share/enigma2/skin_display.xml.org /usr/share/enigma2/skin_display.xml')
                
            #checking if all scripts are in the system
            if FullDBG: printDEBUG("########################### Final User Skin\n%s\n##############################################\n" % user_skin)
            self.checkComponent(user_skin, 'render' , '/usr/lib/enigma2/python/Components/Renderer/' )
            self.checkComponent(user_skin, 'convert type' , '/usr/lib/enigma2/python/Components/Converter/' )
            self.checkComponent(user_skin, 'pixmap' , resolveFilename(SCOPE_SKIN, '') )
            self.checkFontColor(user_skin)

    def generateLCDskin(self, inFile, outFile): #ATV/PLi does not work when id="1" in display skin.
        colors2append = ''
        colorsMarker = False
        colorsEndMarker = False
        if os.path.exists(config.plugins.UserSkin.LCDcolors.value):
           #sprawdzenie czy jest definicja kolorow
           with open(inFile, 'r') as fr:
              while True:
                  fline = fr.readline()
                  if not fline:
                      break
                  if '<colors>' in fline:
                      colorsMarker = True
                  elif colorsMarker and '</colors>' in fline:
                      colorsEndMarker = True
                      break
              fr.close()
           if colorsEndMarker:
              with open(config.plugins.UserSkin.LCDcolors.value, 'r') as fr:
                  while True:
                      fline = fr.readline()
                      if not fline:
                          break
                      if '<color name=' in fline:
                          colors2append += fline
                  fr.close()
               
        with open(inFile, 'r') as fr:
            fw = open(outFile , 'w')
            #first line can contain something which has to be first ;)
            fline = fr.readline()
            if fline:
                if '<?xml' in fline:
                    fw.write(fline)
                    fw.write("<!-- Transformed by UserSkin from file='%s' -->\n" % config.plugins.UserSkin.LCDmode.value )
                else:
                    fw.write("<!-- Transformed by UserSkin from file='%s' -->\n" % config.plugins.UserSkin.LCDmode.value )
                    fw.write(fline)
                while True:
                    fline = fr.readline()
                    if not fline:
                        break
                    if colorsMarker and '</colors>' in fline:
                        fline = colors2append + fline
                    elif not isImageType('vti'):
                        if 'screen name=' in fline:
                            fline = fline.replace('id="1"','')
                        if 'name="vti' in fline.lower(): #ATV has some strange workarrounds for VTI
                            fline = fline.replace('name="','name="fake')
                    fw.write(fline)
            fr.close()
            fw.close()
    
    def checkFontColor(self, myContent):
        def updateLackOfColor(name, mySeparator =', '):
            printDEBUG("Missing color definitions found:%s\n" % name)
            if self.LackOfFile == '':
                self.LackOfFile = name
            else:
                self.LackOfFile += mySeparator + name
        #preparing list of available colors
        DefinedColors=[]
        with open(SkinPath + 'skin.xml', 'r') as f:
            for line in f:
                if re.search('.*<color name="([\S]*)"',line) is not None:
                    DefinedColors.append(re.search('.*<color name="([\S]*)"',line).group(1))
            f.close()
        if len(DefinedColors) < 1:
            return
        #remove not real colors
        myContent = myContent.replace('CoolDateColor=','').replace('CoolHighlightColor','').replace('CoolTitleColor','')
        #checking, if all colors defined
        r=re.findall(r'.*[Cc]olor="([^\W#]*)"',myContent)
        r=list(set(r)) #remove duplicates, no need to check for the same component several times
        
        if r:
            printDEBUG("Found %d color definitions" % len(r))
            for myColor in set(r):
                if myColor not in DefinedColors:
                    updateLackOfColor(myColor)

    def checkComponent(self, myContent, look4Component , myPath): #look4Component=render|
        def updateLackOfFile(name, mySeparator =', '):
            printDEBUG("\tMissing component found:%s\n" % name)
            if self.LackOfFile == '':
                self.LackOfFile = name
            else:
                self.LackOfFile += mySeparator + name
            
        #2 test:
        #with open('/tmp/UserSkin.log') as f: myContent="".join(f.readlines())
        #look4Component='render'
        r=re.findall( r'[ <]%s="([a-zA-Z0-9_/\.]+)"[ >]' % look4Component , myContent )
        r=list(set(r)) #remove duplicates, no need to check for the same component several times

        printDEBUG("Found %d definitions of %s:\n" % (len(r),look4Component))
        if r:
            for myComponent in set(r):
                if FullDBG: printDEBUG(" [UserSkin] checks if %s exists" % myComponent)
                if look4Component == 'pixmap':
                    if FullDBG: printDEBUG("%s\n%s\n" % (myComponent,myPath + myComponent))
                    if myComponent.startswith('/'):
                        if not path.exists(myComponent):
                            updateLackOfFile(myComponent, '\n')
                    else:
                        if not path.exists(myPath + myComponent):
                            updateLackOfFile(myComponent)
                else:
                    if not path.exists(myPath + myComponent + ".pyo") and not path.exists(myPath + myComponent + ".pyc") and not path.exists(myPath + myComponent + ".py"):
                        updateLackOfFile(myComponent)
        return
    
    def readXMLfile(self, XMLfilename, XMLsection): #sections:ALLSECTIONS|fonts|
        myPath=path.realpath(XMLfilename)
        if not path.exists(myPath):
            remove(XMLfilename)
            return ''
        filecontent = ''
        if XMLsection == 'ALLSECTIONS':
            sectionmarker = True
        else:
            sectionmarker = False
        with open (XMLfilename, "r") as myFile:
            lineNo = 0
            for line in myFile:
                lineNo += 1
                if line.find('<skin>') != -1 or line.find('</skin>') != -1:
                    continue
                if line.find('<%s' % XMLsection) != -1 and sectionmarker == False:
                    if DBG == True: printDEBUG('<%s marker found at %s' % (XMLsection, lineNo))
                    sectionmarker = True
                if line.find('</%s>' %XMLsection) != -1 and sectionmarker == True:
                    if DBG == True: printDEBUG('</%s> marker found at %s' % (XMLsection, lineNo))
                    sectionmarker = False
                    filecontent = filecontent + line
                if sectionmarker == True:
                    filecontent = filecontent + line
            myFile.close()
        return filecontent

#################################################################################################################
class TreeUserSkinScreens(Screen):
    skin = """
  <screen position="0,0" size="1280,720" title="UserSkin Setup" backgroundColor="transparent" flags="wfNoBorder">
    <eLabel position="0,0" size="1280,720" zPosition="-15" backgroundColor="#20000000" />
    <eLabel position=" 55,100" size="725,515" zPosition="-10" backgroundColor="#20606060" />
    <eLabel position="785,295" size="445,320" zPosition="-10" backgroundColor="#20606060" />
    <eLabel position="785,100" size="135,190" zPosition="-10" backgroundColor="#20606060" />
    <eLabel position="925,100" size="305,190" zPosition="-10" backgroundColor="#20606060" />
    <eLabel position=" 55,620" size="290,55" zPosition="-10" backgroundColor="#20b81c46" />
    <eLabel position="350,620" size="290,55" zPosition="-10" backgroundColor="#20009f3c" />
    <eLabel position="645,620" size="290,55" zPosition="-10" backgroundColor="#209ca81b" />
    <eLabel position="940,620" size="290,55" zPosition="-10" backgroundColor="#202673ec" />
    <eLabel position=" 55,675" size="290, 5" zPosition="-10" backgroundColor="#20b81c46" />
    <eLabel position="350,675" size="290, 5" zPosition="-10" backgroundColor="#20009f3c" />
    <eLabel position="645,675" size="290, 5" zPosition="-10" backgroundColor="#209ca81b" />
    <eLabel position="940,675" size="290, 5" zPosition="-10" backgroundColor="#202673ec" />
    <!--widget source="session.VideoPicture" render="Pig" position="935,115" zPosition="3" size="284,160" backgroundColor="#ff000000">
    </widget-->
    <widget source="Title" render="Label" position="70,47" size="950,43" font="Regular;35" foregroundColor="#00ffffff" backgroundColor="#004e4e4e" transparent="1" />
    <widget name="filelist" position="70,115" size="700,480" zPosition="1" font="Regular;20" transparent="1" scrollbarMode="showOnDemand"/>
    <widget name="PreviewPicture" position="808,342" size="400,225" alphatest="on" />
    <widget name="PreviewInfo" position="808,575" size="400,225" font="Regular;25" foregroundColor="#00ffeedd" backgroundColor="#004e4e4e" transparent="1" />
    <widget source="key_red" render="Label" position="70,635" size="260,25" zPosition="1" font="Regular;20" halign="left" foregroundColor="#00ffffff" backgroundColor="#20b81c46" transparent="1" />
    <widget source="key_green" render="Label" position="365,635" size="260,25" zPosition="1" font="Regular;20" halign="left" foregroundColor="#00ffffff" backgroundColor="#20009f3c" transparent="1" />
    <widget source="key_yellow" render="Label" position="650,635" size="260,25" zPosition="1" font="Regular;20" halign="left" foregroundColor="#00ffffff" transparent="1" />
    <widget source="key_blue" render="Label" position="954,635" size="260,25" zPosition="1" font="Regular;20" halign="left" foregroundColor="#00ffffff" backgroundColor="#202673ec" transparent="1" />
  </screen>
"""
    EditScreen = False
    DeleteScreen = False
    
    def __init__(self, session):
        Screen.__init__(self, session)
        self.session = session
        
        myTitle=_("UserSkin %s - additional screens") %  UserSkinInfo
        self.setTitle(myTitle)
        try:
            self["title"] = StaticText(myTitle)
        except Exception:
            pass
        
        self["key_red"] = StaticText(_("Exit"))
        self["key_green"] = StaticText("")
        self["key_yellow"] = StaticText(_("Refresh"))
        self["key_blue"] = StaticText(_("Preview"))
        
        self["PreviewPicture"] = Pixmap()
        self["PreviewInfo"] = StaticText("")
        
        self.LastFolderSelected = None
        
        self["shortcuts"] = ActionMap(["TreeUserSkinActions"],
        {
            "runMenuEntry": self.runMenuEntry,
            "cancel": self.keyCancel,
            "green": self.keyGreen,
            "yellow": self.keyYellow,
            "blue": self.keyBlue,
            "lineUp": self.lineUp,
            "lineDown": self.lineDown,
            "pageUp": self.pageUp,
            "pageDown": self.pageDown,
        }, -2)
        
        self.currentSkin = CurrentSkinName
        #self.screen_dir = "allScreens"
        self.allScreens_dir = SkinPath + "allScreens/"
        self.allPreviews_dir = SkinPath + "allPreviews/"
        self.UserSkin_Selections_dir = SkinPath + "UserSkin_Selections/"
        if path.exists("%sUserSkinpics/install.png" % SkinPath):
            if DBG == True: printDEBUG("SkinConfig is loading %sUserSkinpics/install.png" % SkinPath)
            self.enabled_pic = LoadPixmap(cached=True, path="%sUserSkinpics/install.png" % SkinPath)
        else:
            self.enabled_pic = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/UserSkin/pic/install.png"))
        #check if we have preview files
        isPreview=0
        for xpreview in listdir(self.allPreviews_dir):
            if len(xpreview) > 4 and  xpreview[-4:] == ".png":
                isPreview += 1
            if isPreview >= 2:
                break
        if path.exists("%sUserSkinpics/install.png" % SkinPath):
            if DBG == True: printDEBUG("SkinConfig is loading %sUserSkinpics/remove.png" % SkinPath)
            self.disabled_pic = LoadPixmap(cached=True, path="%sUserSkinpics/remove.png" % SkinPath)
        else:
            self.disabled_pic = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/UserSkin/pic/remove.png"))
        
        self.filelist = FileList(self.allScreens_dir)
        self["filelist"] = self.filelist

        self.onLayoutFinish.append(self.__onLayoutFinish)
        self.PreviewTimer = eTimer()
        self.PreviewTimer.callback.append(self.PreviewTimerCB)
        self.PreviewsURL = None
        self.PreviewAnims = None
        self.PreviewAnimsDelay = 100
        self.PreviewAnimCurrent = 0
        self.shownPreview = None
        if pathExists("%s%s" % (SkinPath,'skin.config')):
            with open("%s%s" % (SkinPath,'skin.config'), 'r') as cf:
                for cfg in cf:
                    if cfg.startswith("allPreviews="):
                        self.PreviewsURL = cfg.split('=')[1].strip().replace("'","")
                        break
                    elif cfg.startswith("#allPreviews="):
                        break

    def endrun(self):
        return
     
    def PreviewTimerCB(self):
        def UpdatePreviewPicture(PreviewFileName):
            printDEBUG("[skinconfig:PreviewTimerCB:] UpdatePreviewPicture('%s')" % PreviewFileName )
            if isImageType('vuplus') == False: self["PreviewPicture"].instance.setScale(1)
            self["PreviewPicture"].instance.setPixmap(LoadPixmap(path=PreviewFileName))
            self["PreviewPicture"].show()
            self.shownPreview = PreviewFileName

        def webPreview(response = None):
            if not self.PreviewAnimsDelay is None:
                printDEBUG("[skinconfig:PreviewTimerCB] downloaded '%s%s.jpg'" % (self.PreviewsURL, self.PreviewAnims[self.PreviewAnimCurrent]) )
                UpdatePreviewPicture(self.PreviewAnims[self.PreviewAnimCurrent])
                self.PreviewTimer.start(self.PreviewAnimsDelay,False)
            else:
                printDEBUG("[skinconfig:PreviewTimerCB] downloaded '%s%s.jpg'" % (self.PreviewsURL, pic) )
                UpdatePreviewPicture('/tmp/preview.jpg')
        
        def getPIC(picName):
            #printDEBUG("[skinconfig:PreviewTimerCB] getPIC('%s')" % picName )
            if path.exists('/tmp/preview.jpg'):
                remove('/tmp/preview.jpg')
            if not self.PreviewAnims is None:
                self.PreviewAnims[self.PreviewAnimCurrent] = '/tmp/preview-%s.jpg' % self.PreviewAnimCurrent
                retStatus = downloadPage( picName , '/tmp/preview-%s.jpg' % self.PreviewAnimCurrent)
            else:
                picName = picName.replace(' ','%20')
                retStatus = downloadPage( picName , '/tmp/preview.jpg')
            if retStatus:
                webPreview()
            else:
                self["PreviewPicture"].hide()
            
        self.PreviewTimer.stop()
        self.shownPreview = None

        if self["filelist"].getSelection()[1] == True: # isDir
            self["PreviewPicture"].hide()
            return

        pic =  self.filelist.getFilename()[:-4]
        #info when exists
        myInfoFile=SkinPath + "allInfos/" + pic + ".txt"
        if not path.exists(myInfoFile):
            myInfoFile="/usr/share/enigma2/HomarLCDskins/allInfos/" + pic + ".txt"
        printDEBUG("[skinconfig:PreviewTimerCB] myInfoFile='BH|HMR folder/%s.txt'" % pic )
        self["PreviewInfo"].setText(processInfo(myInfoFile))
        #picture
        if not self.PreviewAnims is None:
            self.PreviewAnimCurrent += 1
            if self.PreviewAnimCurrent >= len(self.PreviewAnims):
                self.PreviewAnimCurrent = 0
            if self.PreviewAnims[self.PreviewAnimCurrent].startswith('/tmp/preview'):
                webPreview()
            else:
                getPIC('%s%s.jpg' % (self.PreviewsURL, self.PreviewAnims[self.PreviewAnimCurrent]))
        elif path.exists(self.allPreviews_dir + "preview_" + pic + '.anim'):
            for line in open(self.allPreviews_dir + "preview_" + pic + '.anim', 'r'):
                line = line.strip()
                if self.PreviewAnimsDelay is None: #delay has to be always in first line!!!!
                    try:
                        self.PreviewAnimsDelay = int(line)
                    except Exception as e:
                        printDEBUG("[skinconfig:PreviewTimerCB] self.PreviewAnimsDelay exception: %s" % str(e) )
                        self.PreviewAnimsDelay = 100
                else:
                    if self.PreviewAnims is None:
                        self.PreviewAnims = []
                    self.PreviewAnims.append(line)
            getPIC('%s%s.jpg' % (self.PreviewsURL, self.PreviewAnims[self.PreviewAnimCurrent]))
        elif path.exists(self.allPreviews_dir + "preview_" + pic + '.png'):
            UpdatePreviewPicture(self.allPreviews_dir + "preview_" + pic + '.png')
        elif path.exists(self.allPreviews_dir + "preview_" + pic + '.jpg'):
            UpdatePreviewPicture(self.allPreviews_dir + "preview_" + pic + '.jpg')
        elif path.exists(self.allPreviews_dir + pic + '.png'):
            UpdatePreviewPicture(self.allPreviews_dir + pic + '.png')
        elif path.exists(self.allPreviews_dir + pic + '.jpg'):
            UpdatePreviewPicture(self.allPreviews_dir + pic + '.jpg')
        else:
            if path.exists('/tmp/preview.jpg'):
                remove('/tmp/preview.jpg')
            if self.PreviewsURL is not None:
                getPIC('%s%s.jpg' % (self.PreviewsURL, pic))
            else:
                printDEBUG("[skinconfig:PreviewTimerCB] '%s.jpg' not found" % pic )
                self["PreviewPicture"].hide()
    
    def installComponentsFromOPKG(self, ret = False):
        if DBG == True: printDEBUG("installComponentsFromOPKG >>>")
        if ret == True:
            if 'Ciacho' in self["filelist"].getSelection()[0]:
                pkgName = 'e2-j00zeks-bh-addon-userspacks-screensbyciacho'
            os.system('opkg update;opkg install %s;sync' % pkgName)
            self.keyOk()

    def runMenuEntry(self):
        selection = self["filelist"].getSelection()
        if selection is None:
            return
        elif selection[1] == True: # isDir
            printDEBUG("SkinConfig.TreeUserSkinScreens.runMenuEntry() selection = %s" % str(selection))
            if self.filelist.getCurrentDirectory() is not None and \
                  len(selection[0]) > len(self.filelist.getCurrentDirectory()) or self.LastFolderSelected == None:
                self.LastFolderSelected = selection[0]
                self["filelist"].changeDir(selection[0], "FakeFolderName")
            else:
                printDEBUG("Folder Down")
                self["filelist"].changeDir(selection[0], self.LastFolderSelected)
            return
        else: #file selected
            d = self.filelist.getCurrentDirectory()
            if d is None:
                d=""
            elif not d.endswith('/'):
                d +='/'
            f = self.filelist.getFilename()
            printDEBUG("self.selectFile>> " + d + f)
            if path.exists(self.UserSkin_Selections_dir + f):
                remove(self.UserSkin_Selections_dir + f)
            else:
                try:
                    symlink(d + f, self.UserSkin_Selections_dir + f)
                except Exception:
                    system('ln -sf %s %s' %(d + f,self.UserSkin_Selections_dir + f))
            self.__refreshList()

    def keyGreen(self):
        if self.EditScreen == True:
            from Plugins.Extensions.UserSkin.editscreens import UserSkinEditScreens
            self.session.openWithCallback(self.__refreshList,UserSkinEditScreens, ScreenFile = self.filelist.getCurrentDirectory() + "/" + self.filelist.getFilename())
        else:
            print("Nothing to Edit :(")
            
    def keyYellow(self):
        def keyYellowRet(result):
            if result is None or result is False:
                printDEBUG("Deletion cancelled.")
            else:
                remove(self.filelist.getCurrentDirectory() + "/" + self.filelist.getFilename())
                pic = self.filelist.getFilename().replace(".xml", ".png")
                if path.exists(SkinPath + "allPreviews/preview_" + pic):
                    remove(SkinPath + "allPreviews/preview_" + pic)
                self.__refreshList()

        if self.DeleteScreen == True:
            self.session.openWithCallback(keyYellowRet, MessageBox, _("Are you sure you want delete the screen?"), MessageBox.TYPE_YESNO, default = False)
        elif self.EditScreen == False:
            try:
                self.__refreshList()
                self["filelist"].moveToIndex(0)
                printDEBUG("Files list refreshed for: %s" % self["filelist"].getCurrentDirectory() )
            except Exception as e:
                printDEBUG("Exception refreshing files list: %s " % str(e))
            
        else:
            print("Nothing to Delete ;)")
            
    def keyCancel(self):
        for f in listdir("/tmp"):
            if f.startswith('preview') and f.endswith('.jpg'):
                remove('/tmp/%s' % f)
        self.close()
####################### FOR NEW TREE SELECTOR ###################################
    def __onLayoutFinish(self):
        self["filelist"].changeDir(self.allScreens_dir)
        self["filelist"].refresh()

    def __refreshList(self):
        self["filelist"].refresh()
       
    def pageUp(self):
        if self["filelist"].getSelectedIndex() == 0:
            self["filelist"].moveToIndex(len(self["filelist"].getFileList())-1)
        else:
            self["filelist"].pageUp()
        self.setInfo()

    def pageDown(self):
        if self["filelist"].getSelectedIndex() == (len(self["filelist"].getFileList())-1):
            self["filelist"].moveToIndex(0)
        else:
            self["filelist"].pageDown()
        self.setInfo()

    def lineUp(self):
        if self["filelist"].getSelectedIndex() == 0:
            self["filelist"].moveToIndex(len(self["filelist"].getFileList())-1)
        else:
            self["filelist"].up()
        self.setInfo()

    def lineDown(self):
        if self["filelist"].getSelectedIndex() == (len(self["filelist"].getFileList())-1):
            self["filelist"].moveToIndex(0)
        else:
            self["filelist"].down()
        self.setInfo()
        
    def setInfo(self):
        self.PreviewTimer.stop()
        self.PreviewAnims = None
        self.PreviewAnimsDelay = None
        self.PreviewAnimCurrent = 0
        
        selection = self["filelist"].getSelection()
        if selection is None:
            return
        elif selection[1] == True: # isDir
            self["key_green"].setText("")
            self.EditScreen = False
            self["key_yellow"].setText(_("Refresh"))
            self.DeleteScreen = False
            self["PreviewPicture"].hide()
        else:
            self["key_green"].setText(_("Edit"))
            self.EditScreen = True
            if path.exists(self.UserSkin_Selections_dir + self.filelist.getFilename()):
                self["key_yellow"].setText("")
                self.DeleteScreen = False
            else:
                self["key_yellow"].setText(_("Delete"))
                self.DeleteScreen = True

            self.PreviewTimer.start(100,False)
            
    def __getCurrentDir(self):
        d = self.filelist.getCurrentDirectory()
        if d is None:
            d=""
        elif not d.endswith('/'):
            d +='/'
        return d
          
    def doNothing(self, ret = None):
        return

    def keyBlue(self):
        printDEBUG("[skinconfig:keyBlue] >>> ")
        previewSkin = ""
        previewSnip = ""
        selection = self["filelist"].getSelection()
        if selection is None or selection[1] == True: # isDir
            return
        selectedXML = os.path.join(self.filelist.getCurrentDirectory(), self.filelist.getFilename())
        printDEBUG("[skinconfig:keyBlue] selectedXML= %s" % selectedXML)
        if path.exists(selectedXML):
            printDEBUG("[skinconfig:keyBlue] selectedXML exists")
            import xml.etree.cElementTree as ET
            root = ET.parse(selectedXML)
            if root.getroot().tag == 'screen' and root.getroot().attrib['name'] in ('InfoBar','SecondInfoBar'):
                previewSkin = open(selectedXML, "r").read().replace('name="%s"' % root.getroot().attrib['name'],'name="UserSkinPreviewSkin"')
            else:
                try:
                    for myScreen in root.findall('screen'):
                        printDEBUG("[skinconfig:keyBlue] myScreen= %s" % myScreen.attrib['name'])
                        if myScreen.attrib['name'] in ('InfoBar','SecondInfoBar'):
                            printDEBUG("[skinconfig:keyBlue] reading %s as UserSkinPreviewSkin" % myScreen.attrib['name'])
                            previewSkin = open(selectedXML, "r").read().replace('name="%s"' % myScreen.attrib['name'],'name="UserSkinPreviewSkin"')
                            break
                except Exception as e:
                    printDEBUG("[skinconfig:keyBlue] Exception: %s" % str(e))

            if not self.shownPreview is None:
                previewSnip = """
<screen name="UserSkinPreviewSkin" backgroundColor="transparent" flags="wfNoBorder" position="0,0" size="1920,1080">
  <widget source="global.CurrentTime" render="j00zekPixmap" pixmap="%s" position="0,0" size="1920,1080" alphatest="blend"/>
</screen>""" % self.shownPreview

            if previewSkin == "":
                if previewSnip != "":
                    self.session.openWithCallback(self.doNothing, UserSkinPreviewSkin, previewSnip, selectedXML)
            else:
                try:
                    self.session.openWithCallback(self.doNothing, UserSkinPreviewSkin, previewSkin, selectedXML)
                except Exception as e:
                    printDEBUG("[skinconfig:keyBlue] Exception displaying live screen: %s" % str(e))
                    if previewSnip != "":
                        self.session.openWithCallback(self.doNothing, UserSkinPreviewSkin, previewSnip, selectedXML)

################################################################################################################################################################
class UserSkinPreviewSkin(Screen):
    def __init__(self, session, previewSkin, selectedXML):
        printDEBUG("[skinconfig:UserSkinPreviewSkin:__init__] >>> ")
        if FullDBG: printDEBUG("[skinconfig:keyBlue] previewSkin= %s" % previewSkin)
        self.skin = previewSkin.replace("<skin>","").replace("</skin>","")
        self.grabFile = "/tmp/%s.jpg" % path.basename(selectedXML)[:-4]
        self.session = session
        Screen.__init__(self, session)

        self["actions"]  = ActionMap(["UserSkinPreviewSkinActions"], {
            "keyCancel": self.close,
            "keyOK": self.close,
            "doGrab": self.doGrab,
            }, -1)
    def doGrab(self):
        system('grab -dj 85 %s' % self.grabFile )
