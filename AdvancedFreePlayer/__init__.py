# -*- coding: utf-8 -*-
from __future__ import absolute_import #zmiana strategii ladowanie modulow w py2 z relative na absolute jak w py3
try:
    from version import Version
except Exception:
    from .version import Version
PluginInfo='@j00zek %s' % Version

#permanent
PluginName = 'AdvancedFreePlayer'
PluginGroup = 'Extensions'

#Plugin Paths
from Tools.Directories import resolveFilename, SCOPE_CURRENT_SKIN, SCOPE_PLUGINS
PluginFolder = PluginName
PluginPath = resolveFilename(SCOPE_PLUGINS, '%s/%s/' %(PluginGroup,PluginFolder))
ExtPluginsPath = resolveFilename(SCOPE_PLUGINS, '%s/' %(PluginGroup))

#Current skin
from Components.config import *
SkinPath = resolveFilename(SCOPE_CURRENT_SKIN, '')
if not SkinPath.endswith('/'):
    SkinPath = SkinPath + '/'
CurrentSkinName=config.skin.primary_skin.value.replace('skin.xml', '').replace('/', '')

#translation
PluginLanguageDomain = "plugin-" + PluginName
PluginLanguagePath = resolveFilename(SCOPE_PLUGINS, '%s/%s/locale' % (PluginGroup,PluginFolder))

#DEBUG
from datetime import datetime
myDEBUG=False
myDEBUGfile = '/tmp/%s.log' % PluginName

append2file=False
def printDEBUG( myText , myFUNC = ''):
    if myFUNC != '':
        myFUNC = ':' + myFUNC
    global append2file
    if myDEBUG:
        print(("[%s:%s] %s" % (PluginName, myFUNC, myText)))
        try:
            if append2file == False:
                append2file = True
                f = open(myDEBUGfile, 'w')
            else:
                f = open(myDEBUGfile, 'a')
            f.write('%s [%s] %s\n' %(str(datetime.now()), myFUNC, myText))
            f.close
        except Exception:
            pass

printDBG=printDEBUG

def ClearMemory(): #avoid GS running os.* (e.g. os.system) on tuners with small RAM
    with open("/proc/sys/vm/drop_caches", "w") as f: f.write("1\n")
    
from os import path as os_path
def getPlatform():
    if os_path.exists("/usr/lib/enigma2/python/Plugins/SystemPlugins/ServiceApp/serviceapp.so"):
        return 'ServiceApp'
    fc=''
    with open('/proc/cpuinfo', 'r') as f:
        fc=f.read()
        f.close()
    if fc.find('sh4') > -1:
        return 'sh4'
    elif fc.find('BMIPS') > -1:
        return 'mipsel'
    elif fc.find('GenuineIntel') > -1:
        return 'i686'
    elif fc.find('ARMv') > -1:
        return 'arm'
    else:
       return 'unknown'
     
def getChoicesList():
    return choicesList
    
def isINETworking():
    try:
        import socket
        socket.setdefaulttimeout(0.5)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(('8.8.8.8', 53))#connection with google dns service
        return True
    except Exception as e:
        printDEBUG("%s" % str(e))
    try:
        import socket
        socket.setdefaulttimeout(0.5)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(('8.8.4.4', 53))#connection with google dns2 service
        return True
    except Exception as e:
        printDEBUG("%s" % str(e))
    printDEBUG("Error no internet connection. > %s" % str(e))
    return False

##################################################### LOAD SKIN DEFINITION #####################################################
def LoadSkin(SkinName):
    printDEBUG("LoadSkin >>> %s" % SkinName)
    from enigma import getDesktop
    model=''
    if os_path.exists("/proc/stb/info/vumodel"):
        with open("/proc/stb/info/vumodel", "r") as f:
            model=f.read().strip()
            f.close()
    elif os_path.exists("/proc/stb/info/model"):
        with open("/proc/stb/info/model", "r") as f:
            model=f.read().strip()
            f.close()
    
    if SkinName.endswith('.xml'):
        SkinName=SkinName[:-4]
    skinDef=None
    
    if getDesktop(0).size().width() == 1920 and os_path.exists("%sskins/%s%sFHD.xml" % (PluginPath,SkinName,model)):
        with open("%sskins/%s%sFHD.xml" % (PluginPath,SkinName,model),'r') as skinfile:
            skinDef=skinfile.read()
            skinfile.close()
    elif getDesktop(0).size().width() == 1920 and os_path.exists("%sskins/%sFHD.xml" % (PluginPath,SkinName)):
        with open("%sskins/%sFHD.xml" % (PluginPath,SkinName),'r') as skinfile:
            skinDef=skinfile.read()
            skinfile.close()
            
    elif os_path.exists("%sskins/%s%s.xml" % (PluginPath,SkinName,model)):
        with open("%sskins/%s%s.xml" % (PluginPath,SkinName,model),'r') as skinfile:
            skinDef=skinfile.read()
            skinfile.close()
    elif os_path.exists("%sskins/%s.xml" % (PluginPath,SkinName)):
        with open("%sskins/%s.xml" % (PluginPath,SkinName),'r') as skinfile:
            skinDef=skinfile.read()
            skinfile.close()
    else:
        printDEBUG("%s does not exists" % SkinName)
    return skinDef

##################################################### TĹUMACZENIA #####################################################
#printDEBUG("LanguageGOS not detected")
from Components.Language import language
import gettext
from os import environ
    
def localeInit():
    lang = language.getLanguage()[:2]
    environ["LANGUAGE"] = lang
    gettext.bindtextdomain(PluginLanguageDomain, PluginLanguagePath)

def translate(txt):
    t = gettext.dgettext(PluginLanguageDomain, txt)
    if t == txt:
            t = gettext.gettext(txt)
            #print("Lack of translation for '%s'" % t)
    return t

localeInit()
language.addCallback(localeInit)
_ = translate
##################################################### CONFIGs #####################################################
config.plugins.AdvancedFreePlayer = ConfigSubsection()
myConfig = config.plugins.AdvancedFreePlayer
myConfig.FileListFontSize = ConfigSelectionNumber(20, 32, 2, default = 24)
myConfig.TextFilesOnFileList = ConfigYesNo(default = False)
myConfig.NamesNOfiles = ConfigYesNo(default = True) # configures, if file selector should present MovieNames or FileNames
myConfig.FileListSort = ConfigSelection(default = "name", choices = [("name", _("Sort by name")),("dateasc", _("Sort by date ascending")),("datedesc", _("Sort by date descending"))])
myConfig.DirListSort = ConfigSelection(default = "name", choices = [("asfiles", _("Like files")),("name", _("Sort by name")),("dateasc", _("Sort by date ascending")),("datedesc", _("Sort by date descending"))])
if getPlatform() == 'sh4':
    myConfig.MultiFramework = ConfigSelection(default = "4097", choices = [("4097", "gstreamer (root 4097)"),("4099", "ffmpeg (root 4099)"),("1", "hardware (root 1)"), ("select", _("Select during start"))])
    choicesList = [("gstreamer (root 4097)","4097"),("ffmpeg (root 4099)","4099"),("Hardware (root 1)","1")]
elif getPlatform() == 'ServiceApp':
    myConfig.MultiFramework = ConfigSelection(default = "4097", choices = [("4097", "standard gstreamer (root 4097)"),("5001", "ServiceApp gstreamer (root 5001)"), ("5002", "ServiceApp ffmpeg (root 5002)"), ("select", _("Select during start"))])
    choicesList = [("gstreamer (root 4097)","4097"),("ServiceApp gstreamer (root 5001)","5001"), ("ServiceApp ffmpeg (root 5002)","5002"),("Hardware (root 1)","1")]
else:
    myConfig.MultiFramework = ConfigSelection(default = "4097", choices = [("4097", "gstreamer (root 4097)")])
    choicesList = [("gstreamer (root 4097)","4097"),("Hardware (root 1)","1")]
myConfig.StopService = ConfigYesNo(default = True)
myConfig.InfobarTime = ConfigSelectionNumber(2, 9, 1, default = 5)
myConfig.InfobarOnPause = ConfigYesNo(default = True)
myConfig.DeleteFileQuestion = ConfigYesNo(default = True)
myConfig.DeleteWhenPercentagePlayed = ConfigSelectionNumber(0, 100, 5, default = 80)
myConfig.KeyOK = ConfigSelection(default = "play", choices = [("unselect", _("Select/Unselect")),("play", _("Select>Play")),("playmovie", _("Play movie"))])
SRTplayerChoices=[]
SRTplayerChoices.append( ("system", _("System")) )
SRTplayerChoices.append( ("plugin", _("Plugin, local subtitles")) )
if os_path.exists(resolveFilename(SCOPE_PLUGINS, 'Extensions/DMnapi' )):
    SRTplayerChoices.append( ("plugin-dmNapi", _("Plugin, dmNapi support")) )
if os_path.exists(resolveFilename(SCOPE_PLUGINS, 'Extensions/SubsSupport' )):
    SRTplayerChoices.append( ("plugin-SubsSupport", _("Plugin, SubsSupport support")) )

myConfig.SRTplayer = ConfigSelection(default = "system", choices = SRTplayerChoices )
#myConfig.TXTplayer = ConfigSelection(default = "plugin", choices = [("convert", _("System after conversion to srt")),("plugin", _("Plugin"))])
#myConfig.TXTengine = ConfigSelection(default = "dmnampi", choices = [("dmnampi", "dmNapi"),("subssupport", "SubsSupport")])
myConfig.Version = ConfigSelection(default = "public", choices = [("debug", _("every new version (debug)")),("public", _("only checked versions"))])

#
# hidden atributes to store configuration data
#
if os_path.exists("/hdd/movie/"):
    myConfig.FileListLastFolder = ConfigText(default = "/hdd/movie/", fixed_size = False)
else:
    myConfig.FileListLastFolder = ConfigText(default = "/", fixed_size = False)
if not os_path.exists(myConfig.FileListLastFolder.value):
    myConfig.FileListLastFolder.value = '/'
    
myConfig.StoreLastFolder = ConfigYesNo(default = True)
myConfig.Inits = ConfigText(default = "540,60,Regular,0,1,0", fixed_size = False)
#position,size,type,color,visibility,background
myConfig.PlayerOn = NoSave( ConfigYesNo(default = False))

myConfig.DirectoryCoversDescriptons = ConfigYesNo(default = True) # informacja o katalogu z plikow _dir.info i _dir.png

#Downloading covers
myConfig.AutoDownloadCoversDescriptions = ConfigYesNo(default = True)
myConfig.PermanentCoversDescriptons = ConfigYesNo(default = False)

#myConfig.MovieSearchTree = ConfigText(default = "/hdd/movie/", fixed_size = False)

try:
    myConfig.coverfind_language = config.plugins.coverfind.language
except:
    from Components.Language import language
    myConfig.coverfind_language = ConfigSelection(default=language.getLanguage()[:2], choices = ["de", "en", "it", "pl"])
try:
    myConfig.coverfind_themoviedb_coversize = config.plugins.coverfind.themoviedb_coversize
except:
    from Components.Language import language
    myConfig.coverfind_themoviedb_coversize = ConfigSelection(default="w185", choices = ["w92", "w185", "w500", "original"])

myConfig.ShowMusicFiles = ConfigYesNo(default = False)
myConfig.ShowPicturesFiles = ConfigYesNo(default = False)
    
myConfig.MoveToTrash = ConfigYesNo(default = False)
myConfig.TrashFolder = ConfigText(default = "/hdd/movie/trashcan", fixed_size = False)

#session settings, not saved
myConfig.FileNameFilter = NoSave(ConfigText(default = "", fixed_size = False))
myConfig.FileListSelectedItem = NoSave(ConfigText(default = "", fixed_size = False))
#ToDo
myConfig.CacheStreams = ConfigYesNo(default = False)
